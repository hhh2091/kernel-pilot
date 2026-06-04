---
id: hw-ldm
title: "LDM 本地存储"
type: hardware
architectures: [teco-t1, sdaa]
tags: [ldm, spe]
confidence: source-reported
related: [pattern-ldm-pressure, technique-p0-p1-overlap]
sources: [source-local-hardware-model, source-local-teco-t1, source-local-instruction-latency-pipeline]
aliases: [LDM, "local memory", SPM, "本地存储"]
---

# LDM 本地存储

每个 SPE 有 256 KB LDM，当前可按两个 128 KB bank 理解。不要不经翻译就把它描述为 NVIDIA shared memory；当前分析并没有直接的 shared-memory bank-conflict 指标。

当前静态指令表中，本地 LDM 向量 load/store 延迟如下：

| 操作 | 管线 | 本地 LDM 最小延迟 |
|---|---|---|
| vector load | P1 | 至少 5 cycles |
| vector store | P1 | 至少 4 cycles |
| scalar load | P1 | 至少 5 cycles |
| scalar store | P1 | 至少 3 cycles |

远程 LDM 访问是不定延迟，必须通过 profiler、cycle log 或 PMU 证据确认。

## 对生成的影响

- 尽可能让热数据保留在消费它的 SPE 本地。
- 除非能与 P0 计算重叠，否则避免在 inner loop 中反复产生本地存储流量。
- 将 `local-memory unarb` 和 `local-memory access per instruction` 视为 LDM 压力信号，而不是 bank conflict 的完整证明。
