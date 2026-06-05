# KernelPilot 中 KernelWiki 、 SDAAKernelWiki 

## 1. KernelWiki 在 KernelPilot 中的角色

KernelWiki 是 KernelPilot 的外部工程记忆。它的作用不是替代 correctness test、benchmark 或 profiler，而是在 Agent 生成候选 kernel 前提供可追溯的 prior art。

在 GPU kernel 优化中，真正有价值的信息经常分散在上游 Pull Request、commit diff、代码注释、benchmark 结果、issue 讨论、竞赛题解和官方文档中。比如：

- CUTLASS/CuTe 如何落地 Blackwell `tcgen05`、`TMEM`、`TMA`。
- SGLang、vLLM、FlashInfer、TensorRT-LLM 如何接入 SM100 内核。
- FlashAttention-4 为什么采用 ping-pong scheduling、2-CTA / 2-SM 协作或软件 exp。
- NVFP4、FP8 block scale、MoE grouped GEMM 在具体 shape 上如何调度。
- 某个 PR 解决的是 correctness、shape generalization、compile flag、padding、layout 还是性能回退。

KernelWiki 把这些工程知识整理成可被脚本检索、可被 Agent 阅读、可追溯到原始来源的知识库。Agent 的正确使用方式是：

```text
查询 KernelWiki
  -> 提取与当前 K/R/W 相关的来源、设计假设和风险
  -> 形成 candidate kernel 编辑计划
  -> 编译、正确性验证、benchmark、profile
  -> 将实测结果写入 ledger
  -> 根据证据保留、拒绝或修正该方向
```

因此，KernelWiki 只提供候选方向和证据来源。最终是否有效，必须由当前硬件、当前 shape、当前实现的实测结果决定。

## 2. 当前 NVIDIA KernelWiki 

当前 `external/KernelWiki` 聚焦 NVIDIA Blackwell / Hopper kernel 优化，重点覆盖 Blackwell SM100 / B200、Hopper SM90 / H100，以及与大模型推理相关的高性能内核。



当前顶层组成：

```text
external/KernelWiki/
├── SKILL.md
├── README.md
├── CLAUDE.md
├── index.md
├── references/
│   ├── primer.md
│   ├── schema.md
│   └── examples.md
├── data/
│   ├── aliases.yaml
│   ├── schemas.yaml
│   ├── tags.yaml
│   ├── version-claims.yaml
│   ├── tool-versions.yaml
│   └── refresh-cutoff.yaml
├── candidates/
├── sources/
│   ├── prs/
│   ├── blogs/
│   ├── docs/
│   └── contests/
├── wiki/
│   ├── hardware/
│   ├── techniques/
│   ├── kernels/
│   ├── patterns/
│   ├── languages/
│   └── migration/
├── artifacts/
├── queries/
└── scripts/
```

### 2.2 `SKILL.md`：Agent 入口与启用边界

`SKILL.md` 是 Agent 使用 KernelWiki 的入口。它明确规定：

- 何时启用：Blackwell / Hopper kernel 编程、tcgen05、TMEM、CLC、NVFP4、2-SM cooperative、FlashAttention-4、DeepGEMM、FlashMLA、MoE、Grouped GEMM、CuTe DSL、PTX、Triton、以及具体上游 PR 参考。
- 何时不启用：泛 CUDA 基础、CPU/host 侧框架集成、DeepEP / EPLB / DualPipe 等分布式系统问题。
- 如何查询：`query.py`、`get_page.py`、`grep_wiki.py`、`queries/` 交叉索引、`references/` 入门资料。
- 如何输出：必须引用 page id 和路径，沿 `sources:` 追溯，尊重 `confidence`，对性能数据标注 GPU、dtype、shape、metric、value、source_id。

这点很重要：KernelWiki 不是“看到关键词就回答”，而是一个带启用范围、证据规则和输出契约的 skill。

### 2.3 `sources/`：原始来源层

`sources/` 保存最接近原始资料的结构化页面。它不是简单网页复制，而是把 PR、博客、官方文档、竞赛题解等整理成统一 frontmatter + 正文格式。

当前来源覆盖包括：

- PR：CUTLASS、SGLang、vLLM、FlashInfer、PyTorch、DeepGEMM、CCCL / CUB、FlashAttention、TensorRT-LLM、TileLang 等。
- 官方文档：NVIDIA tuning guide、PTX ISA、CUDA 13、CUTLASS Blackwell、Triton 3.6 Blackwell、FlashAttention-4 等。
- 技术博客：Colfax CUTLASS Blackwell、tcgen05 tutorial、Blackwell microbenchmarking、DeepGEMM、FlashMLA、NSA、NVFP4 hackathon 等。
- 竞赛：GPU Mode NVFP4 Hackathon、FlashInfer MLSys 2026。

