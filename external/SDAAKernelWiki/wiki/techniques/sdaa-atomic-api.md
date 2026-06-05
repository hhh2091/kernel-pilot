---
id: technique-sdaa-atomic-api
title: "SDAA Atomic 接口与生成约束"
type: technique
architectures: [sdaa, teco-t1]
tags: [atomics, global-memory, spm]
confidence: verified
reproducibility: api-contract
kernel_types: [atomic, reduction]
languages: [sdaa-c]
related: [kernel-sdaa-gemm, technique-sdaa-simd-vectorization]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA Atomic 接口与生成约束

PDF 第 7 章列出 SDAA C atomic 接口，第 13 章将 atomic 作为性能调优主题，第 15 章包含自定义 atomic 示例。

## API 家族

指南列出的 atomic 能力包括：

- `atomic_inc`
- `atomic_add`
- `atomic_add_noret`
- `atomic_sub`
- `atomic_sub_noret`
- `atomic_cas`
- `atomic_cas_bool`

## 生成规则

1. reduction 首选分层规约：SIMD lane 内规约、SPE 内 SPM 规约、SPE group 规约；atomic 作为跨分片合并 fallback。
2. 如果 atomic 返回值未使用，优先选择 no-return 版本，减少不必要依赖。
3. 高争用地址应避免所有 SPE 同时 atomic；改用分桶或分阶段 merge。
4. 用 atomic 实现 correctness 原型后，必须通过 profiler 或 benchmark 判断是否成为瓶颈。

## 测量项

- atomic 调用次数和目标地址分布。
- SPE 并发度、热点 bucket、端到端时间。
- 与无 atomic 的两阶段 reduction 对比。
