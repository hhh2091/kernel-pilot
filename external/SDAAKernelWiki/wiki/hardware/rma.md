---
id: hw-rma
title: "RMA Mesh 通信"
type: hardware
architectures: [teco-t1, sdaa]
tags: [rma, mesh, ldm, dma]
confidence: source-reported
related: [technique-rma-broadcast-selection, pattern-rma-contention, hw-dma]
sources: [source-local-teco-t1, source-local-hardware-model]
aliases: [RMA, "remote LDM", "RMA put", "RMA get"]
---

# RMA Mesh 通信

RMA 是 SPA 内 SPE 间通过 2D mesh 通信的路径。每个 SPE 是一个网络节点，并带有全双工一级连接。本地笔记记录每个方向上限为 25.6 B/cycle，即 2.5 GHz 下 64 GB/s。

经验笔记：

- 在没有路线和节点冲突时，点对点传输可以接近单节点上限。
- 广播路径可能低于点对点带宽。
- 某些 ring 类场景中，`rma_put` 可能优于 `rma_get`。
- DMA get 返回流量和 RMA 列广播可能共享路径并产生拥塞。
- 路线冲突，以及节点同时发送/接收，都会显著降低带宽。

## 对生成的影响

- 对单向 producer/consumer 模式，优先尝试显式 RMA put，除非测量显示 get 更好。
- 根据行/列拓扑和 DMA 引擎使用情况选择广播模式。
- 除非测量证明有收益，否则避免让 DMA get 返回路径与 RMA 广播重叠。
