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

PDF 第 8 章覆盖数学函数（单精度/双精度/向量），第 9 章覆盖高层次函数接口，第 13 章给出完整性能数据。

## 数学函数总览

所有数学函数内置，无需 `#include`。均支持 in-place。

### 函数精度-性能对照表

| 函数 | 单精度 ULP | 双精度 ULP | 标量 cycles | 向量 cycles | 128-wide cycles |
|------|-----------|-----------|------------|------------|----------------|
| `exp` | 1 | 149 | 158/151 | 205 | 523–1214 |
| `expm1` | 1 | 1 | 352/330 | — | — |
| `log` | 4 | 4 | 188/218 | 218 | 1145 |
| `log1p` | 1 | 1 | 356/334 | — | — |
| `log2` | 5 | 6 | 166/217 | 197 | 1146 |
| `sqrt` | 0 | 0 | 31/45 | 98 | — |
| `1/x` | 0 | 0 | 32/47 | 69 | 176 |
| `fabs` | 0 | 0 | 14/14 | — | — |
| `pow` | 3 | 1 | 1602/1579 | — | — |
| `tanh` | 2 | 3 | 251/761 | 251 | 635 |
| `sigmoid` | 3¹ | 124¹ | 205/219 | 204 | 506 |
| `erf` | 1 | 1 | 206-1103/184-1079 | 253 | 1083 |
| `sin` | 1 | 1 | TBD | 140 | 473 |
| `cos` | 1 | 1 | TBD | 278 | 1774 |
| `atan` | 2 | 2 | 214/208 | 148 | 523 |
| `ceil` | 0 | 0 | 99/77 | — | — |
| `floor` | 0 | 0 | 95/73 | 57 | 205 |
| `round` | 0 | 0 | 99/72 | 53 | 131 |
| `trunc` | 0 | 0 | — | 47 | 121 |
| `fma` | 0 | 0 | 39/54 | — | — |
| `fmax`/`fmin` | 0 | 0 | 124/101 | — | — |
| `isnan` | 0 | 0 | 351/351 | — | — |

¹ sigmoid: ULP 指 (-10, 10) 范围内；范围外为 absolute error ≤ 5e-5。

### 128-wide 接口（in-place, 64B 对齐）

`simd_exp128`, `simd_log128`, `simd_tanh128`, `simd_sigmoid128`, `simd_sqrt128`(via simd_sqrt only), `simd_inv128`(via simd_vinv128)，`simd_sin128`, `simd_cos128`, `simd_atan128`, `simd_erf128`, `simd_log2_128`, `simd_round128`, `simd_trunc128`, `simd_floor128`

均处理 128 个 float，要求 **64B 对齐**，in-place 操作。

### 关键性能发现

- 标量→向量(16-wide)→128-wide 性能递增：`expf` 154 → `simd_exp` 12.7 → `simd_exp128` 6.9 beats/element（约 **22x** vs 标量）
- `simd_div`(1723) 和 `pow`(1602) 是最昂贵的数学操作
- `simd_fabs`(3) 和 `simd_redsum`(3) 是最便宜的操作

## 高层接口

需 `#include <scl.h>` 和 `sdaa::scl` 命名空间。全部返回 `void`。

### Batch Math（模板函数）

| 接口 | 操作 | 支持类型 |
|------|------|---------|
| `batch_tanh(dst, src, len)` | tanh | float, half |
| `batch_sin(dst, src, len)` | sin | float, half |
| `batch_cos(dst, src, len)` | cos | float, half |
| `batch_log(dst, src, len)` | ln | float, half |
| `batch_pow(dst, src1, src2, len)` | x^y | float, half |
| `batch_floor(dst, src, len)` | floor | float, half |
| `batch_ceil(dst, src, len)` | ceil | float, half |
| `batch_axpy(dst, src1, src2, alpha, len)` | ax+y | float, half |
| `batch_exp(dst, src, len)` | e^x | float, half |
| `batch_xor(dst, src1, src2, len)` | 位异或 | int, short |

### Activation

| 接口 | 操作 |
|------|------|
| `batch_gelu(dst, src, len)` | GELU: 0.5x(1+tanh(√(2/π)(x+0.044715x³))) |
| `batch_sigmoid(dst, src, len)` | sigmoid |

### Reduction

| 接口 | 操作 |
|------|------|
| `sum(dst, src, len)` | 求和，结果写入 dst[0] |

## 生成规则

1. elementwise activation 先确认高层接口是否存在，再决定手写 SIMD。
2. reduction 优先组合 SIMD reduction + SPE group reduction；高层接口做 baseline。
3. sqrt/div 等长延迟操作用 perf sampling 验证频率与占比。
4. GEMM epilogue（bias、activation、scaling）优先在 matmul store 后用 SIMD 或高层接口。
5. 对大规模单精度数组，优先用 128-wide 向量接口（~22x vs 标量）。