一个 PR source 页面会记录 repo、PR 号、标题、作者、日期、URL、架构、tags、techniques、hardware_features、kernel_types、languages、merge SHA、changed_paths 和 artifact_dir。例如 `pr-cutlass-2139` 记录了 Blackwell blockwise / groupwise GEMM，关联 `tcgen05`、`tmem`、`nvfp4`、`fp8`、CUTLASS 示例和 builder 文件。

这层的价值是保留出处。当 Agent 借鉴某个技巧时，不能只写“来自 KernelWiki”，而应记录具体 page id、source id、上游路径和适配内容。

### 2.4 `wiki/`：综合知识层

`wiki/` 是综合后的主题知识页面。它围绕硬件特性、优化技术、内核案例、问题模式、语言/DSL、架构迁移组织知识。

当前主要类别如下。

#### 硬件特性

`wiki/hardware/` 覆盖 Blackwell 关键硬件：

- `hw-tcgen05-mma`：Blackwell MMA 指令，替代 Hopper WGMMA；页面含 `confidence: verified` 和 `evidence_basis`，同时引用官方 tuning guide 与 CUTLASS PR。
- `hw-tmem`：Tensor Memory，Blackwell 专用片上累加存储。
- `hw-tma`：Tensor Memory Accelerator，异步 bulk load/store。
- `hw-clc`：Cluster Launch Control，用于 persistent kernel 和动态 tile 调度。
- `hw-2sm-cooperative`：2-SM / 2-CTA 协作 MMA。
- `hw-nvfp4`：NVFP4 / block-scale FP。
- `hw-mbarrier`、`hw-pdl-gdc` 等同步和 launch 相关特性。

#### 优化技术

`wiki/techniques/` 覆盖可迁移到 candidate 设计的优化方法：

- warp specialization
- persistent kernels
- ping-pong scheduling
- epilogue fusion
- pipeline stages
- shared memory swizzling
- double / multi buffering
- vectorized loads
- cache policy
- fine-grained quantization
- tile scheduling
- register budgeting
- software exp
- kernel fusion
- chunk-based parallelism

这些页面不仅写概念，还通过 `sources`、`related`、`prerequisites` 和 `reproducibility` 将技术连接到上游实现和可编译片段。

#### Kernel case study

`wiki/kernels/` 覆盖具体算子案例：

- FlashAttention-4
- DeepGEMM
- NVFP4 GEMM
- NVFP4 GEMV
- FP8 block-scale GEMM
- Fused MoE
- Gated Dual GEMM
- Grouped GEMM
- FlashMLA
- Native Sparse Attention
- Sparse MLA
- Gated Delta Net
- TensorRT-LLM Blackwell indexer

例如 `kernel-nvfp4-gemm` 的 frontmatter 中记录了：

- `architectures: [sm100, sm100a]`
- `tags: [gemm, nvfp4, fp4, block-scale, tcgen05, tmem, warp-specialization]`
- `sources: [contest-gpumode-p2, doc-cutlass-blackwell, pr-cutlass-2139]`
- `performance_claims`：B200、NVFP4、latency_us、数值和 source_id
- `artifact_dir: artifacts/kernels/nvfp4-gemm`

这类页面对 KernelPilot 尤其有用，因为它把“某算子怎么优化”压缩成可查询、可引用、可追溯的工程案例。

#### Problem pattern

`wiki/patterns/` 按性能症状组织诊断路径：

- low SM utilization
- memory bandwidth bound
- register pressure / low occupancy
- compute bound
- tail effect
- pipeline stalls
- MoE expert load imbalance

例如 `pattern-memory-bound` 将症状映射到候选技术，如 vectorized loads、swizzling、pipeline stages，并引用相关博客和官方 tuning guide。KernelPilot 中当 profile 显示某类瓶颈时，Agent 可以先查 pattern，再挑选候选技术。

#### Language / DSL

`wiki/languages/` 说明 Blackwell 上的开发表面：

- CUDA C++ with inline PTX
- CuTe DSL
- PTX SM100
- Triton Blackwell

例如 `lang-triton` 明确记录 Triton 3.6+ 对 Blackwell tcgen05 / TMEM lowering 的版本敏感结论，并通过 `version_sensitive` 指向中央版本声明。

#### Migration

`wiki/migration/` 记录 Hopper 到 Blackwell 的迁移路径：

