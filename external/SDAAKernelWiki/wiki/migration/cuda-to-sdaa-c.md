---
id: migration-cuda-to-sdaa-c
title: "CUDA 到 SDAA C 迁移规则"
type: migration
architectures: [sdaa, teco-t1]
tags: [cuda-migration, sdaa-c, spa, spe, spm]
confidence: verified
reproducibility: concept
related: [lang-sdaa-c-programming-guide, hw-spa-spe, hw-sdaa-memory-model]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# CUDA 到 SDAA C 迁移规则

SDAA C 不是 CUDA 语法的逐项替换。KernelPilot 从 NVIDIA KernelWiki 或 CUDA kernel 迁移规则时，必须先翻译到 SPA/SPE/SPM/DMA/RMA/ACE 模型。

## 线程与 launch

| CUDA 概念 | SDAA C 处理 |
|---|---|
| grid / block / thread | 重新设计为 SPA 内 SPE 并行与 host 侧任务划分。 |
| `threadIdx` | SDAA C 的 `threadIdx` 表示当前 SPE ID。 |
| `blockIdx` / blockId | 没有直接等价物；应转成数据分片、kernel 参数或 host 调度。 |
| warp | SDAA C 没有对应 Warp 概念；不要迁移 warp-level intrinsic。 |
| `__shared__` | 根据语义映射到 SPM local storage 或 Global memory staging。 |

## 内存迁移

- CUDA shared memory bank conflict 不能直接套用到 SDAA；应分析 SPM / LDM bank、local-memory access 与 DMA/RMA 行为。
- CUDA global memory coalescing 需要翻译成 SDAA DMA 128B 包、2KB 聚合访问、HBM channel-bank-row 规则。
- CUDA block 内共享数据在 SDAA 上通常变成 SPE 间 RMA/Broadcast 或每 SPE SPM 副本。

## 代码生成注意事项

1. 先写 SDAA K/R/W，不要从 CUDA launch geometry 机械推导。
2. 用 `threadIdx` / `threadDim` 表达 SPA 内并行。
3. 需要跨 SPE 通信时显式选择 RMA、Broadcast 或 Global staging。
4. CUDA warp reduction 应重写成 SIMD lane reduction + SPE group reduction。
5. 每个迁移候选都要记录替换依据和无法保留的 CUDA 假设。
