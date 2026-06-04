---
id: hw-pipe0-pipe1
title: "pipe0 与 pipe1 发射模型"
type: hardware
architectures: [teco-t1, sdaa]
tags: [pipe0, pipe1, simd, dma, rma, ace]
confidence: source-reported
related: [technique-p0-p1-overlap, pattern-scheduling-bubbles]
sources: [source-local-hardware-model, source-local-instruction-latency-pipeline, source-local-rms-metrics-analysis]
aliases: [P0, P1, pipe0, pipe1]
---

# pipe0 与 pipe1 发射模型

当前分析使用双管线模型：

- `pipe0` / P0：偏计算指令，包括标量/向量整数和浮点。
- `pipe1` / P1：偏访存、控制、DMA/RMA/ACE 下发、分支、sync 和 barrier。

硬件可异步发射，并在依赖允许时支持双发射。静态拍数表只能指示方向；需要结合 zero-launch、cannot-launch、sync wait、local-memory wait 等运行时 counter 才能确认瓶颈。

## 对生成的影响

- 交错独立的 P0 计算和 P1 访存/控制工作。
- 在正确性允许时，将 wait 移出热点区域。
- 将高 zero-launch 或 cannot-launch 视作调度/发射症状，先检查源码结构，再判断是否为内存饱和。
