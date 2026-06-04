---
id: pattern-scheduling-bubbles
title: "调度空泡与发射停顿"
type: pattern
tags: [pipe0, pipe1]
symptoms: [scheduling-bubbles]
candidate_techniques: [technique-p0-p1-overlap, technique-dma-queue-budgeting]
related: [hw-pipe0-pipe1, kernel-rmsnorm-pmu-analysis]
sources: [source-local-rms-metrics-analysis, source-local-instruction-latency-pipeline]
---

# 调度空泡与发射停顿

## 症状

zero-launch、launch-zero-latency 或 cannot-launch counter 偏高。在 RMS 分析样例中，这是最强信号。

## 可能原因

- wait 驱动的流水结构。
- P0/P1 不均衡，或依赖阻止双发射。
- 热路径中存在 sync 或 `MEMB`。
- DMA/RMA/ACE issue 与 wait 放置不合理，中间缺少足够独立工作。

## 候选动作

1. 检查 hot loop 的指令结构。
2. 尝试 P0/P1 overlap，把独立计算移动到 memory issue 和 wait 之间。
3. 减少过度 sync/barrier。
4. 改内存布局前先重新 profile；调度可能才是主问题。
