---
id: hw-sdaa-memory-model
title: "SDAA C Host / Global / SPM 存储模型"
type: hardware
architectures: [sdaa, teco-t1]
tags: [spm, global-memory, ldm, dma, rma]
confidence: verified
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-hardware-model]
related: [hw-ldm, hw-dma, hw-rma, hw-spa-spe, lang-sdaa-c-programming-guide]
---

# SDAA C Host / Global / SPM 存储模型

《SDAA C 编程指南 v3.1.0》将存储空间分为 Host 内存、Device Global 存储和 SPE 片上 SPM 存储。

## Host 内存

由 CPU 侧管理，用于准备输入、接收输出和驱动 runtime 调用。通过 `sdaaMemcpy` 与 Device Global 之间传输。

## Global 存储（Device Memory）

SPA 内所有 SPE 共享的 device memory：

- 通过 `__device__` 声明全局变量：`__device__ int g_mem = 1;`
- 通过 `sdaaMalloc`/`sdaaFree` 在 Host 侧申请/释放
- 通过 `sdaaMemset` 在 Host 侧初始化
- 容量：**16 GB** 每 SPA
- 访问延迟远高于 SPM；性能关键路径应先搬到 SPM 再计算

## SPM 存储（Scratch Pad Memory）

每个 SPE 私有的高速片上本地空间，细分为三区：

### 堆空间 (Heap)

- 管理方式：`malloc(size)` / `free(addr)`（设备端接口）
- `malloc` **自动按 64B 颗粒对齐**（4B 请求实际分配 64B，100B 请求分配 128B）
- 最大可分配 SPM 堆空间：**`0x3AC00` 字节**（240,640 B ≈ 235 KB）
- 默认低地址到高地址（起始 `0x1400`），也可 `AddressHighToLow`（起始 `0x3C000`）

### 栈空间 (Stack)

- 由函数调用和局部变量自动使用
- 通过 `--stack-on-global` 可将栈切换到 Global 存储
- 栈切到 Global 后，`__scoped_local__` 变量与 `__local__` 共享 SPM local 空间

### Local 空间

- 通过 `__local__` 声明（仅全局变量，不支持初始化）
- 通过 `__scoped_local__` 声明（函数作用域，`--stack-on-global` 时生效）
- 查询接口：`get_local_size()`

### SPM 空间查询

```cpp
size_t get_heap_size()    // 当前 SPE 堆总大小
size_t get_stack_size()   // 当前 SPE 栈总大小
size_t get_local_size()   // 当前 SPE local 空间总大小
```

## SPE 内部数据交换路径

SPE 内各单元间数据交换：

```
SPM Heap ↔ FU, SREG, VREG, stack, local, Global
SPM Stack ↔ FU, SREG, VREG, heap, local, Global
SPM Local ↔ FU, SREG, VREG, heap, stack, Global
Global ↔ SREG, VREG, heap, stack, local
```

**关键**：FU（矩阵乘单元）仅从 SPM 读写，不能直接访问 Global。

## 数据传输路径

| 路径 | 接口 | 约束 |
|------|------|------|
| Host ↔ Global | `sdaaMemcpy` | `sdaaMemcpyHostToDevice` / `sdaaMemcpyDeviceToHost` |
| Global ↔ Global (同 SPA) | `memcpy` / `memcpy_stride` | 临时占用 20KB SPM 堆 |
| Global ↔ SPM | `memcpy` / `memcpy_async` | 非阻塞仅此方向 |
| 同 SPE SPM ↔ SPM | `memcpy` | 不支持 stride |
| 跨 SPE SPM ↔ SPM | `rma_*` / `broadcast*` | 4B 对齐，4B 倍数 |

## 生成器约束

- Global/SPM 地址参与 DMA、RMA、Broadcast 时按对应接口对齐要求处理。
- 不同 SPE 的 SPM 地址不能用 DMA `memcpy` 直接搬运。
- 使用 `malloc` 为多 SPE RMA/Broadcast 分配 SPM 时，所有参与 SPE 须在相同代码路径分配，保证地址一致，再同步。
- 性能优化中尽量把热点数据放入 SPM，但要显式预算 SPM 堆、栈、local 和 20KB 临时 DMA buffer。
- FU 矩阵乘数据必经 SPM buffering，不可 Global 直连。
