---
id: technique-sdaa-matmul-api
title: "SDAA MatMul 接口与 ACE 生成约束"
type: technique
architectures: [sdaa, teco-t1]
tags: [ace, spm, simd-vectorization, p0-p1-overlap]
confidence: verified
reproducibility: api-contract
related: [hw-ace, technique-ace-double-buffering, pattern-ace-feeding-writeback, kernel-sdaa-gemm]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-ace-cost-table]
---

# SDAA MatMul 接口与 ACE 生成约束

SDAA C 在 `sdaa_matmul.h` / `sdaa` namespace 下提供矩阵乘接口。KernelPilot 生成 GEMM 或 matmul kernel 时，应优先把它视为 ACE / 矩阵单元路径，而不是手写 scalar FMA 的终点。

## 阻塞接口

核心形式：

```text
matmul(type, output, input, weight, m, k, n)
```

语义为 `output[m,n] = input[m,k] * weight[k,n]`。支持 Global 与 SPM 矩阵，支持 in-place，阻塞接口对 `m/k/n` 没有固定枚举上限。

支持的数据类型：

| 类型 | 输入 | 输出 |
|---|---|---|
| `MatmulHalfToHalf` | half | half |
| `MatmulHalfToFloat` | half | float |
| `MatmulShortToShort` | short | short |
| `MatmulShortToInt` | short | int |

生成约束：

- Global 矩阵基址需要 4B 对齐，矩阵字节数需要是 4B 的倍数。
- 对 SPM 矩阵，如果 `k == 32 && n == 32` 且矩阵是 output/input，基址需要 64B 对齐。
- 对 SPM input，如果 `k % 32 == 0`，基址需要 64B 对齐。
- 当任一矩阵位于 Global，或 `n <= 32` 且 output 与 input/weight overlap 时，接口可能使用额外 SPM heap。
- 生成代码应在开发版中调用 `check_matmul`，把参数错误和性能问题分开。

## 非阻塞接口

非阻塞路径暴露 load/compute/store/wait 阶段：

```text
matmul_init(handle, type)
matmul_load_weight(handle, weight, MatmulK32, MatmulN32, stride)
matmul_compute(handle, input, m, MatmulK32, stride)
matmul_store(handle, output, m, MatmulN32)
matmul_wait(handle)
```

重要约束：

- `weight`、`input`、`output` 都应位于 SPM。
- `matmul_compute` 和 `matmul_store` 中的 `m` 合法范围是 `1..128`。
- 当前 K 枚举以 `MatmulK32` 为主，N 枚举以 `MatmulN32` 为主。
- `stride` 单位按接口约定为 64B。
- 可用配置包括 weight row padding、updating weight、output row offset、flushing output，以及等待 weight/input 装载的接口。

## 对 GEMM 生成的影响

1. baseline 可以从 scalar SPMD 或 SIMD 开始，但最终应评估 matmul 非阻塞路径。
2. K 维 tile 应优先围绕 32 对齐设计，避免在热路径上产生边界处理。
3. A/B tile 进入 SPM 后，再调用非阻塞 matmul；Global 直连阻塞 matmul更适合正确性原型，不适合最终高性能路径。
4. 非阻塞接口的价值在于把 load/compute/store 与 DMA、broadcast、SIMD epilogue 交错。
5. 每一轮优化都需要记录 tile shape、SPM 字节、对齐、extra heap 风险和 wait 放置。

## 测量项

- kernel 总时间、有效 TFLOPS、正确性误差。
- SPM 使用量和是否触及 malloc 上限。
- ACE 或 matmul 相关 cycle / stall / writeback 计数；没有官方计数时，至少记录 perf sampling cycle 和端到端时间。
- 与 `source-local-ace-cost-table` 的预测差异。
