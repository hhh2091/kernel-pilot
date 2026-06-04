# SDAAKernelWiki Schema

## 页面类型

| 类型 | ID 前缀 | 用途 |
|---|---|---|
| `source-local` | `source-local-*` | 本地原始笔记、分析报告、表格或 HTML 产物。 |
| `wiki-hardware` | `hw-*` | SDAA 硬件特性页面。 |
| `wiki-technique` | `technique-*` | 优化技术与代码生成启发式。 |
| `wiki-pattern` | `pattern-*` | 症状 -> 诊断 -> 候选技术。 |
| `wiki-kernel` | `kernel-*` | 带证据的算子案例研究。 |
| `wiki-language` | `lang-*` | SDAA 编程模型、编译器或运行时指南。 |

## 置信度

- `verified`：官方文档 + 实现或 profiler 证据共同支持。
- `source-reported`：由本地笔记、经验表或分析报告支持。
- `inferred`：从多个来源综合得出，但没有直接验证。
- `experimental`：合理但仍需复测、官方确认或更多 shape 覆盖。

## SDAA 硬件词表

在 `tags`、`hardware_features` 或 `techniques` 中使用这些受控术语：

- 硬件：`spa`、`spe`、`ldm`、`dma`、`rma`、`ace`、`hbm`、`mesh`、`pipe0`、`pipe1`、`ppu`、`icache`、`simd`。
- 技术：`periodic-partitioning`、`dma-alignment`、`dma-odd-even-interleave`、`dma-queue-budgeting`、`rma-put-preference`、`double-diagonal-broadcast`、`strided-column-broadcast`、`ace-double-buffering`、`p0-p1-overlap`。
- 症状：`scheduling-bubbles`、`ldm-pressure`、`dma-hbm-underutilization`、`rma-contention`、`ace-feeding-stall`、`icache-miss`、`runtime-launch-overhead`。

## 算子生成契约

一个页面若要影响自动 SDAA 算子生成，应回答：

1. 它适用于哪类算子 shape 或访存模式？
2. 预期瓶颈是哪种硬件资源？
3. 它暗示哪种代码编辑或映射选择？
4. 什么测量可以确认或证伪这个选择？
5. 如果测量结果不支持该选择，下一步 fallback 是什么？
