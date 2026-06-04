---
id: pattern-rma-contention
title: "RMA 路线与 DMA 竞争"
type: pattern
tags: [rma, dma, mesh]
symptoms: [rma-contention]
candidate_techniques: [technique-rma-broadcast-selection]
related: [hw-rma, hw-dma]
sources: [source-local-teco-t1]
---

# RMA 路线与 DMA 竞争

## 症状

DMA 和 RMA 重叠时通信性能下降，节点同时发送/接收时性能下降，或行/列广播带宽低于预期。

## 可能原因

- 数据进入网络后，RMA 和 DMA 共享 mesh 路径。
- DMA get 返回路径与 RMA 广播冲突。
- 路线冲突或节点 first-hop 冲突。
- 行广播未充分利用 DMA 引擎。

## 候选动作

- 对比 RMA put 和 RMA get。
- 中等 payload 优先测试点对点，再测试广播。
- 如果行广播没有充分利用引擎，尝试双对角线行广播。
- 除非 shape 必须且测量支持，否则谨慎使用全广播。
