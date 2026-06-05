---
id: technique-sdaa-simd-vectorization
title: "SDAA SIMD 向量化"
type: technique
architectures: [sdaa, teco-t1]
tags: [simd, simd-vectorization, p0-p1-overlap]
confidence: verified
reproducibility: api-contract
related: [hw-pipe0-pipe1, technique-p0-p1-overlap, kernel-sdaa-gemm]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-instruction-latency-pipeline]
---

# SDAA SIMD 向量化

SDAA C 提供显式向量类型与 SIMD intrinsic。适合 elementwise、reduction 局部累加、GEMM baseline、epilogue 和数据转换阶段。

## 向量类型

常用类型包括：

| 类型 | 典型用途 |
|---|---|
| `intv16` / `uintv16` | 16 lane int / uint 操作 |
| `shortv32` / `ushortv32` | 32 lane short / ushort 操作 |
| `halfv16` | half 向量运算 |
| `floatv16` | float 向量运算与累加 |

## API 家族

指南列出的 SIMD 能力覆盖：

- load/store：`simd_load`、`simd_store`、`simd_loadu`、`simd_storeu`。
- 数据变换：widen、narrow、set、stretch、concat、insert、type convert。
- 选择与比较：compare、select、max/min、logical / bitwise。
- 算术：add、sub、mul、div、rem、fabs、FMA/FMS/FNMA/FNMS。
- reduction：`simd_redsum`。

## 生成规则

1. 先确认数据在 lane 间独立；跨 lane 依赖应显式使用 reduction 或 shuffle 风格接口。
2. 对齐已知时优先 aligned load/store；边界处理单独拆出 tail path。
3. 对 GEMM baseline，SIMD 只应作为过渡路径；大规模矩阵乘应进一步迁移到 matmul / ACE 路径。
4. 对 RMSNorm / layernorm，SIMD reduction 后仍需检查 sqrt/div 长延迟是否主导。
5. SIMD 循环应与 DMA/RMA wait、SPM staging 和 P0/P1 issue pattern 一起测量，避免只看静态指令数。

## 验证项

- scalar reference 对比误差。
- 向量宽度、tail 处理、数据类型转换是否覆盖所有 shape。
- perf sampling cycle、P0/P1 空泡、local memory access density。
