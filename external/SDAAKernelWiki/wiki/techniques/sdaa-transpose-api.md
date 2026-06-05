---
id: technique-sdaa-transpose-api
title: "SDAA Transpose 接口"
type: technique
architectures: [sdaa, teco-t1]
tags: [transpose, spm, dma]
confidence: verified
reproducibility: api-contract
kernel_types: [transpose]
languages: [sdaa-c]
related: [technique-sdaa-dma-api, hw-sdaa-memory-model]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA Transpose 接口

PDF 第 7 章提供 transpose 接口。对 GEMM、layout transform 和 epilogue 生成来说，transpose 应作为专门数据布局阶段，而不是混在主 compute loop 中。

## API 家族

指南列出的 transpose 能力包括：

- `transpose`
- `TransposeHandle`
- `transpose_async`
- `transpose_wait`
- `check_transpose_async`

## 生成规则

1. 开发版使用 `check_transpose_async` 验证参数，把非法 shape 与性能问题分开。
2. 异步 transpose 应与 DMA 或 matmul 阶段建立清晰依赖，wait 放置必须可读。
3. 对 GEMM B 矩阵预处理，如果 layout 重排可复用多次，应考虑单独 kernel 或 host-side preprocessing。
4. 对一次性小 shape，transpose 开销可能超过收益，应保留 no-transpose fallback。

## 测量项

- transpose 前后主 loop 的 DMA 连续性和 matmul tile 对齐。
- transpose 自身 cycle、SPM 使用、端到端收益。
