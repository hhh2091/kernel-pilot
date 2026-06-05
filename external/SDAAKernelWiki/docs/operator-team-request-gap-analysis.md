---
id: docs-operator-team-request-gap-analysis
title: "SDAAKernelWiki 与 KernelWiki 对比及算子团队资料需求"
sources: [docs-gap-analysis, doc-sdaa-c-programming-guide-v3-1-0, source-local-teco-t1, source-local-hardware-model, source-local-instruction-latency-pipeline, source-local-rms-metrics-analysis, source-local-ace-cost-table]
---

# SDAAKernelWiki 与 KernelWiki 对比及算子团队资料需求

## 目的

本文用于回答两个问题：

1. 当前 `external/SDAAKernelWiki` 相比成熟的 NVIDIA `external/KernelWiki` 还差什么。
2. 为了让 KernelPilot 真正完成 SDAA 算子内核生成优化，需要向 SDAA 算子团队索取哪些材料。

结论先行：SDAAKernelWiki 已经有硬件词表、SDAA C 编程模型、GEMM 路线和若干优化启发式，但仍缺“可运行代码、真实性能证据、profiler schema、benchmark 原始数据、版本化工具链事实和失败案例”。这些缺口不补齐，Agent 可以生成计划和候选思路，但不能稳定、可复现地完成算子优化闭环。

## 当前规模对比

| 维度 | KernelWiki | SDAAKernelWiki | 影响 |
|---|---:|---:|---|
| 总文件数 | 3529 | 67 | SDAA 仍是 seed wiki，不是成熟工程记忆库。 |
| source markdown 页面 | 2735 | 6 | SDAA 缺少大量原始来源页，难以追溯具体代码、PR、日志和 benchmark。 |
| wiki markdown 页面 | 52 | 40 | SDAA 主题页数量已接近可用，但证据深度不足。 |
| artifact 文件 | 658 | 0 | SDAA 没有本地代码包、patch、日志、benchmark、manifest/provenance。 |
| query 索引 | 6 类 | 4 类 | SDAA 缺 `by-repo`、`by-language` 等横向入口。 |
| source 类型 | PR、doc、blog、contest | local、doc | SDAA 缺上游代码变更、团队内部案例、竞赛/benchmark 记录。 |
| kernel case | 多个真实算子，带性能声明 | GEMM 路线、RMSNorm PMU 案例 | SDAA 缺可运行 case study 和性能 claim。 |

## 成熟 KernelWiki 的关键能力

NVIDIA KernelWiki 的价值不只是页面多，而是有完整证据链：

1. `sources/prs/` 记录上游 PR，包括 repo、PR 号、作者、日期、merge SHA、changed paths、techniques、hardware features 和 artifact_dir。
2. `sources/docs/`、`sources/blogs/`、`sources/contests/` 提供官方文档、博客、竞赛题解和性能声明。
3. `artifacts/` 保存 patch、关键源文件、提取代码、benchmark 片段、MANIFEST 和 PROVENANCE。
4. `wiki/kernels/` 的 kernel 页面要求 `performance_claims`，性能结论带 GPU、dtype、shape、metric、value 和 source_id。
5. `data/version-claims.yaml` 和 `tool-versions.yaml` 记录版本敏感结论，避免把旧工具链经验误用到新环境。
6. `queries/` 提供按问题、技术、硬件、算子、语言、repo 的交叉索引。
7. `validate.py` 对 schema、page id、source 引用、artifact 关系、reproducibility 和版本声明进行约束。

对 KernelPilot 来说，这些能力让 Agent 能从“一个想法”追溯到“具体实现、具体 shape、具体性能证据和具体风险”。

## 当前 SDAAKernelWiki 已具备的能力

当前 SDAAKernelWiki 已经覆盖第一阶段推理所需的基础知识：

- 硬件词表：SPA、SPE、LDM/SPM、DMA、RMA、ACE、pipe0、pipe1、HBM、mesh。
- 官方 SDAA C 入口：`.scpp`、`tecocc`、kernel launch、`threadIdx/threadDim`、Host Runtime、SPM allocation、DMA/RMA/Broadcast、matmul、SIMD、atomic、transpose、math/high-level API、perf sampling、环境变量和设备端调试。
- 本地经验规则：DMA 128B/2KB、DMA 奇偶引擎顺序、DMA queue 预算、RMA 路线、ACE 双缓冲、P0/P1 overlap、RMSNorm PMU 症状。
- 算子路线：GEMM 从 baseline、SIMD、matmul/ACE、Broadcast 到 double buffering。
- 迁移规则：CUDA block/warp/shared memory 不能直接套用，必须翻译为 SPA/SPE/SPM/DMA/RMA/ACE。

