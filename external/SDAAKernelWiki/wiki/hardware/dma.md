---
id: hw-dma
title: "DMA 引擎模型"
type: hardware
architectures: [teco-t1, sdaa]
tags: [dma, hbm, ppu, mesh]
confidence: source-reported
related: [hw-hbm-channel-bank-row, technique-dma-periodic-partitioning, technique-dma-odd-even-interleave, pattern-dma-hbm-underutilization]
sources: [source-local-hardware-model, source-local-teco-t1, source-local-rms-metrics-analysis]
aliases: [DMA, "DMA engine", dma_get, dma_put]
---

# DMA 引擎模型

单 SPA 有 8 个 DMA 引擎，每个 SPE 列一个。每个 DMA 引擎由该列 4 个 SPE 共享。DMA 数据进入 mesh 后可能与 RMA 流量竞争。

当前本地规则：

- PPU 视角下 DMA packet 为 128B。
- 4B 请求和 128B 请求可能具有相近 packet 成本；请求不会自动合并。
- 16 个 HBM channel 给出一个有用目标：`128B x 16 = 2KB`。
- channel 映射被记录为 `(address / 128B) % 16`。
- 经验 DMA 队列深度约为 11 个读写请求总数。
- 奇偶引擎顺序 `(0, 2, 4, 6, 1, 3, 5, 7)` 在记录的访问模式中可减少流量冲突。

## 对生成的影响

- 尽可能生成 128B 对齐的 DMA 请求。
- 评估完整 SPA 的聚合访问，而不是只看单 SPE 连续访问。
- 在 benchmark 证明更深队列有效之前，将 outstanding DMA 读写请求控制在队列预算内。
- 记录候选实现使用的是块划分、周期划分还是跨步访问；这是后续诊断所必需的。
