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

ThreadGroup 用于把同一 SPA 内的 SPE 组织成子集，并可用于同步、RMA、Broadcast 等接口。

## API 摘要

| 接口 | 作用 |
|---|---|
| `ThreadGroup()` | 创建空线程组。 |
| `ThreadGroup(unsigned long *thread_group, unsigned int size)` | 通过 SPE ID 数组创建线程组。 |
| `ThreadGroup(unsigned long mask, unsigned long position = 0)` | 通过 bit mask 创建线程组；每个 bit 对应一个 SPE。 |
| `thread_group_set_mask` | 设置线程组 mask。 |
| `thread_group_include` | 向线程组添加 SPE。 |
| `thread_group_exclude` | 从线程组移除 SPE。 |
| `thread_group_is_included` | 判断 SPE 是否在组内。 |
| `thread_group_get_size` | 获取组内 SPE 数量。 |
| `thread_group_clear` | 清空线程组。 |
| `sync_threads()` | 同步当前 SPA 内全部 SPE。 |
| `sync_threads(ThreadGroup)` | 同步指定线程组。 |

## 同步规则

- 无参 `sync_threads` 必须放在当前所有 SPE 都能执行到的代码路径。
- 带 ThreadGroup 的 `sync_threads` 必须保证指定线程组内的所有 SPE 都能执行到。
- 如果仅部分 SPE 进入同步，应先用 `thread_group_is_included` 保护调用路径。

## KernelPilot 生成建议

- SPMD 数据划分优先用 `threadIdx` / `threadDim` 写循环，而不是硬编码 32。
- 对 RMA/Broadcast 的参与 SPE 应显式构造 ThreadGroup，并在数据搬运前后同步。
- 对不同 SPE 执行不同分支时，避免让不参与的 SPE 误入 group sync。
- 每个候选 kernel 的 ThreadGroup 设计应写入 ledger，尤其是 GEMM 中按行/列/块划分 SPE 时。