这些内容足以让 Agent 做设计规划和候选方向选择，但还不足以让 KernelPilot 自动生成、编译、运行、分析并迭代出稳定高性能算子。

## 核心缺口

### 1. 缺可运行 seed kernel

当前 SDAAKernelWiki 有 quickstart 和示例路线，但没有可直接进入 KernelPilot 的代码包。缺：

- `.scpp` kernel 源码。
- Host runtime harness。
- CPU reference。
- correctness test。
- benchmark runner。
- shape 配置。
- 构建脚本。
- 原始运行日志。

影响：Agent 每次都要临场猜工具链、目录结构和 API 细节，容易把时间消耗在 smoke test 和编译错误上，而不是优化本身。

### 2. 缺真实算子案例的性能证据

KernelWiki 的 kernel case 往往带 shape、dtype、GPU、metric 和性能值。SDAA 当前只有路线和 PMU 分析片段，缺：

- GEMM 不同 shape 的 baseline 与优化结果。
- RMSNorm/LayerNorm/Softmax/Reduction/Elementwise/Transpose/Memcpy 的性能表。
- vendor baseline 或框架 baseline。
- 每次优化改动前后的速度、正确性、失败原因。

影响：Agent 只能推断“可能有用”，不能判断“在 T1 这个 shape 上是否值得做”。

### 3. 缺 SDAA profiler / PMU schema

当前已记录 zero-launch、cannot-launch、local-memory unarb、DMA request density 等词，但缺字段定义：

- 指标来自哪个工具：optest、SDPTI、PMU、runtime log、perf sampling。
- 字段单位、归一化方法、采样窗口。
- active SPE 计算方式。
- DMA/RMA/ACE counter 含义。
- 何种阈值对应何种 pattern。
- profile 原始输出样例。

影响：KernelPilot 无法把 profiler 输出自动映射到 `pattern-*` 页面，下一步优化仍依赖人工解释。

### 4. 缺工具链和版本事实

SDAA 编译/运行高度依赖版本。当前有 SDAA C 编程指南 v3.1.0，但还缺：

- `tecocc` 实际版本和常用参数矩阵。
- Runtime、Driver、头文件、库路径、CMake 接入方式。
- LTO / non-LTO 的真实工程模板。
- 已知编译错误和修复方式。
- 与 Paddle SDAA / vendor BLAS / custom op 框架的版本兼容关系。

影响：Agent 很容易生成“看起来像 SDAA C”的代码，但在真实机器上不可编译。

### 5. 缺 ACE / matmul 底层事实和 cost model 验证

当前 wiki 有 `sdaa_matmul.h` 的官方接口，以及本地 ACE cost table 的抽象描述，但还缺：

- `sdaa_matmul.h` 真实头文件和示例。
- 阻塞/非阻塞 matmul 的可运行 microbenchmark。
- ACE cost table 的机器可读 CSV/JSON。
- 表中 TFLOPS、cycle、IO_AB、IO_C、writeback、dispatch delay 的单位定义。
- 多 shape 实测验证。
- ACE feeding/writeback 相关 PMU 字段。

影响：GEMM 生成无法可靠判断 tile、K/N 对齐、SPM 占用、writeback 和 double buffering 是否正确。

### 6. 缺内存与通信 microbenchmark

当前有 HBM channel-bank-row、DMA/RMA 经验规则，但缺实测基准：

- Global <-> SPM DMA 吞吐。
- DMA size、alignment、stride、queue depth sweep。
- SPE mapping 与 8 个 DMA engine 的关系。
- RMA put/get、Broadcast 的拓扑敏感性。
- RMA 与 DMA 同时发生时的争用。
- HBM channel/bank/row 地址映射验证。

影响：Agent 无法把访问模式改动和硬件瓶颈建立可靠因果关系。

### 7. 缺 artifacts / provenance 层

SDAAKernelWiki 当前没有 `artifacts/`。缺：

- 代码 bundle。
- patch / diff。
- benchmark 原始 JSON/CSV。
- profile 原始输出。
- MANIFEST。
- PROVENANCE。
- license / ownership 说明。

影响：知识库只能做文字摘要，不能支持 Agent 阅读真实代码结构或复用可验证片段。

### 8. 缺失败案例和调试知识

成熟优化系统需要知道哪些路走不通。当前缺：

- 编译失败日志。
- runtime crash 日志。
- 错误结果案例。
- 性能退化案例。
- DMA/RMA/ACE 错误用法。
- LTO、CMake、链接、符号解码问题。

影响：Agent 会重复犯团队已经踩过的坑。

## 向算子团队索取的材料

### P0：没有这些就很难闭环

