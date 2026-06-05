---
name: SDAAKernelWiki
description: 用于优化 SDAA / TECO T1 kernel 与算子，尤其是涉及 SPA/SPE、LDM、DMA/RMA、ACE 矩阵加速、pipe0/pipe1 调度、HBM channel-bank-row 访问、optest PMU 字段或 SDAA 算子优化计划生成的问题。不要在未翻译到 SDAA 硬件本语前直接套用 NVIDIA SM/warp/shared-memory 假设。
argument-hint: "[natural-language-question] | [--tag dma --type technique] | [page-id]"
allowed-tools: "Bash Read Grep Glob"
---

# SDAAKernelWiki

这是 KernelWiki 在 SDAA / 太初 T1 上的对应知识 skill。当 KernelPilot 任务面向国产太初 / SDAA 硬件，而不是 NVIDIA Blackwell/Hopper 时，优先使用这里的知识。

## 查询流程

在本 skill 根目录下运行：

```bash
python3 scripts/query.py "RMSNorm zero launch LDM pressure" --compact
python3 scripts/query.py "SDAA C GEMM matmul broadcast double buffering" --compact
python3 scripts/query.py --tag dma --type technique --compact
python3 scripts/query.py --tag simd-vectorization --compact
python3 scripts/query.py "atomic transpose math activation reduction" --compact
python3 scripts/query.py --symptom scheduling-bubbles --compact
python3 scripts/get_page.py kernel-sdaa-gemm --follow-sources
python3 scripts/get_page.py example-sdaa-programming-guide-examples
python3 scripts/get_page.py hw-ace --follow-sources
python3 scripts/get_page.py docs-gap-analysis
```

问题较宽泛时先读 `references/primer.md`。新增页面或判断证据质量时读 `references/schema.md`。

## 硬件术语

优先使用 SDAA 本硬件术语：

- `SPA`、`SPE`、`SPM/LDM`、`Global memory`、`DMA`、`RMA`、`Broadcast`、`ACE`、`pipe0`、`pipe1`
- `HBM channel / pseudo-channel / bank / row`
- `launch / zero-launch / cannot-launch`、`local-memory unarb`、`DMA queue`
- `tecocc`、`.scpp`、`threadIdx`、`threadDim`、`__global__`、`__local__`

不要直接输出未经翻译的 NVIDIA 术语，例如 `SM`、`warp`、`shared memory bank conflict`、`occupancy`、`waves/SM`、`L1TEX`。如果要迁移 KernelWiki 中的模式，必须显式翻译到 SDAA 硬件口径。

## 证据规则

1. 回答时引用 page id 和路径。
2. 沿 `sources:` 追溯到 `sources/local/` 下的本地原始资料页。
3. 来自 `SDAA C 编程指南 v3.1.0` 的语言/API 规则可按 `verified` 使用；T1 微架构和性能经验仍应视为 `source-reported` 或 `inferred`，除非页面明确说明有官方最终微架构依据。
4. 静态指令拍数表只能支持 `possible` 级结论。只有结合 profiler、PMU、cycle log 或 benchmark 证据后，才能升级为 `likely` 或 `confirmed`。
5. 用于算子生成时，输出必须是可验证的优化计划：K/R/W、候选映射、预期瓶颈、必要测量项和 fallback。

## KernelPilot 集成

SDAA 任务在 KernelPilot 中应遵循：

1. 恢复 `K`、`R`、`W`。
2. 先查询 SDAAKernelWiki，再套用 NVIDIA KernelWiki 的启发式。
3. 用页面证据选择一个可测量的下一步编辑。
4. 在 attempt ledger 中记录影响本轮决策的 SDAA page id。
