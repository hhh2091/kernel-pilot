---
id: hw-hbm-channel-bank-row
title: "HBM Channel、Bank 与 Row 行为"
type: hardware
architectures: [teco-t1, sdaa]
tags: [hbm, dma]
confidence: source-reported
related: [hw-dma, technique-dma-periodic-partitioning, pattern-dma-hbm-underutilization]
sources: [source-local-teco-t1, source-local-hardware-model]
aliases: [HBM, channel, bank, row]
---

# HBM Channel、Bank 与 Row 行为

当前 T1 笔记强调完整 SPA 的 HBM 访问形态：

- DMA 视角下可见 16 个 channel。
- 每个 channel 处理 128B 单元。
- channel 内 bank 可以并行工作，但 row 切换代价较高。
- `128B x 16 = 2KB` 的聚合访问可以覆盖所有 channel。
- 32 个 SPE 应共同访问足够低位地址空间，以覆盖 channel 和 bank，同时避免过度跨行。
- 一条经验规则是：将 32 个 SPE 同时访问的地址跨度控制在约 512KB 内；传统 DMA 模式下，每 SPE 8-16KB 左右可能较优。

## 对生成的影响

- 在 SPA 级别判断 HBM 合并访问，而不是只看单 SPE。
- 当块划分导致完整 SPA 访问稀疏或 row 不友好时，优先尝试周期/循环划分。
- 在 benchmark metadata 中记录 base address、stride、per-SPE bytes、aggregate bytes 和 alignment。
