---
id: doc-sdaa-c-programming-guide-v3-1-0
title: "SDAA C 编程指南 v3.1.0"
type: source-doc
source_category: official-doc
product_version: "v3.1.0"
published_at: "2026-01-16"
created_at: "2026-03-26"
captured_at: "2026-06-05"
author: "docs.tecorigin.net"
architectures: [sdaa, teco-t1]
tags: [spa, spe, spm, global-memory, dma, rma, ace, simd, perf-sampling, tecocc-lto]
languages: [sdaa-c, sdaa-cpp, tecocc]
source_file_removed: "external/SDAA C编程指南_v3.1.0.pdf"
confidence: verified
---

# SDAA C 编程指南 v3.1.0

这是 `SDAA C编程指南` PDF 的结构化来源页。PDF 原件按用户要求不在仓库中保留；本页只保留用于 SDAAKernelWiki 检索和 KernelPilot 生成的摘要、章节索引、API 家族和约束事实。

## 文档元信息

- 标题：SDAA C 编程指南。
- 产品版本：v3.1.0。
- 发布日期：2026-01-16。
- PDF 元数据创建时间：2026-03-26。
- 作者元数据：docs.tecorigin.net。
- 页数：671。
- 抽取方式：`pdftotext -layout`。

## 章节索引

1. 概述：SDAA C 定义、Host-Device 主从异构模型、SPA/SPE 组织、工作流程、设备端 C/C++ 使用限制。
2. 最新动态：v1.9.0 到 v3.1.0 的接口和工具更新。
3. 快速入门：`.scpp` 文件、`__global__` kernel、`sdaaSetDevice`、`<<<...>>>` launch、`sdaaDeviceSynchronize`、`tecocc` 编译。
4. 异构计算模型：SPMD、kernel 函数、Host / Global / SPM 存储空间、硬件架构、数据传输、SDAARuntime。
5. 语言规范：`<<<placeHolder, stream>>>`、`__host__`、`__global__`、`__device__`、`__local__`、`__scoped_local__`、`threadIdx`、`threadDim`、标量/向量类型、头文件、命名空间、常用 Runtime 接口。
6. 环境变量：`SDAA_SYNC_PRINT`。
7. 函数接口：线程组、SPE 同步、SPM malloc/free、memset、DMA、RMA、Broadcast、MemoryStride、原子、matmul、transpose、SIMD、性能采样、设备信息、printf/abort/assert。
8. 数学函数：单精度、双精度、向量数学接口。
9. 高层次函数接口：batch math、activation、reduction。
10. 程序编译：TecoCC 命令行、LTO / 非 LTO 编译流程、动态/静态库、直接生成可执行文件。
11. 程序调试：运行时日志、TecoGDB、abort、assert。
12. 开发工具：TecoGDB、`sdaacfilt` 符号解码。
13. 性能调优：性能指标、性能采样、任务级并行、SPMD、SIMD、DMA/RMA/Broadcast、原子、matmul、向量、数学函数、编译优化。
15. 示例：向量运算、SPMD 矩阵乘、SUMMA 矩阵乘、自定义原子。
16. 算子开发指南：算子基本概念、加法算子、矩阵乘算子、性能调优、GEMM 基础和优化实战。
17. 常见问题：CMake、LTO 静态库索引、CUDA 程序迁移、VSCode 高亮补全。

## 对 KernelPilot 最重要的事实