- WGMMA -> tcgen05
- register accumulator -> TMEM

这使 Agent 不会把 Hopper 经验机械套到 Blackwell，而是知道哪些概念需要重写。

### 2.5 `artifacts/`：代码、patch 与资源包

`artifacts/` 是 KernelWiki 最接近代码的一层。它保存：

- PR diff / patch
- 提取的 kernel 源文件
- 博客配套代码
- derived snippet
- benchmark 片段
- MANIFEST / PROVENANCE

当前校验结果显示有 94 个 asset bundle，其中包括 verbatim、extracted、derived 三类。这个设计让 Agent 不只看到文字总结，还能看到实际代码结构、changed paths、patch 和可复现片段。

使用规则是：可以研究和移植思想，但如果代码或结构直接影响候选实现，必须在 ledger 中记录来源、路径、版本、许可证/通知和改动方式。最终候选仍必须在当前 workspace 中通过 K/R/W 验证。

### 2.6 `data/`：schema、标签、别名、版本声明

`data/` 让 KernelWiki 不只是全文搜索，而是一个轻量结构化知识库。

关键文件：

- `schemas.yaml`：不同页面类型的必填/可选字段。
- `tags.yaml`：受控术语表，覆盖 architectures、hardware_features、techniques、kernel_types、languages、source_category 等。
- `aliases.yaml`：别名映射。例如 B200 / Blackwell -> `sm100`，UMMA -> `tcgen05`，TMEM -> `tmem`。
- `version-claims.yaml`：版本敏感声明的中央注册表。
- `tool-versions.yaml`：Triton、CUTLASS、CUDA、PTX 等工具版本快照。
- `refresh-cutoff.yaml`：知识截止日期。

这套结构让 `query.py` 可以做别名归一、过滤、排序，也让 `validate.py` 可以检查 page id、引用、schema 和版本声明一致性。

### 2.7 `queries/`：预生成交叉索引

`queries/` 是自动生成的横向索引，方便 Agent 快速从一个视角跳到另一个视角：

- `by-problem.md`：症状 -> pattern -> 候选技术。
- `by-technique.md`：技术 -> 适配架构、置信度、相关页面。
- `by-hardware-feature.md`：硬件特性 -> wiki / PR。
- `by-kernel-type.md`：GEMM、attention、MoE、MLA、GEMV 等算子索引。
- `by-language.md`：CUDA C++、CuTe DSL、PTX、Triton 等。
- `by-repo.md`：按上游 repo 查看 PR 归档。

这类索引对 Agent 很重要：如果自然语言查询召回太宽，Agent 可以直接走结构化目录。

### 2.8 `scripts/`：查询和维护工具

KernelWiki 的主要查询路径：

```bash
cd external/KernelWiki

# 自然语言或关键词查询
python3 scripts/query.py "GEMM tcgen05 tmem Blackwell" --limit 12 --compact

# 按结构化字段查询
python3 scripts/query.py --tag nvfp4 --type kernel --compact
python3 scripts/query.py --repo vllm --architecture B200 --compact

# 打开页面
python3 scripts/get_page.py kernel-nvfp4-gemm --follow-sources
python3 scripts/get_page.py pr-cutlass-2139 --frontmatter-only

# 正则搜索
python3 scripts/grep_wiki.py "tcgen05\\.fence" --only wiki

# 全量校验
python3 scripts/validate.py
```

`query.py` 适合主题召回，`get_page.py` 适合精读，`grep_wiki.py` 适合找具体符号、API 或错误文本，`validate.py` 适合维护知识库质量。

### 2.9 页面 schema 和证据等级

KernelWiki 的页面采用 Markdown + YAML frontmatter。典型字段包括：

- `id`
- `title`
- `type`
- `architectures`
- `tags`
- `techniques`
- `hardware_features`
- `kernel_types`
- `languages`
- `sources`
- `related`
- `prerequisites`
- `confidence`
- `reproducibility`
- `performance_claims`
- `artifact_dir`
- `version_sensitive`
- `evidence_basis`

证据等级：

- `verified`：至少有官方文档和上游代码证据。
- `source-reported`：来自权威源码、论文、博客或主要项目报告。
- `inferred`：从多个来源综合推断。
- `experimental`：实验性、未文档化或版本敏感技巧。

可复现等级：

- `concept`
- `pseudocode`
- `snippet`
- `runnable`
- `benchmarked`

NVIDIA KernelWiki 成熟的关键不只是内容多，而是这些字段让 Agent 能判断：资料是否可信、是否可运行、能否迁移、适用于什么硬件、和当前任务关系是什么。

