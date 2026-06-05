---
id: hw-sdaa-memory-model
title: "SDAA C Host / Global / SPM 存储模型"
type: hardware
architectures: [sdaa, teco-t1]
tags: [spm, global-memory, ldm, dma, rma]
confidence: verified
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-hardware-model]
related: [hw-ldm, hw-dma, hw-rma, lang-sdaa-c-programming-guide]
---

# SDAA C Host / Global / SPM 存储模型

《SDAA C 编程指南 v3.1.0》将存储空间分为 Host 内存、Device Global 存储和 SPE 片上 SPM 存储。SDAAKernelWiki 中已有 `LDM` 页面；从编程指南口径看，SPM 是每个 SPE 私有的高速片上本地存储，和本地硬件模型中的 LDM 口径相近。写生成器时应优先使用指南 API 名称 `SPM`，性能分析时可映射到 `LDM / local memory` 指标。

## Host 内存

Host 内存由 CPU 侧管理，用于准备输入、接收输出和驱动 runtime 调用。Host 与 Device Global 之间的数据传输使用 `sdaaMemcpy`。

## Global 存储

Global 存储是 SPA 内所有 SPE 共享的 device memory：

- 可通过 `__device__` 声明全局变量。
- 可通过 `sdaaMalloc` / `sdaaFree` 在 Host 侧申请和释放。
- 容量口径：指南存储表给出 Global 存储空间为 16GB。
- 访问 Global 通常比访问 SPM 慢；性能关键路径应考虑搬到 SPM 后计算。

## SPM 存储

SPM 是每个 SPE 私有的高速片上本地空间，细分为：

| 区域 | 管理方式 | 查询接口 | 注意事项 |
|---|---|---|---|
| 堆空间 | `malloc` / `free` | `get_heap_size` | `malloc` 自动按 64B 颗粒对齐。 |
| 栈空间 | 函数调用和局部变量 | `get_stack_size` | 开启 `--stack-on-global` 后栈切换到 Global。 |
| local 空间 | `__local__` / `__scoped_local__` | `get_local_size` | `__local__` 不支持初始化；`__scoped_local__` 与 `--stack-on-global` 相关。 |

SPM malloc 约束：

- 需求空间自动 64B 对齐。
- 指南给出的最大可分配 SPM 堆空间为 `0x3AC00` 字节。
- 默认低地址到高地址分配；也支持 `AddressHighToLow`。

## 数据传输路径

| 路径 | 接口 |
|---|---|
| Host <-> Device Global | `sdaaMemcpy` |
| 同一 SPA 内 Global <-> Global | `memcpy` / `memcpy_stride` |
| Global <-> SPM | `memcpy` / `memcpy_async` |
| 同一 SPE 内 SPM <-> SPM | `memcpy` |
| 不同 SPE 的 SPM <-> SPM | `rma_*` 或 `broadcast*` |

## 生成器约束

- Global/SPM 地址参与 DMA、RMA、Broadcast 时需要按对应接口的对齐要求处理。
- 不同 SPE 的 SPM 地址不能用 DMA `memcpy` 直接搬运。
- 使用 `malloc` 为多 SPE RMA/Broadcast 分配 SPM 时，需要所有参与 SPE 在相同代码路径分配，保证地址一致，再同步。
- 性能优化中应尽量把热点数据放入 SPM，但要显式预算 SPM 堆、栈、local 和临时 DMA buffer。
