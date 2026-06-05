---
id: kernel-sdaa-operator-development
title: "SDAA 算子开发指南到 KernelPilot 的映射"
type: kernel
architectures: [sdaa, teco-t1]
tags: [sdaa-c, tecocc, quickstart, perf-sampling]
confidence: verified
kernel_types: [elementwise, reduction, gemm, matmul]
languages: [sdaa-c, sdaa-cpp, tecocc]
related: [example-sdaa-programming-guide-examples, kernel-sdaa-gemm, runtime-sdaa-host-api, compiler-tecocc-build-debug]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA 算子开发指南到 KernelPilot 的映射

PDF 第 16 章覆盖算子开发、添加算子、matmul 算子和 GEMM 性能优化。KernelPilot 需要把这些内容映射成 K/R/W、workspace、benchmark 和迭代 ledger。

## 标准流程

1. 定义算子语义、dtype、layout 和 shape 集。
2. 写 Host Runtime harness：device 选择、memory allocation、copy、launch、sync、copy back。
3. 写 correctness reference。
4. 建立 baseline kernel。
5. 按 wiki 页面选择一个优化方向：SIMD、DMA/RMA/Broadcast、matmul/ACE、double buffering、P0/P1 overlap。
6. benchmark 并记录结果。
7. 用 profiler 或 perf sampling 解释瓶颈，再进入下一轮。

## 算子类型映射

| 算子 | 首查页面 |
|---|---|
| add / elementwise | `technique-sdaa-simd-vectorization`, `technique-sdaa-math-and-high-level-api` |
| reduction | `technique-sdaa-simd-vectorization`, `technique-sdaa-atomic-api` |
| memcpy / layout | `technique-sdaa-dma-api`, `technique-sdaa-transpose-api` |
| communication | `technique-sdaa-rma-broadcast-api`, `technique-rma-broadcast-selection` |
| GEMM / matmul | `kernel-sdaa-gemm`, `technique-sdaa-matmul-api` |

## 完成标准

一个 SDAA 算子 seed 至少需要：

- 可重复 build。
- 可重复 correctness。
- 可重复 benchmark。
- 明确 shape 元数据。
- attempt ledger 中记录 page id、假设、测量和下一步。
