---
id: technique-p0-p1-overlap
title: "通过指令调度实现 P0/P1 重叠"
type: technique
architectures: [teco-t1, sdaa]
tags: [pipe0, pipe1, p0-p1-overlap, static-cycle-estimation, profiler-cross-check]
confidence: inferred
reproducibility: concept
related: [hw-pipe0-pipe1, pattern-scheduling-bubbles, pattern-ldm-pressure]
sources: [source-local-instruction-latency-pipeline, source-local-rms-metrics-analysis, source-local-teco-t1]
---

# 通过指令调度实现 P0/P1 重叠

T1 在依赖允许时支持异步发射和双发射。计算指令多走 P0，访存/控制/DMA/RMA/ACE/sync 多走 P1。算子生成应尝试将独立 P1 工作靠近 P0 计算，而不是形成长 wait 驱动区域。

## 实用启发式

- 将 DMA/RMA issue 提前到消费数据的计算之前。
- 在 DMA issue 和 wait 之间放入依赖允许的 P0 向量计算。
- 在正确性允许时，将 `MEMB` 和 sync 移出 inner loop。
- 对 RMSNorm 类 kernel，不要过度关注低频 `sqrt`；先检查 zero-launch/cannot-launch 和 LDM 流量是否主导。

## 置信度

该技术从 pipe 模型和 RMS 分析综合推断而来。具体重写需要 profiler 或 cycle-log 验证。