- SDAA C 是运行在 SDAA 异构并行平台上的 C/C++ 编程模型，采用 Host-Device 主从异构运行模式。
- Device 侧由多个 SPA 构成；每个 SPA 包含多个 SPE，SPE 在 SDAA C 中相当于执行 SPMD 程序的计算核心。
- `threadIdx` 表示当前 SPE ID，`threadDim` 表示当前 SPA 内 SPE 数量。
- Kernel 由 `__global__` 修饰，返回类型需要为 `void`，通过 `<<<placeHolder, stream>>>` 从 Host 侧 launch。
- `placeHolder` 当前暂无实际含义；`stream` 是 SDAA stream，可缺省。
- `.scpp` 后缀用于让 TecoCC 识别 SDAA C 关键字。
- Global 存储空间属于 SPA 内共享的 device memory；SPM 是每个 SPE 私有片上本地存储。
- SPM 细分为堆、栈和 local 空间；`__local__` 声明 local 空间变量，不支持初始化。
- `__scoped_local__` 在开启 `--stack-on-global` 后用于把函数栈变量放入与 `__local__` 共享的 SPM local 空间。
- `malloc` / `free` 管理设备端 SPM 堆空间，分配自动按 64B 颗粒对齐。
- `memcpy` / `memcpy_stride` / `memcpy_async` 管理同一 SPA 内 Global / SPM 之间以及同一 SPE SPM 内的数据搬运；不同 SPE 的 SPM 间搬运需要 RMA 或 Broadcast。
- RMA 用于同一 SPA 内 SPE 间 SPM 数据搬运，SPM 地址和搬运量需要满足 4B 对齐/整数倍要求。
- Broadcast 用于同一 SPA 内一个指定 SPE 向多个 SPE 传输数据。
- `sdaa_matmul.h` 提供阻塞和非阻塞矩阵乘接口；非阻塞接口由 `matmul_init`、`matmul_load_weight`、`matmul_compute`、`matmul_store`、`matmul_wait` 组成。
- SIMD 向量类型包括 `intv16`、`uintv16`、`shortv32`、`ushortv32`、`halfv16`、`floatv16`。
- 性能采样接口包括 `perf_start`、`perf_stop`、`perf_print`、`clock`、`PerfData`，需要 `sdaa_perf.h`。
- 编译器为 `tecocc`，支持 LTO 与非 LTO 模式；跨 `.scpp` 设备函数调用需要 LTO。
- CUDA 迁移时不能照搬 block / warp / shared memory。SDAA C 只有 SPA 内的 `threadIdx` / `threadDim` 口径，没有 CUDA Warp 对应概念；CUDA shared memory 应重新映射为 Global / SPM。

## API 家族索引

| 家族 | 关键接口 |
|---|---|
| Host Runtime | `sdaaSetDevice`, `sdaaGetDevice`, `sdaaGetDeviceCount`, `sdaaDeviceSynchronize`, `sdaaMalloc`, `sdaaFree`, `sdaaMemcpy`, `sdaaMemset`, `sdaaStreamCreate` |
| ThreadGroup | `ThreadGroup`, `thread_group_set_mask`, `thread_group_include`, `thread_group_exclude`, `thread_group_is_included`, `thread_group_get_size`, `thread_group_clear` |
| SPE sync | `sync_threads`, `sync_threads(ThreadGroup)` |
| SPM allocation | `malloc(size, direct)`, `free(addr)`, `get_heap_size`, `get_stack_size`, `get_local_size` |
| DMA | `memcpy`, `check_memcpy`, `memcpy_stride`, `check_memcpy_stride`, `MemcpyHandle`, `memcpy_async`, `memcpy_wait`, `check_memcpy_async` |
| RMA | `rma_get`, `rma_put`, `RmaHandle`, `rma_set_thread_id`, `rma_set_thread_group`, `rma_async_get`, `rma_async_put`, `rma_complete`, `rma_wait` |
| Broadcast | `BroadcastHandle`, `broadcast_set_thread_group`, `broadcast`, `broadcast_async`, `broadcast_wait` |
| Atomic | `atomic_inc`, `atomic_add`, `atomic_add_noret`, `atomic_sub`, `atomic_sub_noret`, `atomic_cas`, `atomic_cas_bool` |
| Matmul | `matmul`, `check_matmul`, `MatmulHandle`, `matmul_init`, `matmul_load_weight`, `matmul_compute`, `matmul_store`, `matmul_wait`, `matmul_set_*` |
| Transpose | `transpose`, `TransposeHandle`, `transpose_async`, `transpose_wait`, `check_transpose_async` |
| SIMD | `simd_load`, `simd_store`, `simd_loadu`, `simd_storeu`, `simd_load_widen`, `simd_store_narrow`, `simd_set`, `simd_stretch`, arithmetic/compare/select/logic/bitwise ops |
| Perf/debug | `perf_start`, `perf_stop`, `perf_print`, `clock`, `printf`, `abort`, `assert` |

