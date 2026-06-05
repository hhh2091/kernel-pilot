---
id: technique-sdaa-math-and-high-level-api
title: "SDAA 数学函数与高层接口"
type: technique
architectures: [sdaa, teco-t1]
tags: [math-functions, high-level-api, simd-vectorization]
confidence: verified
reproducibility: api-contract
kernel_types: [elementwise, reduction]
languages: [sdaa-c]
related: [technique-sdaa-simd-vectorization, pattern-scheduling-bubbles]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA 数学函数与高层接口

PDF 第 8 章覆盖数学函数，第 9 章覆盖高层次函数接口，第 13 章把数学函数和向量操作纳入性能调优主题。

## 数学函数范围

指南将数学函数分为：

- 单精度数学接口。
- 双精度数学接口。
- 向量数学接口。

生成代码时，需要按 dtype 明确选择标量、向量或高层接口。不要把 CUDA libdevice 函数名直接迁移到 SDAA C。

## 高层接口范围

高层次函数接口覆盖：

- batch math。
- activation。
- reduction。

这些接口适合用于快速建立 correctness prototype 或替代手写复杂数学路径。最终性能版本仍需和 SIMD、SPMD、DMA/RMA、matmul 等底层路径对比。

## 生成规则

1. 对 elementwise activation，先确认是否存在高层接口，再决定是否手写 SIMD。
2. 对 reduction，优先组合 SIMD reduction 和 SPE group reduction；高层接口可作为 baseline。
3. 对 sqrt/div 等长延迟数学操作，必须用 perf sampling 或外部 PMU 验证频率与占比。
4. 对 GEMM epilogue，如 bias、activation、scaling，优先在 matmul store 后用 SIMD 或高层接口处理。

## 测量项

- 数学函数调用次数、dtype、向量化比例。
- P0/P1 空泡、长延迟指令占比、端到端收益。
- 高层接口与手写 SIMD 的正确性和性能差异。
