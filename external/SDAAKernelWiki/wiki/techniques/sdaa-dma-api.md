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

DMA 数据搬运覆盖同一 SPA 内 Global/SPM 之间、Global/Global 之间，以及同一 SPE 内 SPM/SPM 之间的数据流动。

## 阻塞接口

### memcpy

```cpp
void *memcpy(void *dst, const void *src, size_t size)
```

阻塞型 DMA 搬运。支持 Global↔Global、同 SPE SPM↔SPM、Global↔SPM，均在同一 SPA 内。

| 参数 | 说明 |
|------|------|
| `dst` | 目标地址（Global 或 SPM） |
| `src` | 源地址（Global 或 SPM） |
| `size` | 搬运字节数 |

**空间大小约束**（源/目标不可重叠）：

- 同存储空间：理论最大搬运量 = 该空间的一半
- 不同存储空间：理论最大搬运量 = 较小空间的大小

**关键约束**：
- 不支持跨 SPE 的 SPM↔SPM DMA（用 RMA 或 Broadcast）
- Global↔Global 搬运会临时占用 **20KB SPM 堆空间**作为中转 buffer

### check_memcpy

```cpp
unsigned int check_memcpy(const void *dst, const void *src, size_t size)
```

校验参数合法性，返回 `MemcpyStatus` 位掩码：

| 位 | bit 0=1 时含义 |
|----|---------------|
| 0 | 0=参数合法(MEMCPY_SUCC)；1=有错误 |
| 1 | 源或目标地址非法 (MEMCPY_ERR_ADDR_ILLEGAL) |
| 2 | 源和目标重叠 (MEMCPY_ERR_MEM_OVERLAP) |
| 3 | SPM 堆溢出——20KB 临时 buffer 超出剩余堆 (MEMCPY_ERR_SPM_OVERSIZE) |

### memcpy_stride

```cpp
void *memcpy_stride(void *dst, const void *src, size_t size,
                    size_t section_1d, MemoryStride stride_1d)
```

带 stride 的阻塞 DMA。与 `memcpy` 传送范围相同。

| 参数 | 说明 |
|------|------|
| `section_1d` | 1D 搬运单元大小(字节)，**必须是 4B 倍数** |
| `stride_1d` | `MemoryStride` 结构体，stride 仅 Global 内存支持 |

**约束**：
- stride 仅 Global 内存支持，SPM↔SPM 仅连续搬运
- 若两个 stride 均为 0：连续搬运，`section_1d` 无效

### check_memcpy_stride

```cpp
unsigned int check_memcpy_stride(const void *dst, const void *src, size_t size,
                                  size_t section_1d, MemoryStride stride_1d)
```

比 `check_memcpy` 多返回 stride 参数错误（bit 4: MEMCPY_ERR_STRIDE_PARAM）。

## 非阻塞接口

非阻塞 DMA **仅**支持 Global↔SPM 传送，不支持 Global↔Global 或 SPM↔SPM（即使同 SPE）。

### MemcpyHandle

```cpp
MemcpyHandle::MemcpyHandle()
```

分组控制 handle。同 handle 的 `memcpy_async` 可被一个 `memcpy_wait(handle)` 同步。不指定 handle 时使用系统默认组。

### memcpy_async

```cpp
void *memcpy_async(void *dst, const void *src, size_t size, size_t section_1d,
                   MemoryStride stride_1d, MemcpyDirect direct)
void *memcpy_async(void *dst, const void *src, size_t size, size_t section_1d,
                   MemoryStride stride_1d, MemcpyDirect direct, MemcpyHandle &handle)
```

| 参数 | 约束 |
|------|------|
| `dst`, `src` | 必须是 Global 或 SPM；**4B 对齐** |
| `size` | **4B 倍数**；最大=SPM 空间大小 |
| `section_1d` | **4B 倍数** |
| `stride_1d` | stride 仅 Global 支持；stride 大小需 < Global 空间 |
| `direct` | `MemcpyGlobalToSpm` 或 `MemcpySpmToGlobal` |

### memcpy_wait

```cpp
void memcpy_wait()
void memcpy_wait(MemcpyHandle &handle)
```

同步屏障——阻塞至对应 handle 组的所有 `memcpy_async` 完成。不带参数等待默认组。

### check_memcpy_async

```cpp
unsigned int check_memcpy_async(const void *dst, const void *src, size_t size,
    size_t section_1d, MemoryStride stride_1d, MemcpyDirect direct)
unsigned int check_memcpy_async(..., MemcpyHandle &handle)
```

返回 `MemcpyAsyncStatus` 位掩码：

| 位 | bit 0=1 时含义 |
|----|---------------|
| 1 | 地址未 4B 对齐 (MEMCPY_ASYNC_ERR_ADDR_UNALIGNED) |
| 2 | size 非法 (MEMCPY_ASYNC_ERR_SIZE_ILLEGAL) |
| 3 | 方向非法 (MEMCPY_ASYNC_ERR_DIRECT_ILLEGAL) |
| 4 | stride 参数错误 (MEMCPY_ASYNC_ERR_STRIDE_PARAM) |

## 约束速查表

| 约束 | 适用范围 |
|------|---------|
| 需要 `using namespace sdaa;` | 所有 check_* 接口 |
| 不支持跨 SPE SPM↔SPM | 所有 DMA（用 RMA/Broadcast） |
| Global↔Global 临时占 20KB SPM | `memcpy`、`memcpy_stride` |
| 非阻塞仅 Global↔SPM | `memcpy_async` |
| 地址 4B 对齐 | `memcpy_async` |
| size/section_1d 4B 倍数 | `memcpy_async`、`memcpy_stride` |
| stride 仅 Global | 所有 strided 接口 |
| 必配对 async→wait | `memcpy_async`→`memcpy_wait` |
| 必配对 malloc→free | SPM malloc→free |

## 性能特征（来自 PDF Ch13）

| 搬运方向 | 带宽 | 说明 |
|---------|------|------|
| SPM→SPM（同 SPE） | ~62 GB/s | 最快 |
| Global→SPM | ~41 GB/s | |
| SPM→Global | ~40 GB/s | |
| Global→Global | ~16 GB/s | 额外 20KB SPM 开销 |
| 4B 对齐 vs 不对齐不同余数 | ~49x | 对齐极其关键 |
| 非阻塞 vs 阻塞 | ~1.72x | overlap 带来增益 |
| SPE ID 同余数 vs 不同余数 | ~2.47–3.29x | 选择不同 mod 8 余数的 SPE |

## KernelPilot 生成建议

- 正确性优先可先用阻塞 DMA；性能候选应尽快切换到 `memcpy_async` + `memcpy_wait`。
- 每个 DMA candidate 记录：地址空间、搬运方向、size、section、stride、对齐、参与 SPE、是否 handle 分组。
- 若 profile 显示 HBM/DMA 未打满，优先查询 `pattern-dma-hbm-underutilization` 和 `technique-dma-periodic-partitioning`。