## 3. KernelWiki 如何服务 KernelPilot

在 KernelPilot / RLCR 循环中，KernelWiki 的使用应该进入 ledger，而不是停留在临时阅读。

推荐工作流：

```text
Round 0:
  1. 恢复 K/R/W 和目标硬件。
  2. 查询 KernelWiki 中算子、硬件、瓶颈、语言、上游 PR。
  3. 将 page id、source id、候选方向写入 research ledger。

Candidate round:
  1. 选择一个可验证假设。
  2. 修改 kernel / harness / dispatch。
  3. 编译、正确性、benchmark、profile。
  4. 将结果写入 lineage、attempt ledger、performance-map。
  5. 根据结果保留、拒绝或修正方向。

Review gate:
  1. 检查 correctness 是否被削弱。
  2. 检查 benchmark 是否可复现。
  3. 检查 KernelWiki 引用是否被正确转化为实测假设。
```

一个好 ledger 条目应包含：

```json
{
  "candidate": "v3_epilogue_fusion",
  "parent": "v2_tiled",
  "kernelwiki_pages": ["technique-epilogue-fusion", "kernel-gated-dual-gemm"],
  "sources": ["pr-cutlass-2139"],
  "hypothesis": "Fuse bias/scale into epilogue to reduce output memory traffic.",
  "changed_files": ["src/kernel.cu", "benchmarks/bench.py"],
  "correctness": "pass",
  "benchmark": {"shape": "M=64,N=2048,K=2048", "speedup": 1.18},
  "decision": "keep"
}
```

## 4. 当前 SDAAKernelWiki 的实际状态

当前仓库中已经存在 `external/SDAAKernelWiki`，它不是空想目录，而是一个已经可查询、可校验的 seed wiki。

本地校验结果：

```text
python3 external/SDAAKernelWiki/scripts/validate.py

OK: 26 pages, 26 ids
```

当前内容规模：

- `sources/local/`：5 个本地来源页，指向 `external/knowledge` 中的资料。
- `wiki/`：20 个主题页，覆盖 hardware、techniques、patterns、kernels、languages。
- `docs/gap-analysis.md`：1 个缺口分析页。
- `queries/`：4 个预生成索引。
- `references/`：primer 和 schema。
- `data/`：aliases、schemas、tags。
- `scripts/`：query、get_page、validate。

当前目录：

```text
external/SDAAKernelWiki/
├── README.md
├── SKILL.md
├── data/
├── docs/
├── queries/
├── references/
├── scripts/
├── sources/local/
└── wiki/
```

### 4.1 当前来源

当前 SDAAKernelWiki 主要来自 `external/knowledge`：

- `teco-T1.md`：T1 架构、Mesh、HBM、DMA、RMA 等优化笔记。
- `hardware_model.md`：optest-agent 当前硬件模型口径，定义 SPA/SPE、LDM、DMA/RMA/ACE、pipe0/pipe1、PMU 字段解释。
- `指令拍数和流水线派发.md`：P0/P1 指令拍数和静态分析口径。
- `rms_collect_metrics.analysis.md`：RMSNorm 性能 JSON 的瓶颈分析视图。
- `ACE.xlsx`：ACE cost model 表，包含 TFLOPS、Cycle、IO_AB、IO_C、write half、下发 delay 等 sheet。

这些资料很有价值，但证据形态主要是本地笔记、经验表和一次 RMSNorm 分析，还不是大规模上游 PR + 官方文档 + 可运行 artifact。

### 4.2 当前硬件页面

当前 `wiki/hardware/` 已覆盖：

- `hw-spa-spe`：SPA/SPE 执行模型。
- `hw-ldm`：LDM 本地存储。
- `hw-dma`：DMA 引擎模型。
- `hw-rma`：RMA 与 Mesh 通信。
- `hw-ace`：ACE 矩阵加速单元。
- `hw-pipe0-pipe1`：P0/P1 发射与流水。
- `hw-hbm-channel-bank-row`：HBM channel / pseudo-channel / bank / row 行为。

这些页面已经把 NVIDIA 术语替换为 SDAA 本硬件口径，例如：

- 不说 SM / warp，改说 SPA / SPE / pipe。
- 不说 shared memory，改说 LDM / local memory。
- 不说 tensor core，改说 ACE 或 SDAA 矩阵相关执行单元。
- 不说 occupancy，改说 active SPE、pipe launch、zero-launch、cannot-launch 等可见信号。

### 4.3 当前技术页面

当前 `wiki/techniques/` 覆盖：

