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

头文件由 `sdaa_dma.h` 提供（RMA/Broadcast 接口与 DMA 共享此头文件）。

## RMA 接口

### 阻塞 RMA

#### rma_get

```cpp
void rma_get(void *local_addr, const void *remote_addr, size_t size,
             unsigned int local_id, unsigned int remote_id)
```

从 `remote_id` 号 SPE 的 SPM 读取数据到本地 `local_id` 号 SPE 的 SPM。

| 参数 | 说明 |
|------|------|
| `local_addr` | 本地 SPE 目标 SPM 地址 |
| `remote_addr` | 远端 SPE 源 SPM 地址 |
| `size` | 搬运字节数，必须为 4B 整数倍 |
| `local_id` | 本地 SPE 的 threadIdx |
| `remote_id` | 远端 SPE 的 threadIdx |

#### rma_put

```cpp
void rma_put(void *local_addr, const void *remote_addr, size_t size,
             unsigned int local_id, unsigned int remote_id)
```

将本地 SPE 的 SPM 数据写入 `remote_id` 号 SPE 的 SPM。

| 参数 | 说明 |
|------|------|
| `local_addr` | 本地 SPE 源 SPM 地址 |
| `remote_addr` | 远端 SPE 目标 SPM 地址 |
| `size` | 搬运字节数，必须为 4B 整数倍 |
| `local_id` | 本地 SPE 的 threadIdx |
| `remote_id` | 远端 SPE 的 threadIdx |

### 非阻塞 RMA

#### RmaHandle 构造函数

```cpp
RmaHandle::RmaHandle()
RmaHandle::RmaHandle(ThreadGroup *thread_group)
```

- 默认构造：不关联 ThreadGroup。
- 带 ThreadGroup 构造：关联指定 ThreadGroup，后续非阻塞 RMA 由 group 内 SPE 参与。

#### rma_set_thread_id

```cpp
void rma_set_thread_id(RmaHandle &handle, unsigned int local_id, unsigned int remote_id)
```

为 handle 设置本地 SPE ID 和远端 SPE ID。

#### rma_set_thread_group

```cpp
void rma_set_thread_group(RmaHandle &handle, ThreadGroup *thread_group)
```

为 handle 设置 ThreadGroup。修改后无需重新调用 `rma_set_thread_id`，handle 自动反映 ThreadGroup 变化。

#### rma_async_get / rma_async_put

```cpp
void rma_async_get(RmaHandle &handle, void *local_addr, const void *remote_addr,
                   size_t size)
void rma_async_put(RmaHandle &handle, void *local_addr, const void *remote_addr,
                   size_t size)
```

非阻塞 RMA 读写。发起后需要 `rma_complete` 或 `rma_wait` 等待完成。

| 参数 | 说明 |
|------|------|
| `handle` | RmaHandle 引用，已配置好 SPE ID 和 ThreadGroup |
| `local_addr` | 本地 SPE 的 SPM 地址 |
| `remote_addr` | 远端 SPE 的 SPM 地址 |
| `size` | 搬运字节数，必须为 4B 整数倍 |

#### rma_complete

```cpp
void rma_complete(RmaHandle &handle)
```

仅等待 handle 中 src/dst SPE 对之间的最后一个非阻塞 RMA 操作完成。

#### rma_wait

```cpp
void rma_wait(RmaHandle &handle)
```

等待所有 SPE 上通过该 handle 发起的非阻塞 RMA 操作完成。

### RMA 约束汇总

- **地址约束**：RMA 地址必须是 SPM 地址。
- **对齐要求**：SPM 地址需要 4B 对齐。
- **大小约束**：搬运量需要是 4B 整数倍。
- **参与约束**：仅本地和远端相关 SPE 执行对应 RMA 接口，其他 SPE 不应执行。不需要所有 SPE 都同步参与。
- **SPM 一致性**：使用 `malloc` 分配 SPM 参与 RMA 时，所有参与 SPE 应在同一路径分配，使 SPM 首地址一致，并在 RMA 前同步。
- **Handle 同步**：`RmaHandle` 创建后、非阻塞 RMA 前，需要一次 `sync_threads()`。
- **同地址重复操作**：若对同一 SPM 地址先后发起 RMA 携带不同数据，需在两次之间加 `sync_threads()` 保证时序。
- **SPM malloc/free**：若不同 SPE 此前 `malloc` 的空间大小不同、需先 `free` 再统一 `malloc`，才能保证 SPM 地址一致。

