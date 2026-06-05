---
id: technique-sdaa-thread-group-sync
title: "SDAA ThreadGroup 与 SPE 同步"
type: technique
architectures: [sdaa, teco-t1]
tags: [spa, spe, thread-grouping, load-balance]
confidence: verified
reproducibility: snippet
sources: [doc-sdaa-c-programming-guide-v3-1-0]
related: [hw-spa-spe, lang-sdaa-c-programming-guide, technique-rma-broadcast-selection]
---

# SDAA ThreadGroup 与 SPE 同步

ThreadGroup 用于把同一 SPA 内的 SPE 组织成子集，可用于同步、RMA、Broadcast 等接口。

## 完整 API

### ThreadGroup 构造函数

```cpp
ThreadGroup::ThreadGroup()                                          // 空组
ThreadGroup::ThreadGroup(unsigned long *ids, unsigned int size)     // SPE ID 数组
ThreadGroup::ThreadGroup(unsigned long mask, unsigned long pos = 0) // bit mask
```

- bit mask 构造：每个 bit 对应一个 SPE ID = bit_position + pos。
- 示例：`ThreadGroup(0x7)` → SPE0, SPE1, SPE2。

### thread_group_set_mask

```cpp
void thread_group_set_mask(ThreadGroup &thread_group, unsigned long mask,
                           unsigned long pos = 0)
```

用 mask+pos 设置组成员（覆盖已有设置）。

### thread_group_include / thread_group_exclude

```cpp
void thread_group_include(ThreadGroup &thread_group, unsigned long thread_id)
void thread_group_exclude(ThreadGroup &thread_group, unsigned long thread_id)
```

向组中添加/移除指定 SPE。修改自动反映到关联的 `RmaHandle`/`BroadcastHandle`。

### thread_group_is_included

```cpp
bool thread_group_is_included(const ThreadGroup &thread_group, unsigned long thread_id)
```

判断指定 SPE 是否在组内。

### thread_group_get_size

```cpp
unsigned int thread_group_get_size(const ThreadGroup &thread_group)
```

返回组内 SPE 数量。

### thread_group_clear

```cpp
void thread_group_clear(ThreadGroup &thread_group)
```

移除组内所有 SPE。

### sync_threads

```cpp
void sync_threads()
void sync_threads(const ThreadGroup &thread_group)
```

同步全部或指定组内 SPE。所有目标 SPE 都必须到达调用点才能继续。

## 同步规则

- 无参 `sync_threads` 必须放在当前 SPA 所有 SPE 都能执行到的代码路径。
- 带 ThreadGroup 的 `sync_threads` 必须保证组内所有 SPE 都能执行到。
- 如果仅部分 SPE 进入同步，应先用 `thread_group_is_included` 保护调用路径。

## 性能特征（来自 PDF Ch13）

**ThreadGroup 同步性能** 与 SPE ID 的组织方式强相关：

| 组型 | 示例 | 平均 beats/sync |
|------|------|----------------|
| 同商 (same quotient mod 8) | {0,1,2,3} | 226 |
| 同余 (same remainder mod 8) | {0,8,16,24} | 218 |
| 混合 (mixed) | {0,9,18,27} | 495 |

**最好 vs 最差：~2.19x**。优先使用同商或同余的 SPE ID 组合。

## Broadcast 相关的 ThreadGroup 性能

| 组型 | 平均 beats/broadcast |
|------|---------------------|
| {0-7} 连续 8 个 | 266 |
| {0,1,8,9,16,17,24,25} | 322 |
| {0,1,9,10,18,19,27,28} | 1362 |

**最好 vs 最差：~5.12x**。广播组设计应按完整行（0-7, 8-15...）或列（同余数）组织。

## KernelPilot 生成建议

- SPMD 数据划分优先用 `threadIdx`/`threadDim` 写循环，不硬编码 32。
- RMA/Broadcast 的参与 SPE 应显式构造 ThreadGroup，搬运前后同步。
- 不同 SPE 执行不同分支时，用 `thread_group_is_included` 保护避免误入 group sync。
- GEMM 中按行/列/块划分 SPE 时，ThreadGroup 设计应写入 ledger。
