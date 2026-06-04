---
id: pattern-ace-feeding-writeback
title: "ACE Feeding 与 Writeback 瓶颈"
type: pattern
tags: [ace, ldm]
symptoms: [ace-feeding-stall]
candidate_techniques: [technique-ace-double-buffering]
related: [hw-ace]
sources: [source-local-teco-t1, source-local-ace-cost-table]
---

# ACE Feeding 与 Writeback 瓶颈

## 症状

ACE matmul 或 GEMM-like kernel 低于 cost-table roofline；或减少 compute tile 数后耗时没有改善。

## 可能原因

- west/north feeding 不均衡。
- accumulator writeback 与 compute 串行。
- tile shape 不适合 ACE 表。
- 小 shape 下 dispatch delay 占主导。

## 候选动作

- 用 ACE cost table 选择候选 `(m, k)` shape。
- 使用 ACE 累加器双缓冲重叠 compute 和 writeback。
- 在 microbenchmark 中拆分 feeding、compute 和 writeback 计时。
- 可用后补充真实 ACE profiler counter。