### RMA 典型场景

**场景 1：单个 SPE 向多个 SPE 发起非阻塞 RMA**

- 发送方 SPE 创建 RmaHandle，循环调用 `rma_set_thread_id(handle, sender_id, receiver_id)`，然后 `rma_async_put(...)`。
- 可选：使用 `rma_complete(handle)` 逐个等待单一远端完成。
- 最终：`rma_wait(handle)` 等待所有未完成操作。

**场景 2：多个 SPE 向单个 SPE 发起非阻塞 RMA**

- 每个发送方 SPE 分别调用 `rma_async_put` 向同一远端发送。
- 所有写入完成后，接收方才能安全读取数据。

---

## Broadcast 接口

Broadcast 用于同一 SPA 内一个指定 SPE 向多个 SPE 搬运数据。

### BroadcastHandle 及相关配置

#### BroadcastHandle 构造函数

```cpp
BroadcastHandle::BroadcastHandle()
BroadcastHandle::BroadcastHandle(ThreadGroup *thread_group)
```

- 默认构造：广播组包含当前 SPA 内所有 SPE。
- 带 ThreadGroup 构造：广播组仅为 thread_group 内的 SPE。
- 创建后需调用 `sync_threads()` 才能进行数据搬运。
- ThreadGroup 后续修改自动反映到 handle，无需重新调用配置接口。

#### broadcast_set_thread_group

```cpp
void broadcast_set_thread_group(BroadcastHandle &handle, ThreadGroup *thread_group)
```

为 handle 设置 ThreadGroup。修改后 ThreadGroup 的直接 API 调整会自动同步到 handle。

### 阻塞 Broadcast

#### broadcast

```cpp
void broadcast(void *dst, const void *src, size_t size, size_t section_1d,
               MemoryStride stride_1d, unsigned long root, BroadcastDirect direct)

void broadcast(void *dst, const void *src, size_t size, size_t section_1d,
               MemoryStride stride_1d, unsigned long root, BroadcastDirect direct,
               BroadcastHandle &handle)
```

| 参数 | 说明 |
|------|------|
| `dst` | 目标地址（SPM） |
| `src` | 源地址 |
| `size` | 搬运字节数，必须是 4B 倍数；受限于源/目标空间较小者 |
| `section_1d` | 1D section 大小（字节），必须是 4B 倍数；当两个 stride 字段均为 0 时无效（连续拷贝） |
| `stride_1d` | `MemoryStride` 结构体，stride 仅 Global 内存支持；跨步大小需小于 Global 空间 |
| `root` | 发送方 SPE 的 threadIdx；对于 `BroadcastGlobalToSpm`，root 必须在 thread group 内 |
| `direct` | `BroadcastDirect` 枚举值 |
| `handle` | 可选，`BroadcastHandle&` 标识接收 SPE 组 |

**BroadcastDirect 枚举值：**

- 非 stride 场景：`BroadcastGlobalToSpm`、`BroadcastSpmToSpm`
- Stride 场景：仅 `BroadcastGlobalToSpm` 支持 stride

**约束：**

- SPM 地址必须 4B 对齐。
- 搬运量必须 4B 对齐。
- stride 使用时，Global 空间 stride 必须 4B 倍数。
- **无 handle（全广播）**：SPA 内所有 SPE 必须执行 `broadcast()`，否则同步失败。
- **有 handle**：发送方和广播组内所有 SPE 必须执行 `broadcast()`，否则结果不可预测。
- 重复向同一地址广播不同数据需在两次间加 `sync_threads()`。
- 使用 `malloc` 分配 SPM 作为广播缓冲区时，所有参与 SPE 需分配相同大小，使 SPM 首地址一致，`malloc` 后需 `sync_threads()`。