- DMA 周期式划分。
- DMA 奇偶引擎交错。
- DMA 队列预算。
- RMA broadcast 选择。
- ACE double buffering。
- P0/P1 overlap。

这些技术页面直接服务 SDAA 算子生成。例如 GEMM 或 RMSNorm 中，如果 HBM/DMA 没打满，可以查询：

```bash
python3 external/SDAAKernelWiki/scripts/query.py "GEMM ACE DMA HBM" --compact
```

当前该查询能召回：

- `pattern-dma-hbm-underutilization`
- `hw-hbm-channel-bank-row`
- `hw-dma`
- `technique-dma-periodic-partitioning`
- `technique-dma-odd-even-interleave`
- `source-local-teco-t1`
- `pattern-ace-feeding-writeback`
- `source-local-ace-cost-table`
- `hw-ace`
- `pattern-rma-contention`

### 4.4 当前 pattern 页面

当前 `wiki/patterns/` 覆盖：

- DMA / HBM 未打满。
- LDM pressure。
- RMA contention。
- ACE feeding / writeback 瓶颈。
- scheduling bubbles。

这些页面对应 KernelPilot 中常见失败点：

- benchmark 慢但 DMA request 密度低。
- local-memory unarb cycles 高。
- zero-launch / cannot-launch 高。
- ACE 计算快但 feed 或 writeback 拖后腿。
- RMA 和 DMA 共享路径造成竞争。

### 4.5 当前 kernel / language 页面

当前 `wiki/kernels/` 只有 RMSNorm PMU 分析案例：

- `kernel-rmsnorm-pmu-analysis`

当前 `wiki/languages/` 有：

- `lang-sdaa-programming-model`

这说明 SDAAKernelWiki 还缺 GEMM、Softmax、LayerNorm、Reduce、Attention、Elementwise、Memcpy / DMA microbenchmark 等核心算子页面，也缺完整编译器/运行时/语言 API 页面。

### 4.6 当前查询和维护工具

当前 SDAAKernelWiki 有：

- `scripts/query.py`
- `scripts/get_page.py`
- `scripts/validate.py`

目前还缺：

- `grep_wiki.py`：用于搜索 API、错误文本、PMU 字段、指令助记符。
- `generate-indices.py`：自动从 frontmatter 生成 `queries/`。
- `ingest_*`：从官方文档、源码、benchmark、profile 结果生成 source 页面。
- `artifact` 校验：类似 KernelWiki 的 MANIFEST / PROVENANCE。

## 5. SDAAKernelWiki 不能直接复制 NVIDIA KernelWiki

SDAA 迁移不是 CUDA 术语替换。SDAA 的硬件口径、工具链、性能计数器和编程模型都不同。

### 5.1 术语迁移原则

| NVIDIA KernelWiki 术语 | SDAA 中应优先使用的口径 |
|---|---|
| SM | SPA / SPE，按实际上下文区分核组与执行核心 |
| warp / warp group | 不直接使用；改成 SPE 任务划分、pipe 发射、SIMD/vector lane 或实际编程模型术语 |
| shared memory | LDM / local memory |
| shared memory bank conflict | LDM bank / local-memory unarb / local-memory violate，除非官方确认不要一一对应 |
| tensor core | ACE 或矩阵相关加速单元 |
| TMA | DMA / RMA / HBM 搬运路径，不能直接等价 |
| occupancy | active SPE、launch share、zero-launch、cannot-launch、资源占用等替代指标 |
| L1TEX / L2 | 只有在 SDAA profiler 明确定义后才能使用对应层级 |
| Nsight Compute metric | SDAA PMU / SDPTI / optest metric |

### 5.2 证据迁移原则

NVIDIA KernelWiki 的很多优化技巧可以提供启发，但不能直接作为 SDAA 结论。例如：

- double buffering 可以迁移为 DMA / ACE / writeback overlap，但具体 buffer 数量、同步和 queue depth 必须由 SDAA 实测决定。
- memory-bound pattern 可以迁移为 HBM / DMA / LDM / RMA 诊断，但不能照搬 NCU 的 L1TEX、SM occupancy、eligible warps。
- GEMM epilogue fusion 可以作为候选方向，但 SDAA 上是否受 ACE writeback、LDM 容量、DMA 队列或 P1 发射限制，需要用 profiler 验证。
- persistent scheduling 的思想可以迁移为 SPE/SPA 层面的任务持久化或调度表，但不能照搬 CLC。

因此，SDAAKernelWiki 应该保留 KernelWiki 的结构化方法，而不是保留 NVIDIA 的术语体系。

