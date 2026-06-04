---
id: kernel-rmsnorm-pmu-analysis
title: "RMSNorm PMU 分析案例"
type: kernel
architectures: [teco-t1, sdaa]
tags: [rmsnorm, pipe0, pipe1, ldm, dma]
confidence: source-reported
kernel_types: [rmsnorm, reduction]
languages: [sdaa-cpp]
related: [pattern-scheduling-bubbles, pattern-ldm-pressure, pattern-dma-hbm-underutilization]
sources: [source-local-rms-metrics-analysis, source-local-instruction-latency-pipeline]
---

# RMSNorm PMU 分析案例

本地 RMS 分析是 SDAA 算子生成的一个有用 seed case。它说明系统不应盲目套用 NVIDIA 风格的 memory-bound 诊断。

## 观测信号

| 信号 | 解释 |
|---|---|
| 32 个 SPE 中 8 个 active | 工作映射只使用了部分 SPA。 |
| 8 个 DMA engine active | 尽管 SPE 只部分激活，DMA 列覆盖已存在。 |
| zero-launch / cannot-launch 偏高 | 调度或 wait 驱动流水可能重要。 |
| local-memory access density | 应检查 LDM 压力。 |
| global-load / DMA request density 低 | 没有典型 DMA/HBM 饱和证据。 |
| icache miss rate 低 | 指令缓存不是第一嫌疑。 |

## 对生成的影响

对 RMSNorm 候选实现：

1. 保留 correctness oracle 和 shape metadata。
2. 先检查 scheduling、wait placement 和 P0/P1 overlap。
3. 追踪 LDM access count 和 reuse。
4. 将 `FSQRTS` 视为长延迟操作，但要验证频率是否足以主导性能。
5. 在声称 HBM 未打满之前，补充 DMA access pattern 字段。
