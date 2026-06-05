---
id: technique-sdaa-dma-api
title: "SDAA C DMA 数据搬运接口"
type: technique
architectures: [sdaa, teco-t1]
tags: [dma, spm, global-memory, dma-alignment, async-dma]
confidence: verified
reproducibility: snippet
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-teco-t1]
related: [hw-dma, hw-hbm-channel-bank-row, pattern-dma-hbm-underutilization, technique-dma-periodic-partitioning, technique-dma-queue-budgeting]
---

# SDAA C DMA 数据搬运接口

DMA 数据搬运覆盖同一 SPA 内 Global / SPM 之间、Global / Global 之间，以及同一 SPE 内 SPM / SPM 之间的数据流动。

## 阻塞接口

| 接口 | 作用 |
|---|---|
| `memcpy(dst, src, size)` | 阻塞搬运。 |
| `check_memcpy(dst, src, size)` | 检查地址合法性、重叠、SPM 临时空间等。 |
| `memcpy_stride(dst, src, size, section_1d, MemoryStride)` | 带 1D stride 的阻塞搬运。 |
| `check_memcpy_stride(...)` | 检查 stride 搬运参数。 |

约束：

- 不支持不同 SPE 的 SPM 之间直接 DMA；该场景使用 RMA 或 Broadcast。
- Global / Global 搬运会临时占用 SPM 堆空间作为中转，指南给出的额外占用为 20KB。
- `memcpy_stride` 的 `section_1d` 需要是 4B 整数倍。
- stride 设置当前仅支持 Global 存储空间；SPM / SPM stride 搬运仅支持连续数据。

## 非阻塞接口

| 接口 | 作用 |
|---|---|
| `MemcpyHandle` | 控制不同非阻塞 DMA 搬运组。 |
| `memcpy_async(...)` | 非阻塞 Global / SPM 搬运。 |
| `memcpy_wait()` | 等待默认搬运组完成。 |
| `memcpy_wait(handle)` | 等待指定搬运组完成。 |
| `check_memcpy_async(...)` | 检查非阻塞参数。 |

非阻塞 DMA 仅适用于 Global 与 SPM 之间的数据搬运。生成器可用它建立 load/compute/store overlap。

## 与本地 T1 优化笔记的结合

`source-local-teco-t1` 进一步给出 DMA/HBM 经验规则：

- 全 SPA 视角看连续地址覆盖，不只看单个 SPE。
- DMA 大小和 offset 应优先满足 128B 对齐。
- 以周期式 SPE 划分提升 HBM channel/bank 覆盖。
- DMA 队列深度和奇偶 DMA 引擎顺序需要通过 profile / benchmark 验证。

## KernelPilot 生成建议

- 正确性优先可先用阻塞 DMA；性能候选应尽快切换到 `memcpy_async` + `memcpy_wait`。
- 每个 DMA candidate 记录：地址空间、搬运方向、size、section、stride、对齐、参与 SPE、是否 handle 分组。
- 若 profile 显示 HBM/DMA 未打满，优先查询 `pattern-dma-hbm-underutilization` 和 `technique-dma-periodic-partitioning`。
