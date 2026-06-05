---
id: example-sdaa-programming-guide-examples
title: "SDAA C 编程指南示例集合"
type: example
architectures: [sdaa, teco-t1]
tags: [quickstart, simd-vectorization, matmul, atomics, broadcast]
confidence: verified
reproducibility: concept
kernel_types: [vector, matmul, atomic, reduction]
languages: [sdaa-c, tecocc]
related: [example-sdaa-quickstart, kernel-sdaa-gemm, technique-sdaa-atomic-api, technique-sdaa-simd-vectorization]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA C 编程指南示例集合

PDF 第 15 章提供示例，第 16 章提供算子开发指南。SDAAKernelWiki 不保留 PDF 原文，而是把示例整理为可转成 KernelPilot seed 的路线图。

## 示例类别

| 示例 | 可转成的 KernelPilot seed |
|---|---|
| 向量运算 | elementwise / vector add / SIMD smoke test |
| SPMD 矩阵乘 | GEMM scalar 或 SIMD baseline |
| SUMMA 矩阵乘 | 多 SPE 协作 matmul / broadcast 路线 |
| 自定义 atomic | reduction / histogram / conflict update 原型 |
| 加法算子开发 | 最小自定义 op 接入流程 |
| 矩阵乘算子开发 | GEMM K/R/W、性能调优和接口封装 |

## 整理为 seed 的要求

每个示例要进入 KernelPilot，需要补齐：

1. K：device kernel 或 op entry 的最小实现。
2. R：CPU reference 和误差阈值。
3. W：shape、dtype、layout、随机种子和边界 shape。
4. build：`tecocc` 或 CMake 命令。
5. run：correctness、benchmark、perf sampling 命令。
6. ledger：引用相关 SDAAKernelWiki page id。

## 对 GEMM 的连接

GEMM 示例应落到 `kernel-sdaa-gemm` 的实现阶梯：SPMD baseline、SIMD、matmul/ACE、Broadcast、double buffering。PDF 中的示例路线只作为生成顺序，不应直接视作某个 shape 上的最终最佳实现。
