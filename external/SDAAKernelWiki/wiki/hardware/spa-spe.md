---
id: hw-spa-spe
title: "SPA 与 SPE 拓扑"
type: hardware
architectures: [teco-t1, sdaa]
tags: [spa, spe, hbm]
confidence: source-reported
related: [hw-dma, hw-ldm, hw-pipe0-pipe1]
sources: [source-local-hardware-model, source-local-teco-t1]
aliases: [SPA, SPE, "核组", "从核"]
---

# SPA 与 SPE 拓扑

T1 当前按 4 个 SPA 核组建模。每个 SPA 独占 16 GB HBM。除非任务明确涉及跨 SPA 行为，KernelPilot 分析应先从单 SPA 范围开始。

单 SPA 内部：

| 单元 | 当前模型 |
|---|---|
| SPE 数量 | 32 |
| 排布 | 4 行 x 8 列 |
| SPE 主频 | 2.5 GHz |
| ACE 主频 | 1.25 GHz |
| DMA 引擎 | 8 个按列绑定的引擎 |
| 每 SPE LDM | 256 KB |

算子优化生成应显式把工作映射到 32 个 SPE 上。如果只有部分 SPE 激活，应把它视为 workload mapping 事实，而不是 NVIDIA occupancy 的等价物。

## 对生成的影响

- 使用 `threadIdx` / `threadDim` 作为 SPE 身份和 SPA 规模抽象。
- 除非 RMA/DMA 通信模式要求有意区分发送者/接收者，否则保持每个 SPE 工作量均衡。
- 从完整 SPA 视角分析内存访问：32 个 SPE 合起来决定 HBM channel/bank 覆盖情况。
