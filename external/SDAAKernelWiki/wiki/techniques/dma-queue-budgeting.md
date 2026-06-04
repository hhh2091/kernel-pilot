---
id: technique-dma-queue-budgeting
title: "DMA 队列预算"
type: technique
architectures: [teco-t1, sdaa]
tags: [dma, dma-queue-budgeting]
confidence: source-reported
reproducibility: concept
related: [hw-dma, pattern-dma-hbm-underutilization]
sources: [source-local-teco-t1]
---

# DMA 队列预算

本地笔记记录经验 DMA 队列深度约为 11，读写共享。连续请求中的第 12 个请求可能比前面的请求代价高很多。

## 规则

在 benchmark 证明其他选择更优之前：

- outstanding DMA read+write requests <= 11。
- 避免发起大量 tiny DMA 请求后再统一 wait。
- 优先使用 128B 对齐 chunk，并设计可与 P0 计算重叠的队列计划。

该规则应视为 `source-reported` 且 shape-dependent。
