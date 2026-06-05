---
id: kernel-sdaa-gemm
title: "SDAA GEMM 优化生成路线"
type: kernel
architectures: [sdaa, teco-t1]
tags: [gemm, matmul, ace, simd-vectorization, dma, broadcast, spm]
confidence: source-reported
kernel_types: [gemm, matmul]
languages: [sdaa-c, sdaa-cpp, tecocc]
related: [technique-sdaa-matmul-api, technique-sdaa-simd-vectorization, technique-sdaa-dma-api, technique-sdaa-rma-broadcast-api, technique-ace-double-buffering]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-ace-cost-table, source-local-teco-t1]
---

# SDAA GEMM 优化生成路线

SDAA C 编程指南把 GEMM 作为算子开发示例，优化路线包含 baseline、SIMD、矩阵乘单元、Broadcast 和 double buffering。KernelPilot 面向 TECO_AICARD_01 / T1 生成 GEMM 时，应把这条路线转成可逐轮验证的候选序列。

## K/R/W 契约

- K：`C = A x B`，明确 dtype、layout、M/N/K、alpha/beta、是否支持 transpose、误差阈值。
- R：host reference 或高精度 CPU reference；half 输入时至少用 float accumulation reference 检查。
- W：覆盖 square、skinny、small-K、large-K、非 32 对齐边界、batch 或多 shape 列表。

## 实现阶梯

| 阶段 | 目的 | 何时继续 |
|---|---|---|
| SPMD scalar baseline | 建立正确性、launch、数据搬运和边界处理 | 正确但性能低时转 SIMD |
| SIMD baseline | 验证 lane 并行、tail、epilogue | 计算主导或静态 FMA 密集时转 matmul |
| matmul / ACE | 使用 SDAA 矩阵单元 | tile 已进入 SPM，K/N 可围绕 32 对齐 |
| Broadcast | 减少 B tile 或共享 tile 的重复搬运 | 多 SPE 使用同一 tile 且 RMA 点对点过重 |
| Double buffering | 重叠 DMA/Broadcast、matmul compute、writeback | wait 或 writeback 暴露在时间线上 |

## 首选 tile 规则

1. 优先让 K tile 以 32 为核心粒度，匹配 `MatmulK32`。
2. B / weight tile 进入 SPM 后使用 `matmul_load_weight`。
3. A / input tile 进入 SPM 后使用 `matmul_compute`，`m` 控制在接口合法范围内。
4. 输出 tile 通过 `matmul_store` 回到 SPM，再用 DMA 写回 Global。
5. 边界 tile 单独处理，不要污染主路径的对齐和 stride。

## 数据搬运与通信

- Global <-> SPM 用 DMA；同一 SPA 的 SPE 间 SPM 传递用 RMA 或 Broadcast。
- B tile 在多个 SPE 间复用时优先评估 Broadcast，而不是每个 SPE 独立 DMA。
- 使用 double buffering 时，至少维护 load buffer、compute buffer、store buffer 的状态机，避免覆盖未完成数据。
- DMA/RMA/Broadcast 的 wait 位置应与 matmul 非阻塞阶段交错。

## 必测指标

- 端到端时间、有效 TFLOPS、带宽估算、正确性误差。
- tile shape、SPM 使用、alignment、DMA 请求数、Broadcast/RMA 次数。
- perf sampling 中 load/compute/store/wait 分段 cycle。
- 与 ACE cost table 的理论差距；差距过大时先查 feeding/writeback，而不是直接增加 unroll。

## 生成 fallback

- 如果 matmul 非阻塞接口受 shape 或对齐限制，退回阻塞 `matmul` 验证语义，再拆分 tile。
- 如果 K/N tail 复杂，主路径只覆盖对齐部分，tail 用 SIMD 或 scalar。
- 如果 Broadcast 引入 RMA 竞争，退回每列 DMA 或更小 thread group。