| 材料 | 需要内容 | 推荐格式 | 用途 |
|---|---|---|---|
| 最小可运行 GEMM seed | `.scpp` kernel、host harness、CPU reference、build/run/test/benchmark 命令 | 一个 tar/zip 或 repo 子目录 | 建立 KernelPilot 第一个可执行 SDAA workspace。 |
| 工具链发现清单 | `teco-smi`、`tecocc --version`、头文件路径、库路径、runtime/driver 版本、CMake 示例 | `toolchain.md` + 命令输出 txt | 防止 Agent 猜命令、猜路径。 |
| 官方/团队推荐编译模板 | LTO/non-LTO、动态库、静态库、可执行文件、自定义 op 的标准命令 | `Makefile`、`CMakeLists.txt`、README | 让生成代码可编译。 |
| correctness/benchmark 方法 | shape 集、dtype、容差、warmup/repeat、计时 API、同步方式、TFLOPS 公式 | `benchmark_spec.md` + runner | 固定性能评估口径。 |
| profiler/optest 样例 | 原始输出、字段解释、采集命令、推荐指标 | 原始 log/json/csv + `metrics_schema.md` | 替代 NCU，接入 pattern 诊断。 |
| GEMM baseline 数据 | naive、vendor BLAS/框架 GEMM、团队优化版本的性能 | CSV/JSON，带环境元数据 | 定义优化目标和对比上界。 |

### P1：决定优化质量上限

| 材料 | 需要内容 | 推荐格式 | 用途 |
|---|---|---|---|
| GEMM 优化版本谱系 | baseline -> tiled -> SIMD -> matmul/ACE -> Broadcast -> double buffering 的代码和结果 | 每个版本一个目录 + lineage.jsonl | 训练 Agent 如何逐轮优化。 |
| ACE / matmul microbench | shape sweep、tile 参数、SPM 使用、matmul API 配置、性能 | CSV/JSON + 源码 | 建立 GEMM cost model。 |
| DMA microbench | size、alignment、stride、queue depth、SPE mapping sweep | CSV/JSON + 源码 | 校验 DMA/HBM 规则。 |
| RMA/Broadcast microbench | put/get/broadcast、thread group、拓扑、争用测试 | CSV/JSON + 源码 | 支撑跨 SPE 数据复用策略。 |
| 典型算子 seed | elementwise、reduction、RMSNorm、LayerNorm、Softmax、Memcpy、Transpose | 每个算子 K/R/W + 源码 + 日志 | 扩展 KernelPilot 到非 GEMM。 |
| 失败案例库 | 编译错误、runtime 错误、错误结果、性能退化 | markdown + 原始日志 | 降低重复踩坑。 |

### P2：让知识库接近成熟 KernelWiki

| 材料 | 需要内容 | 推荐格式 | 用途 |
|---|---|---|---|
| 内部 PR / MR 摘要 | 标题、作者、日期、变更路径、问题、方案、性能影响 | `source-pr` 风格 markdown | 模仿 KernelWiki 的 source-pr 层。 |
| 代码片段授权说明 | 哪些代码可进入 wiki artifacts，哪些只能摘要 | LICENSE/NOTICE/ownership | 避免代码来源不清。 |
| 版本敏感声明 | 哪些 API/性能结论随 Driver/Runtime/tecocc 版本变化 | `version-claims.yaml` | 防止旧经验误用。 |
| 工具版本矩阵 | Driver、Runtime、TecoCC、Paddle SDAA、BLAS、profiler | `tool-versions.yaml` | 支撑复现。 |
| 算子团队调优手册 | 团队内部调优 checklist 和禁忌 | markdown | 转化为 patterns 和 techniques。 |

## 每份材料必须带的元数据

为了能进入 SDAAKernelWiki，每份资料最好包含：

```yaml
id: source-team-...
title: ...
owner: ...
date: YYYY-MM-DD
captured_at: YYYY-MM-DD
hardware:
  device: TECO_AICARD_01
  driver: ...
  runtime: ...
  memory_gb: 64
toolchain:
  tecocc: ...
  headers: ...
  libs: ...
operator:
  type: gemm
  dtype: fp32
  layout: row-major
workloads:
  - name: square_1024
    M: 1024
    N: 1024
    K: 1024
commands:
  build: ...
  correctness: ...
  benchmark: ...
  profile: ...
results:
  correctness: ...
  latency_us: ...
  tflops: ...
  baseline: ...
artifacts:
  code_dir: ...
  logs_dir: ...
  profile_dir: ...
license_or_usage: internal-ok | summary-only | public-ok
```

## 建议给算子团队的请求邮件/消息

