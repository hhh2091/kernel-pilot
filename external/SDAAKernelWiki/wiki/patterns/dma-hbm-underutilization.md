---
id: pattern-dma-hbm-underutilization
title: "DMA / HBM 未打满"
type: pattern
tags: [dma, hbm]
symptoms: [dma-hbm-underutilization]
candidate_techniques: [technique-dma-periodic-partitioning, technique-dma-odd-even-interleave, technique-dma-queue-budgeting]
related: [hw-dma, hw-hbm-channel-bank-row]
sources: [source-local-teco-t1, source-local-rms-metrics-analysis]
---

# DMA / HBM 未打满

## 症状

数据搬运时间较差，但没有 DMA/HBM counter 饱和证据；或访问 metadata 显示未对齐、聚合访问稀疏、chunk 太小、队列过深。

## 可能原因

- per-SPE 块划分让完整 SPA 地址空间变稀疏。
- 请求不是 128B 对齐。
- 聚合访问没有覆盖 16 channel / 2KB group。
- DMA 引擎到 channel 的映射不佳。
- outstanding DMA 请求超过经验队列预算。

## 候选动作

1. 显式记录访问 metadata：base、stride、per-SPE bytes、aggregate bytes。
2. 尝试周期式划分。
3. 尝试 DMA 奇偶交错。
4. 将 outstanding read+write requests 控制在约 11 以内。
5. 围绕每 SPE 4KB、8KB、16KB 以及 shape 相关更大 size 做 benchmark。
