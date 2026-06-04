---
id: hw-ace
title: "ACE 矩阵加速单元"
type: hardware
architectures: [teco-t1, sdaa]
tags: [ace, ldm]
confidence: source-reported
related: [technique-ace-double-buffering, pattern-ace-feeding-writeback]
sources: [source-local-teco-t1, source-local-ace-cost-table, source-local-hardware-model]
aliases: [ACE, "matrix unit", "异步加速"]
---

# ACE 矩阵加速单元

ACE 是当前 SDAA 模型中的矩阵/异步加速路径。它运行在 1.25 GHz，即当前 SPE 频率的一半。

当前本地事实：

- `rt_ace_load_west` 在 west 方向加载时同步执行乘加；该步骤不需要额外计算指令。
- ACE 有两个累加器缓冲区，每个记录为 `128 x 32 x 2B = 8 KB`。
- 一个累加器缓冲区可用于当前计算，另一个可通过 `rt_ace_writeback` 写回 LDM，从而实现双缓冲。
- 理想 west feeding 按 1.25 GHz 下 64B/cycle 建模，即 80 GB/s。
- 当 west 与 north 加载重叠时，north 方向等效带宽需求可能降低；本地笔记中 128-row west 场景给出 20 GB/s 的 north 等效需求。
- `ACE.xlsx` 提供按 shape 组织的 TFLOPS、cycle、IO_AB、IO_C、writeback 和 dispatch-delay 表。

## 对生成的影响

- 通过 cost table 选择 ACE tile shape，不要假设 NVIDIA tensor-core 启发式适用。
- 利用两个累加器缓冲区重叠计算和 writeback。
- 在调整 tile shape 前，先确认瓶颈是 feeding、compute、writeback 还是 dispatch delay。