## 6. 面向 SDAA 算子优化生成的目标结构

建议保持当前路径名 `external/SDAAKernelWiki`，并逐步扩展为以下结构：

```text
external/SDAAKernelWiki/
├── SKILL.md
├── README.md
├── references/
│   ├── primer.md
│   ├── schema.md
│   └── examples.md
├── data/
│   ├── schemas.yaml
│   ├── tags.yaml
│   ├── aliases.yaml
│   ├── tool-versions.yaml
│   ├── device-profiles.yaml
│   ├── ops.yaml
│   ├── metrics.yaml
│   ├── errors.yaml
│   └── ace-cost-model.yaml
├── sources/
│   ├── local/
│   ├── docs/
│   ├── code/
│   ├── examples/
│   ├── benchmarks/
│   ├── profiles/
│   └── issues/
├── wiki/
│   ├── hardware/
│   ├── techniques/
│   ├── kernels/
│   ├── patterns/
│   ├── languages/
│   ├── compiler/
│   ├── runtime/
│   └── profiling/
├── artifacts/
│   ├── docs/
│   ├── examples/
│   ├── kernels/
│   ├── benchmarks/
│   └── profiles/
├── queries/
└── scripts/
    ├── query.py
    ├── get_page.py
    ├── grep_wiki.py
    ├── validate.py
    ├── generate-indices.py
    ├── ingest_docs.py
    ├── ingest_profile.py
    ├── ingest_benchmark.py
    └── ace_cost.py
```

这个结构的目标是让 Agent 在每个失败点都有可查资料：

- 不知道怎么写 kernel：查 `wiki/languages/`、`wiki/runtime/`、`sources/examples/`。
- 编译失败：查 `wiki/compiler/`、`data/errors.yaml`、`sources/issues/`。
- 正确性失败：查 `wiki/kernels/<op>.md`、`data/ops.yaml`。
- 性能失败：查 `wiki/patterns/`、`wiki/profiling/`、`data/metrics.yaml`、历史 `artifacts/profiles/`。
- ACE/GEMM 调优：查 `wiki/hardware/ace.md`、`wiki/kernels/gemm.md`、`scripts/ace_cost.py`、历史 benchmark。

## 7. SDAAKernelWiki 需要补齐的内容

### 7.1 官方编程模型和运行时资料

当前最缺的是稳定、可引用的编程模型：

- kernel 函数语法。
- device / host API。
- 内存分配、拷贝、stream/event、同步 API。
- device 选择方式。
- kernel launch 方式。
- DMA / RMA / ACE API 函数签名。
- LDM 声明、对齐、容量限制。
- 编译命令、链接库、include path、runtime path。
- 支持 dtype、vector 类型、矩阵指令或 ACE intrinsic 的真实列表。

这些资料应进入：

- `sources/docs/`
- `wiki/languages/sdaa-programming-model.md`
- `wiki/runtime/`
- `wiki/compiler/`
- `data/tool-versions.yaml`

### 7.2 可运行 seed kernel

为了让 Agent 能生成真实 SDAA 算子，至少需要以下可运行样例，每个样例都必须有 K/R/W、构建命令、正确性 oracle、benchmark 命令和原始日志：

1. device memcpy / DMA copy。
2. elementwise add / mul。
3. reduce sum / max。
4. RMSNorm 或 LayerNorm。
5. GEMM baseline。
6. ACE matmul microkernel。
7. RMA broadcast / point-to-point microbenchmark。

这些样例应进入：

- `sources/examples/`
- `artifacts/examples/`
- `wiki/kernels/`

### 7.3 Profiler / PMU schema

当前已有 RMSNorm JSON 分析，但还缺通用 schema：

- 字段名称、单位、归一化方式。
- `zero_launch`、`cannot_launch`、`local_memory_unarb`、`DMA requests`、`RMA requests`、`ACE counters` 的定义。
- active SPE / active DMA engine 推导逻辑。
- runtime / driver 开销与 kernel 内部开销的分离方法。
- 指标到 pattern 的映射规则。
- 阈值和置信度规则。

建议新增：

- `data/metrics.yaml`
- `wiki/profiling/pmu-schema.md`
- `wiki/profiling/optest-json.md`
- `scripts/ingest_profile.py`

### 7.4 ACE cost model 机器化

`ACE.xlsx` 不能长期只作为人工表格存在。需要：

- 转成 CSV / JSON。
- 明确每个 sheet 的单位和维度。
- 建立 `scripts/ace_cost.py` helper。
- 用 GEMM / MatMul microbenchmark 进行 shape 覆盖验证。
- 将预测值和实测值写入 `wiki/kernels/gemm.md` 或 `artifacts/benchmarks/gemm/`。

