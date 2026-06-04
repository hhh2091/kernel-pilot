---
id: source-local-instruction-latency-pipeline
title: "指令拍数与流水线派发笔记"
source_category: local-note
path: external/knowledge/指令拍数和流水线派发.md
captured_at: 2026-06-04
tags: [pipe0, pipe1, simd, ldm, dma, rma, ace]
---

# 指令拍数与流水线派发笔记

本地来源摘要：

- 静态拍数表只适合判断热点方向。DMA、RMA、global memory、remote LDM、sync 和 ACE 的延迟必须结合运行时证据。
- P0 是主要计算管线。当前表中 `VFMULS`、`VADDS`、`VMAS` 等向量浮点操作约 5 拍。
- P1 是主要访存/控制管线。当前表中本地 LDM 向量 load 至少 5 拍，store 至少 4 拍。
- `FSQRTS` 和 `FDIVS` 是长延迟且非完全流水；它们共享子部件，RMSNorm 类 kernel 需要特殊关注。
- `MEMB` 会阻塞后续发射直到完成。`SYNC/SYNR/SYNP` 是不定延迟。
- 静态发现应从 `possible` 置信级别开始，只有 profiler 或 cycle 证据支持后才能升级为 `likely` 或 `confirmed`。
