<div align="center">

# KernelPilot

**一个由 Humanize 驱动的自主 GPU 内核优化循环，连接 KernelWiki 证据和外部 Nsight Compute 性能分析 skill。**

[![GitHub stars](https://img.shields.io/github/stars/BBuf/kernel-pilot?style=social)](https://github.com/BBuf/kernel-pilot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/BBuf/kernel-pilot?style=social)](https://github.com/BBuf/kernel-pilot/forks)
[![Last commit](https://img.shields.io/github/last-commit/BBuf/kernel-pilot?style=flat-square)](https://github.com/BBuf/kernel-pilot/commits/main)
[![KernelWiki PR pages](https://img.shields.io/badge/KernelWiki_PR_pages-2692-2ea44f?style=flat-square)](external/KernelWiki/sources/prs/)
[![Knowledge cutoff](https://img.shields.io/badge/cutoff-2026--05--20-8250df?style=flat-square)](external/KernelWiki/data/refresh-cutoff.yaml)

</div>

KernelPilot 适用于严肃的 CUDA 内核调优场景，在这些场景中关键信息很容易丢失：哪个上游 PR 启发了候选方案、哪个 shape 出现了性能回退、Nsight Compute 实际报告了什么、哪条证据改变了下一次编辑、以及候选方案应该放入框架仓库还是独立实验中。

项目将 Humanize 循环逻辑保存在本仓库中，并使用两个外部 skill 子模块提供内核证据和性能分析：

| Skill | 来源 | 角色 |
| --- | --- | --- |
| [`humanize-kernel-agent-loop`](humanize/skills/humanize-kernel-agent-loop/) | KernelPilot | 围绕 `K`、`R`、`W` 创建干净的内核优化循环：独立工作区、正确性/基准证据、轻量级账本、可选的性能分析、可选的先验知识查找，以及 Humanize 审查。 |
| [`KernelWiki`](external/KernelWiki/) | [`BBuf/KernelWiki`](https://github.com/BBuf/KernelWiki/tree/kernelpilot-knowledge-expansion) | 当先前的 PR、wiki 综合页面、文档、博客或上游内核示例可以为当前设计提供参考时使用。 |
| [`ncu-report-skill`](external/ncu-report-skill/) | [`DongyunZou/ncu-report-skill`](https://github.com/DongyunZou/ncu-report-skill) | 当需要 Nsight Compute 证据来分析内核性能、诊断瓶颈、解释回退或选择下一次优化编辑时使用。 |

它们共同构成了一个可以从简单请求开始工作的优化循环：

```text
[$humanize-kernel-agent-loop] 为 M=64, N=2048, K=2048, fp16, bias=true 优化 SGLang 的 GEMM 路径，目标是比当前 SGLang 基线至少快 10%。
```

该循环在保持工程结构的同时保持策略上的轻量化：设置干净的工作区、提交脚手架、在内核编辑前验证活跃的严格成功 RLCR 状态、证明正确性、测量延迟、在先验知识有帮助时查阅 KernelWiki、在性能分析能改变下一次编辑时进行分析，并让 Humanize 审查每轮的证据。

## 为什么使用它

- **需要时提供先验知识。** 当 KernelWiki PR 产物、综合页面、博客/文档/竞赛和实时上游研究有助于当前内核决策时，agent 可以使用它们。
- **默认独立运行。** 候选内核不会污染 SGLang、vLLM、PyTorch 或其他大型框架仓库。循环创建一个包含绑定、测试、基准、账本、谱系和性能分析产物的隔离仓库。
- **需要时进行性能分析。** 当 Nsight Compute 证据可以解释基线、回退、平台期、意外提升或下一次优化编辑时，agent 使用 `ncu-report-skill`。
- **审查门控迭代。** Humanize RLCR 防止循环过早宣布胜利；默认循环预算为 84 次迭代，除非另行配置。
- **Shape 感知调优。** 循环将基准测试用例视为工作负载分布，构建性能图，并在不同场景需要不同内核或配置时发出调度/调优决策。

## 内核 Agent 循环

<p align="center">
  <img src="https://raw.githubusercontent.com/BBuf/kernel-pilot/main/docs/assets/kernel-agent-loop.svg" alt="KernelPilot Agent Loop" width="620">
</p>

## KernelWiki

KernelWiki 位于 [`external/KernelWiki`](external/KernelWiki/)。KernelPilot 将此子模块指向 `BBuf/KernelWiki` 的 `kernelpilot-knowledge-expansion` 分支，该分支包含通过 KernelWiki 自身的候选账本、PR 页面生成器、产物获取器、索引生成器和验证器合并的 KernelPilot 专属 PR 和源知识。

当前快照：

| 语料层 | 内容 |
| --- | --- |
| PR 页面 | 来自 SGLang、vLLM、TensorRT-LLM、PyTorch、FlashAttention、FlashInfer、CUTLASS/CuTe、CCCL、Triton、DeepGEMM、ThunderKittens、TileLang、QuACK 和 DeepSeek TileKernels 的 2,692 个已合并的 CUDA/Triton/CuTe/CUTLASS 相关 PR 页面。 |
| PR 产物 | 为选定的高价值 PR 获取的 `diff.patch` 和来源包，包括 FlashAttention SM100 MLA TopK、TensorRT-LLM Blackwell DSA/indexer 和 CCCL scan/memory 原语。 |
| 综合 | KernelWiki wiki 页面、博客/代码源注释、文档、竞赛，以及为硬件特性、技术、仓库、语言和内核类型生成的查询索引。 |

查询示例：

```bash
cd external/KernelWiki
python3 scripts/query.py "TensorRT FP4 DSA indexer" --limit 5 --compact
python3 scripts/query.py "FlashAttention SM100 MLA topk" --limit 5 --compact
python3 scripts/query.py --repo sglang --tag tma --compact
python3 scripts/grep_wiki.py "tcgen05|tmem" --only prs
python3 scripts/get_page.py kernel-flash-attention-sm100-mla-topk --follow-sources
python3 scripts/validate.py
```

## ncu-report-skill

`ncu-report-skill` 位于 [`external/ncu-report-skill`](external/ncu-report-skill/)。它提供当性能分析证据是最佳下一个真相来源时循环使用的工作流：

```bash
cd external/ncu-report-skill
less reference/01-workflow.md
less reference/03-collection.md
less reference/08-b200-metric-names.md
```

该 skill 强调每次分析使用独立运行目录、尽可能使用独立测试工具、`ncu --set full` 加源码级收集、通过 `ncu_report` API 进行 Python 解析，以及最终生成按证据支持排序的下一次编辑建议报告。

## 安装

克隆仓库及子模块：

```bash
git clone --recurse-submodules https://github.com/BBuf/kernel-pilot.git
cd kernel-pilot
```

对于已有的检出：

```bash
git submodule update --init --recursive
```

### Claude Code 安装

```bash
humanize/scripts/install-skills-claude.sh
```

安装程序会添加 KernelPilot 市场、安装 `humanize@KernelPilot`、将 `KernelWiki` 和 `ncu-report-skill` 链接到 Claude Code 的 skills 目录、安装 KernelWiki 查询依赖、使用绝对路径 `HUMANIZE_RUNTIME_ROOT`、`KERNELPILOT_ROOT`、`KERNELWIKI_ROOT` 和 `NCU_REPORT_SKILL_ROOT` 注入 Claude Code 已安装的 skill 缓存，如果仍有占位符残留则失败。

在 Claude Code 中，你应该能看到 `/humanize:start-rlcr-loop` 等命令和 `humanize-kernel-agent-loop`、`KernelWiki`、`ncu-report-skill` 等 skill。

### Codex 安装

```bash
humanize/scripts/install-skills-codex.sh
```

通用安装程序：

```bash
humanize/scripts/install-skill.sh --target codex
```

安装后，重启 agent 会话并检查以下 skill 是否可用：

```text
humanize-kernel-agent-loop
KernelWiki
ncu-report-skill
```

## Prompt 卡片

端到端 prompt 卡片位于 [`prompts/`](prompts/)：

| Prompt | 目标 |
| --- | --- |
| [`B200 int8_scaled_mm`](prompts/b200-int8-scaled-mm.md) | 在 B200 上优化 SGLang `int8_scaled_mm`，M=64, N=2048, K=2048, fp16 输出带 bias，目标是比 SGLang 基线至少 2.5 倍加速。 |
| [`B200 FA4 MHA`](prompts/b200-fa4-mha.md) | 构建独立的 BF16 前向 MHA 内核，在配置的 B200 用例上以几何平均 TFLOPS 至少超过官方 FlashAttention-4 5%。 |

## 维护

验证外部知识和安装程序连接：

```bash
cd external/KernelWiki
python3 scripts/validate.py

cd ../..
humanize/tests/test-ncu-report-skill.sh
humanize/tests/run-all-tests.sh
```

刷新或更新子模块：

```bash
git submodule update --remote external/KernelWiki
git submodule update --remote external/ncu-report-skill
```

## 相关项目

- [Humanize](https://github.com/PolyArch/humanize)：KernelPilot 为其专门化 GPU 内核优化的 RLCR 运行时。
- [KernelWiki](https://github.com/BBuf/KernelWiki/tree/kernelpilot-knowledge-expansion)：本仓库使用的扩展 GPU 内核证据 skill。
- [AI-Infra-Auto-Driven-SKILLS](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS)：更广泛的 serving、性能分析、SGLang、事件和模型优化 skill。