```text
我们正在把 KernelPilot 从 NVIDIA KernelWiki 扩展到 SDAA/太初 T1，
目标是让 Agent 能自动生成、测试、benchmark 并迭代优化 SDAA 算子。

当前 SDAAKernelWiki 已整理 SDAA C 编程指南、SPA/SPE/SPM/DMA/RMA/ACE
基础知识和 GEMM 优化路线，但缺可运行代码、真实性能数据、profiler
schema 和失败案例。请协助提供以下材料：

P0:
1. 一个最小可运行 GEMM seed，包括 .scpp kernel、host harness、CPU reference、
   build/test/benchmark 命令和原始日志。
2. 当前机器/容器的 SDAA 工具链清单：teco-smi、tecocc 版本、头文件路径、
   库路径、runtime/driver 版本、CMake/Makefile 示例。
3. GEMM baseline 数据：naive、vendor BLAS/框架 GEMM、已有团队优化版本，
   请包含 shape、dtype、layout、latency、TFLOPS、正确性容差和环境信息。
4. profiler/optest/PMU 的采集命令、原始输出样例和字段解释。

P1:
5. GEMM 优化谱系代码和结果：baseline、SIMD、matmul/ACE、Broadcast、
   double buffering 等版本。
6. DMA、RMA/Broadcast、ACE/matmul microbenchmark 及结果。
7. elementwise、reduction、RMSNorm/LayerNorm、Softmax、Memcpy、Transpose
   等最小可运行算子样例。
8. 编译失败、runtime crash、错误结果、性能退化等失败案例和修复方式。

请尽量保留原始命令和日志。代码若不能公开进入仓库，也可以提供 summary-only
版本，但需要说明可引用范围。
```

## 进入 SDAAKernelWiki 的转化规则

收到材料后按以下方式落库：

1. 原始说明、日志和团队材料进入 `sources/team/` 或 `sources/local/`。
2. 可复用代码、patch、benchmark、profile 进入 `artifacts/`，并添加 MANIFEST / PROVENANCE。
3. 可运行样例进入 `wiki/examples/`，并标注 `reproducibility: runnable`。
4. 有性能数据的算子案例进入 `wiki/kernels/`，补充 `performance_claims`。
5. profiler 字段和阈值进入 `wiki/patterns/` 与 `data/metrics.yaml`。
6. 版本敏感结论进入 `data/version-claims.yaml`。
7. 工具链版本进入 `data/tool-versions.yaml`。
8. 每次新增后运行 `scripts/validate.py` 和代表性 `query.py`。

## 优先级路线

### 第一周：让 GEMM 能跑

- 收到最小 GEMM seed。
- 建立 `templates/sdaa-gemm-workspace/`。
- 固化 build/test/benchmark JSON 输出。
- 将 GEMM baseline 写入 `kernel-sdaa-gemm`。

### 第二周：让 profiling 能解释

- 收到 profiler/optest/PMU schema。
- 将字段映射到 `pattern-scheduling-bubbles`、`pattern-ldm-pressure`、`pattern-dma-hbm-underutilization`、`pattern-ace-feeding-writeback`。
- 建立 profile parser。

### 第三周：让优化能复用

- 收到 GEMM 优化谱系。
- 增加 DMA/RMA/ACE microbenchmark。
- 写入 artifacts 和 performance_claims。
- 让 KernelPilot ledger 自动记录 SDAAKernelWiki page id、shape、结果和拒绝原因。

## 完成标准

当以下条件满足时，可以认为 SDAAKernelWiki 达到“可支撑 SDAA 算子生成优化”的最小可用状态：

1. 至少一个 GEMM seed workspace 可以在 SDAA 机器上 build、correctness、benchmark。
2. 至少 3 类基础 microbenchmark 可运行：DMA、RMA/Broadcast、ACE/matmul。
3. 至少 5 类算子有 K/R/W seed：GEMM、elementwise、reduction、RMSNorm/LayerNorm、Memcpy/Transpose。
4. profiler/optest 输出能自动映射到至少 4 个 pattern。
5. `wiki/kernels/` 至少有 3 个带性能数据的 SDAA kernel case。
6. `artifacts/` 有代码、日志、profile 和 provenance。
7. KernelPilot 一轮优化能在 ledger 中记录 page id、候选假设、正确性、性能和下一步。

## 风险

- 如果只补文档、不补代码和日志，SDAAKernelWiki 会停留在“解释型知识库”，不能支撑自动优化。
- 如果只给优化后代码、不保留 baseline 和失败谱系，Agent 学不到迭代路径。
- 如果 profiler 字段没有 schema，pattern 页面无法闭环。
- 如果版本信息不完整，Agent 可能把某个 Driver/Runtime/TecoCC 下成立的经验误用到另一套环境。
- 如果代码授权不清晰，artifacts 无法进入仓库，只能保留摘要，复现能力会下降。
