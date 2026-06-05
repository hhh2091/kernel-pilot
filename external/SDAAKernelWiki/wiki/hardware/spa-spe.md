---
id: hw-spa-spe
title: "SPA 与 SPE 拓扑"
type: hardware
architectures: [teco-t1, sdaa]
tags: [spa, spe, hbm]
confidence: source-reported
related: [hw-dma, hw-ldm, hw-pipe0-pipe1, hw-sdaa-memory-model]
sources: [source-local-hardware-model, source-local-teco-t1, doc-sdaa-c-programming-guide-v3-1-0]
aliases: [SPA, SPE, "核组", "从核"]
---

# SPA 与 SPE 拓扑

T1 当前按 4 个 SPA 核组建模。每个 SPA 独占 16 GB HBM。除非任务明确涉及跨 SPA 行为，KernelPilot 分析应先从单 SPA 范围开始。

## 单 SPA 拓扑

| 单元 | 当前模型 |
|------|---------|
| SPE 数量 | 32 |
| 排布 | 4 行 × 8 列 |
| SPE 主频 | 2.5 GHz |
| ACE 主频 | 1.25 GHz |
| DMA 引擎 | 8 个按列绑定的引擎 |
| 每 SPE LDM | 256 KB |
| 每 SPA Global 存储 | 16 GB |

## SPE 内部架构（来自编程指南第 4 章）

每个 SPE 内部由以下功能单元组成：

| 单元 | 全称 | 功能 |
|------|------|------|
| **SU** | Scalar Unit | 执行标量算术/逻辑运算，从 SREG 接收数据 |
| **SREG** | Scalar Register | 存储标量数据，可与 SPM 和 Global 交换 |
| **VPU** | Vector Processing Unit | 执行向量操作（load、算术、类型转换、比较、选择），从 VREG 接收数据 |
| **VREG** | Vector Register | 存储向量数据，支持多标量元素并行读写 |
| **FU** | Function Unit | 执行矩阵乘等操作，**仅**与 SPM 交换数据 |
| **SPM** | Scratch Pad Memory | 每 SPE 私有的高速片上本地存储 |

## 数据交换路径

```
SPM Heap ↔ FU, SREG, VREG, stack, local, Global
SPM Stack ↔ FU, SREG, VREG, heap, local, Global（栈切到 Global 后则与全部交换）
SPM Local ↔ FU, SREG, VREG, heap, stack, Global
Global ↔ SREG, VREG, heap, stack, local
```

**关键约束**：FU（矩阵乘单元）仅从 SPM 读取/写入数据，不能直接访问 Global。所有矩阵乘 I/O 必须经过 SPM buffering。

## 对生成的影响

- 使用 `threadIdx` / `threadDim` 作为 SPE 身份和 SPA 规模抽象。
- 除非 RMA/DMA 通信模式要求有意区分发送者/接收者，否则保持每个 SPE 工作量均衡。
- 从完整 SPA 视角分析内存访问：32 个 SPE 合起来决定 HBM channel/bank 覆盖情况。
- 算子优化生成应显式把工作映射到 32 个 SPE 上。如果只有部分 SPE 激活，应把它视为 workload mapping 事实。
- 矩阵乘数据必经 SPM staging，不可从 Global 直连 FU。
