---
id: source-local-rms-metrics-analysis
title: "RMS metrics 分析报告"
source_category: local-analysis
path: external/knowledge/rms_collect_metrics.analysis.md
captured_at: 2026-06-04
tags: [rmsnorm, scheduling-bubbles, ldm, dma, icache]
---

# RMS metrics 分析报告

本地来源摘要：

- 采样的 RMS demo 激活了 32 个 SPE 中的 8 个，但使用到了全部 8 个 DMA 引擎。
- 最强信号是调度/发射压力：zero-launch 与 cannot-launch counter 偏高。
- 存在 LDM/local-memory 压力，但尚不能证明它是唯一瓶颈。
- 样例不像典型 HBM/DMA 饱和：global load 和 DMA request 密度较低。
- 指令缓存 miss rate 较低。
- 对端到端性能而言，runtime/driver API 开销相对 kernel duration 不可忽略。
- 缺失字段包括 DMA stride/access pattern、concurrent DMA queue depth 和 RMA/broadcast mode。