ACE 页面应从“经验规则”升级为可查询、可计算、可验证的 cost model。

### 7.5 GEMM 专项知识

为了支撑用户当前目标“实现 SDAA 的算子优化生成”，GEMM 应作为第一优先级。至少需要：

- `wiki/kernels/gemm.md`
- `sources/examples/gemm-naive.md`
- `sources/examples/gemm-tiled.md`
- `sources/examples/ace-matmul.md`
- `artifacts/kernels/gemm/`
- `benchmarks/performance-map` 示例。

GEMM 页面应回答：

- 支持哪些 dtype：FP32、FP16、BF16、INT8 或其他。
- 累加类型是什么。
- A/B/C layout 和 leading dimension 如何定义。
- M/N/K tile 如何映射到 SPA/SPE。
- DMA 如何搬 A/B tile。
- LDM 如何分配 A/B/C / double buffer。
- ACE 如何 feed 和 writeback。
- 小 M、小 N、大 K、大方阵分别用什么策略。
- 什么时候用朴素 SPE 向量路径，什么时候用 ACE。
- correctness oracle 和容差如何定义。
- benchmark 如何计算 FLOPs。

### 7.6 错误库

SDAA 生态的错误信息对模型不友好，必须结构化沉淀：

- 编译错误。
- include / link 错误。
- runtime 初始化错误。
- device selection 错误。
- kernel launch 错误。
- dtype / layout mismatch。
- illegal memory / out-of-bound。
- profiler 采集失败。

建议新增：

- `data/errors.yaml`
- `wiki/compiler/common-errors.md`
- `sources/issues/`

每个错误模式至少包含：错误片段、触发条件、最小复现、修复方式、验证命令。

### 7.7 Artifact 和 provenance

SDAAKernelWiki 需要复刻 KernelWiki 的 artifact 思路：

```text
artifacts/kernels/gemm/naive/
├── MANIFEST.yaml
├── PROVENANCE.yaml
├── src/
├── build.log
├── correctness.log
├── benchmark.json
└── profile.json
```

`PROVENANCE.yaml` 应记录：

- 来源类型：official-doc / local-note / example / benchmark / profile / internal-code。
- 原始路径。
- 采集时间。
- 设备型号。
- SDAADriver / SDAARuntime / TECO-SMI 版本。
- 编译器版本。
- commit 或文件 hash。

没有 artifact，Agent 很难从“知道规则”进入“复现实验”。

## 8. 推荐 page schema

### 8.1 source-doc

```yaml
---
id: doc-sdaa-runtime-api
type: source-doc
title: SDAA Runtime API Reference
source_category: official-doc
hardware: [teco-t1]
tool_versions:
  SDAADriver: "3.1.0"
  SDAARuntime: "3.1.0"
tags: [runtime, memory, stream, event]
captured_at: 2026-06-04
confidence: verified
artifact_dir: artifacts/docs/runtime-api
---
```

### 8.2 source-code

```yaml
---
id: source-code-sdaa-gemm-naive
type: source-code
title: Naive SDAA GEMM Example
repo: local
path: examples/gemm/naive
commit: <commit-or-hash>
op_type: gemm
dtypes: [fp32]
hardware: [teco-t1]
tags: [gemm, baseline, correctness]
artifact_dir: artifacts/kernels/gemm/naive
confidence: source-reported
---
```

### 8.3 wiki-kernel

```yaml
---
id: kernel-sdaa-gemm
type: wiki-kernel
title: SDAA GEMM Kernel Optimization
op_type: gemm
hardware: [teco-t1]
tags: [gemm, dma, ldm, ace, hbm, p0-p1-overlap]
sources:
  - source-local-teco-t1
  - source-local-ace-cost-table
  - source-code-sdaa-gemm-naive
related:
  - hw-ace
  - hw-dma
  - hw-hbm-channel-bank-row
  - technique-ace-double-buffering
  - technique-dma-periodic-partitioning
confidence: source-reported
reproducibility: runnable
performance_claims:
  - device: TECO_AICARD_01
    driver: "3.1.0"
    runtime: "3.1.0"
    dtype: fp32
    shape: "M=1024,N=1024,K=1024"
    metric: GFLOPS
    value: <measured>
    source_id: benchmark-sdaa-gemm-001
artifact_dir: artifacts/kernels/gemm
---
```

### 8.4 wiki-pattern