### 非阻塞 Broadcast

#### broadcast_async

```cpp
// 带 root 参数版本：发送方 + 所有 handle 组内 SPE 均需调用
void broadcast_async(void *dst, const void *src, size_t size, size_t section_1d,
                     MemoryStride stride_1d, unsigned long root, BroadcastDirect direct,
                     BroadcastHandle &handle)

// 不带 root 参数版本：仅发送方 SPE 调用
void broadcast_async(void *dst, const void *src, size_t size, size_t section_1d,
                     MemoryStride stride_1d, BroadcastDirect direct,
                     BroadcastHandle &handle)
```

**关键区别：**

- **带 `root`**：发送方和所有 handle 组内 SPE 均执行。配对 `broadcast_wait(handle)`（无 `until_times`）。
- **不带 `root`**：仅发送方 SPE 执行。配对 `broadcast_wait(handle, until_times)`。

**约束与 `broadcast()` 相同**：4B 对齐、size 约束、stride 约束等。

#### broadcast_wait

```cpp
void broadcast_wait(BroadcastHandle &handle)
void broadcast_wait(BroadcastHandle &handle, unsigned int until_times)
```

| 参数 | 说明 |
|------|------|
| `handle` | BroadcastHandle 引用 |
| `until_times` | 可选，当前 SPE 接收广播的次数 |

**配对规则：**

- `broadcast_wait(handle)` ↔ 带 `root` 的 `broadcast_async`
- `broadcast_wait(handle, until_times)` ↔ 不带 `root` 的 `broadcast_async`

**约束：**

- 并非所有 SPE 都需要执行 `broadcast_wait`，但未执行的发送/接收 SPE 不保证完成。
- 不参与广播的 SPE 不得调用 `broadcast_wait(handle, until_times)`，但可安全跳过。

### Broadcast 典型场景

**场景 1：模拟核心阵列横向广播**

- 每行第一个 SPE 作为 root，向同行其他 SPE 广播。
- 使用 ThreadGroup 按行构建广播组。

**场景 2：模拟核心阵列纵向广播**

- 每列第一个 SPE 作为 root。
- 配合 RMA 实现跨列数据分发。

---

## MemoryStride

```cpp
typedef struct {
    size_t dst_stride;
    size_t src_stride;
} MemoryStride;
```

用于配置跨步数据传输参数。

| 字段 | 说明 |
|------|------|
| `dst_stride` | 目标 stride 单元大小（字节），仅 Global 内存支持 |
| `src_stride` | 源 stride 单元大小（字节），仅 Global 内存支持 |

**约束：**

- 两者均为 0 时为连续拷贝，忽略 `section_1d`。
- stride 仅 Global 内存支持，SPM-to-SPM 仅支持连续传输。
- 支持的 stride 组合：
  - Global → SPM（可配置 src_stride）
  - SPM → Global（可配置 dst_stride）
  - Global → Global（可配置双 stride）
  - SPM → SPM（仅连续）

---

## KernelPilot 生成建议

- SPE 间一对一或少量点对点优先尝试 RMA。
- 一对多共享数据优先尝试 Broadcast。
- GEMM 中 B tile 或公共向量复用可尝试 Broadcast，但要和 DMA 周期划分、LDM 容量和同步成本一起评估。
- 若 RMA 与 DMA 同时出现性能退化，查询 `pattern-rma-contention`，检查 Mesh 路径竞争。
- 非阻塞 Broadcast 的生命周期：`BroadcastHandle` 创建 → `sync_threads()` → `broadcast_async()` → `broadcast_wait()`。
- 如果 `broadcast_async` 不带 `root` 参数，仅发送方 SPE 调用即可，但 `broadcast_wait` 需要使用带 `until_times` 的版本。
- 若使用 `malloc` 分配 SPM 并参与 RMA/Broadcast，确保所有参与 SPE 执行相同的分配路径，否则 SPM 地址不一致导致数据错误。
