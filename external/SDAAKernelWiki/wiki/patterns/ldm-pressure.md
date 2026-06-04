---
id: pattern-ldm-pressure
title: "LDM 与 local-memory 压力"
type: pattern
tags: [ldm]
symptoms: [ldm-pressure]
candidate_techniques: [technique-p0-p1-overlap]
related: [hw-ldm, pattern-scheduling-bubbles]
sources: [source-local-rms-metrics-analysis, source-local-instruction-latency-pipeline, source-local-hardware-model]
---

# LDM 与 local-memory 压力

## 症状

local-memory access per instruction、local-memory unarb cycles 偏高，或 hot loop 中 LDM 向量 load/store 流量密集。

## 可能原因

- 反复从 LDM reload，而不是复用寄存器。
- local layout 不佳，导致仲裁压力。
- store/load 流量没有与 P0 计算重叠。
- 通信路径中隐藏了 remote LDM 访问。

## 候选动作

- 在寄存器压力允许时，将可复用值保留在向量寄存器中。
- 重排 hot loop，使 LDM load/store 与 P0 计算重叠。
- 在 benchmark metadata 中增加每 SPE LDM footprint 和访问计数。
- 除非 SDAA 指标支持，否则不要声称存在 “shared memory bank conflict”。
