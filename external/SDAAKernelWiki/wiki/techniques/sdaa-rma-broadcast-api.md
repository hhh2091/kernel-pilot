---
id: technique-sdaa-rma-broadcast-api
title: "SDAA C RMA 与 Broadcast 数据搬运接口"
type: technique
architectures: [sdaa, teco-t1]
tags: [rma, broadcast, spm, async-rma, rma-broadcast-selection]
confidence: verified
reproducibility: snippet
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-teco-t1]
related: [hw-rma, pattern-rma-contention, technique-rma-broadcast-selection, technique-sdaa-thread-group-sync]
---

# SDAA C RMA 与 Broadcast 数据搬运接口

RMA 和 Broadcast 处理同一 SPA 内不同 SPE 的 SPM 数据交换。它们不能和 DMA 混为一谈：DMA 负责 Global/SPM 等路径，RMA/Broadcast 面向 SPE 间 SPM 通信。

## RMA 接口

阻塞接口：

- `rma_get(local_addr, remote_addr, size, local_id, remote_id)`
- `rma_put(local_addr, remote_addr, size, local_id, remote_id)`

非阻塞接口：

- `RmaHandle`
- `rma_set_thread_id`
- `rma_set_thread_group`
- `rma_async_get`
- `rma_async_put`
- `rma_complete`
- `rma_wait`

约束：

- RMA 地址必须是 SPM 地址。
- SPM 地址需要 4B 对齐。
- 搬运量需要是 4B 整数倍。
- 仅本地和远端相关 SPE 执行对应 RMA 接口，其他 SPE 不应执行。
- 使用 `malloc` 分配 SPM 参与 RMA 时，所有参与 SPE 应在同一路径分配，使 SPM 首地址一致，并在 RMA 前同步。
- `RmaHandle` 创建后、非阻塞 RMA 前，需要一次 SPE 同步。

## Broadcast 接口

接口族：

- `BroadcastHandle`
- `broadcast_set_thread_group`
- `broadcast`
- `broadcast_async`
- `broadcast_wait`

Broadcast 表达同一 SPA 内一个指定 SPE 向多个 SPE 搬运数据。它适合 GEMM / reduction / stencil 中的共享 tile、向量或标量参数分发。

约束：

- 搬运量需要是 4B 整数倍。
- 参与 SPE 的 SPM 分配路径应一致，避免同名 SPM 指针在不同 SPE 上地址不一致。
- 非阻塞 Broadcast 需要 handle 和 wait 管理生命周期。

## KernelPilot 生成建议

- SPE 间一对一或少量点对点优先尝试 RMA。
- 一对多共享数据优先尝试 Broadcast。
- 若 RMA 与 DMA 同时出现性能退化，查询 `pattern-rma-contention`，检查 Mesh 路径竞争。
- GEMM 中 B tile 或公共向量复用可尝试 Broadcast，但要和 DMA 周期划分、LDM 容量和同步成本一起评估。
