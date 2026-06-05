---
id: technique-sdaa-perf-sampling
title: "SDAA 设备端性能采样"
type: technique
architectures: [sdaa, teco-t1]
tags: [perf-sampling, profiler-cross-check]
confidence: verified
reproducibility: api-contract
related: [pattern-scheduling-bubbles, pattern-ldm-pressure, pattern-ace-feeding-writeback]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-rms-metrics-analysis]
---

# SDAA 设备端性能采样

SDAA C 在 `sdaa_perf.h` 中提供设备端性能采样接口。它适合在 KernelPilot attempt 内标记一个候选实现的热区，并与外部 profiler / optest 指标交叉验证。

## 核心接口

常用接口包括：

- `perf_start`
- `perf_stop`
- `perf_print`
- `clock`
- `PerfData`

指南中的接口用于采样目标代码段的性能数据。当前生成流程应至少把 cycle 作为稳定字段记录；其他字段需要结合实际 runtime / profiler 输出确认。

## KernelPilot 用法

1. 在 benchmark harness 中保留端到端 wall time。
2. 在 device hot loop 周围插入 perf start/stop，只测 kernel 内关键阶段。
3. 对 DMA/RMA/matmul 版本，分别标记 load、compute、store、wait 区段。
4. 在 attempt ledger 中记录 perf 区段名、shape、SPE 数、SPM 字节和 page id。
5. 如果 perf sampling 与外部 PMU 结论冲突，以可复现 microbenchmark 继续缩小范围。

## 不足

- 指南提供 API 入口，但没有给出完整 profiler schema。
- `zero-launch`、`cannot-launch`、DMA/RMA/ACE counter 的字段定义仍需从 optest / SDPTI / PMU 输出中补齐。
- 采样代码本身会引入扰动；只应用于阶段对比，不应替代端到端 benchmark。
