---
id: source-local-teco-t1
title: "TECO T1 架构与优化笔记"
source_category: local-note
path: external/knowledge/teco-T1.md
captured_at: 2026-06-04
tags: [hbm, mesh, dma, rma, ldm, ace, simd]
---

# TECO T1 架构与优化笔记

本地来源摘要：

- 数据进入网络后，DMA 和 RMA 会共享 mesh 流量。DMA/RMA 的方向和路线冲突可能主导通信性能。
- HBM 行为应从完整 SPA 视角分析。32 个 SPE 应共同覆盖足够的 channel/bank 地址空间，同时尽量避免不必要的跨行。
- DMA 通过 PPU 使用 128B packet。小请求不会自动合并。
- 16 个 HBM channel 的视角意味着 `128B x 16 = 2KB` 的对齐聚合访问是一个有用的带宽目标。
- 传统 DMA 访问中，每个 SPE 访问约 8-16KB 可能是较好的区间；部分双缓冲读场景指出每 SPE 4KB。
- DMA 引擎顺序 `(0, 2, 4, 6, 1, 3, 5, 7)` 被记录为一种有助于避免交叉开关冲突的奇偶交错方式。
- 经验 DMA 队列深度约为 11，读写请求共享这个队列。
- RMA 点对点可能高于广播带宽。部分场景下 RMA put 可能优于 RMA get。
- 行广播可能没有充分利用 DMA 引擎；双对角线行广播可以通过使用更多引擎提升带宽。
- ACE 有双累加器缓冲，可重叠计算和 writeback。