```yaml
---
id: pattern-sdaa-ace-feeding-stall
type: wiki-pattern
title: ACE Feeding Stall
symptoms:
  - ace-feeding-stall
  - scheduling-bubbles
  - dma-hbm-underutilization
candidate_techniques:
  - technique-ace-double-buffering
  - technique-dma-periodic-partitioning
  - technique-p0-p1-overlap
metrics:
  - ace_active_ratio
  - dma_requests_per_inst
  - pipe1_cannot_launch
sources:
  - source-local-ace-cost-table
  - benchmark-sdaa-gemm-001
confidence: inferred
---
```

## 9. SDAAKernelWiki 与 KernelPilot 的对接

SDAA 任务进入 KernelPilot 时，应执行以下约束。

### 9.1 Prompt / skill 选择

如果目标硬件是太初 / SDAA，KernelPilot 应优先使用 `SDAAKernelWiki`，而不是 NVIDIA `KernelWiki`。只有在需要类比设计模式时，才查询 NVIDIA KernelWiki，并且必须把结论翻译到 SDAA 术语。

### 9.2 Round 0 必做项

SDAA Round 0 应输出：

- 设备快照：`teco-smi`、SDAADriver、SDAARuntime、设备名、显存。
- 工具链发现：编译器、runtime、headers、libs、profiler。
- K/R/W：目标 kernel、CPU reference、workload shape。
- SDAAKernelWiki 查询记录。
- 第一条候选谱系。
- 正确性命令、benchmark 命令、profile 命令。
- 主要风险：API 未知、dtype 未知、ACE API 未知、profiler 字段未知等。

### 9.3 Ledger 字段

每个 candidate 记录应包含：

```json
{
  "candidate": "v2_dma_tiled",
  "parent": "v1_naive",
  "sdaa_kernelwiki_pages": [
    "hw-dma",
    "hw-hbm-channel-bank-row",
    "technique-dma-periodic-partitioning"
  ],
  "hypothesis": "Periodic SPE partitioning improves HBM channel/bank coverage.",
  "measurements_required": [
    "latency",
    "GFLOPS",
    "DMA request density",
    "local-memory unarb",
    "zero-launch"
  ],
  "correctness": "pass",
  "benchmark": {},
  "decision": "keep-or-reject"
}
```

### 9.4 Performance map

SDAA workspace 应维护：

```text
benchmarks/performance-map.json
```

最少记录：

- shape。
- dtype。
- baseline latency。
- candidate latency。
- GFLOPS / TFLOPS。
- correctness tolerance。
- device snapshot。
- SDAAKernelWiki page id。
- 是否使用 ACE。
- 是否使用 DMA / RMA。
- profiler 摘要。

### 9.5 Feedback loop

每次真实优化后，都应把新发现写回：

- 如果知识库规则正确：补充 benchmark / profile artifact。
- 如果规则不适用：写入 rejected pattern 或 gap analysis。
- 如果发现新 API / 错误 / profiler 字段：新增 source 页面或 data 条目。
- 如果 GEMM 产生稳定模板：升级为 `wiki/kernels/gemm.md` 的可复用策略。

这一步是从“资料库”变成“算子优化生成系统”的关键。

### 

- 收集官方 runtime / compiler / profiler 文档。
- 增加 source-doc 页面。
- 增加 compile / run / profile smoke test。
- 增加 error pattern。
- 增加 device profile：TECO_AICARD_01、SDAADriver 3.1.0、SDAARuntime 3.1.0。

### Phase 2：GEMM seed kernel

- 建立 FP32 GEMM baseline。
- 建立 CPU reference。
- 建立 benchmark harness。
- 建立 ACE matmul microbenchmark。
- 将 `ACE.xlsx` 转成 JSON / CSV。
- 写 `wiki/kernels/gemm.md`。
- 写 `artifacts/kernels/gemm/`。

### Phase 3：Profiler 到 pattern 的闭环

- 定义 PMU / optest JSON schema。
- 将 zero-launch、cannot-launch、local-memory unarb、DMA/RMA、ACE、icache 等字段映射到 pattern。
- 建立 `scripts/ingest_profile.py`。
- 将 RMSNorm 分析从单例升级为模板。

### Phase 4：算子族扩展

按优先级扩展：

1. GEMM / MatMul。
2. Reduce / Sum / Max。
3. RMSNorm / LayerNorm。
4. Softmax。
5. Elementwise fusion。
6. Attention 子模块。
7. Quant / dequant / scaled matmul。

每个算子页面都必须包含 K/R/W、layout、dtype、correctness、benchmark、profile、已知限制和历史最佳候选。