## 章节到 wiki 页面覆盖

| PDF 章节 | SDAAKernelWiki 覆盖页 |
|---|---|
| 1. 概述 | `lang-sdaa-c-programming-guide`, `hw-spa-spe`, `hw-sdaa-memory-model` |
| 2. 最新动态 | `doc-sdaa-c-programming-guide-v3-1-0` |
| 3. 快速入门 | `example-sdaa-quickstart`, `runtime-sdaa-host-api`, `compiler-tecocc-build-debug` |
| 4. 异构计算模型 | `lang-sdaa-c-programming-guide`, `hw-sdaa-memory-model`, `runtime-sdaa-host-api` |
| 5. 语言规范 | `lang-sdaa-c-programming-guide` |
| 6. 环境变量 | `runtime-sdaa-env-and-debug` |
| 7. 函数接口 | `technique-sdaa-thread-group-sync`, `technique-sdaa-dma-api`, `technique-sdaa-rma-broadcast-api`, `technique-sdaa-matmul-api`, `technique-sdaa-simd-vectorization`, `technique-sdaa-atomic-api`, `technique-sdaa-transpose-api`, `technique-sdaa-perf-sampling`, `runtime-sdaa-env-and-debug` |
| 8. 数学函数 | `technique-sdaa-math-and-high-level-api` |
| 9. 高层次函数接口 | `technique-sdaa-math-and-high-level-api` |
| 10. 程序编译 | `compiler-tecocc-build-debug` |
| 11. 程序调试 | `runtime-sdaa-env-and-debug`, `compiler-tecocc-build-debug` |
| 12. 开发工具 | `compiler-tecocc-build-debug`, `runtime-sdaa-env-and-debug` |
| 13. 性能调优 | `technique-sdaa-perf-sampling`, `technique-sdaa-simd-vectorization`, `technique-sdaa-dma-api`, `technique-sdaa-rma-broadcast-api`, `technique-sdaa-matmul-api`, `technique-sdaa-atomic-api`, `technique-sdaa-math-and-high-level-api`, `kernel-sdaa-gemm` |
| 15. 示例 | `example-sdaa-programming-guide-examples`, `example-sdaa-quickstart` |
| 16. 算子开发指南 | `kernel-sdaa-operator-development`, `kernel-sdaa-gemm` |
| 17. 常见问题 | `pattern-sdaa-compile-porting-errors`, `migration-cuda-to-sdaa-c`, `compiler-tecocc-build-debug` |

## 派生 wiki 页面

- `lang-sdaa-c-programming-guide`
- `runtime-sdaa-host-api`
- `runtime-sdaa-env-and-debug`
- `compiler-tecocc-build-debug`
- `hw-sdaa-memory-model`
- `example-sdaa-quickstart`
- `technique-sdaa-thread-group-sync`
- `technique-sdaa-dma-api`
- `technique-sdaa-rma-broadcast-api`
- `technique-sdaa-matmul-api`
- `technique-sdaa-simd-vectorization`
- `technique-sdaa-perf-sampling`
- `technique-sdaa-atomic-api`
- `technique-sdaa-transpose-api`
- `technique-sdaa-math-and-high-level-api`
- `kernel-sdaa-gemm`
- `kernel-sdaa-operator-development`
- `migration-cuda-to-sdaa-c`
- `pattern-sdaa-compile-porting-errors`
- `example-sdaa-programming-guide-examples`
