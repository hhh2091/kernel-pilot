---
id: source-local-hardware-model
title: "optest-agent 硬件模型笔记"
source_category: local-note
path: external/knowledge/hardware_model.md
captured_at: 2026-06-04
tags: [spa, spe, ldm, dma, rma, ace, pipe0, pipe1]
---

# optest-agent 硬件模型笔记

本地来源摘要：

- T1 包含 4 个 SPA 核组。每个 SPA 独占 16 GB HBM。
- 单 SPA 分析口径使用 32 个 SPE，排布为 4 x 8。
- SPE 主频当前按 2.5 GHz 建模。ACE 当前按 1.25 GHz 建模。
- 当前执行模型描述为 2 译码、2 发射、2 写回；pipe0 偏计算，pipe1 偏访存/控制/DMA/RMA/ACE/sync。
- 每个 SPE 有 256 KB LDM，可理解为两个 128 KB bank。
- DMA 引擎按列绑定：每个 SPA 有 8 个 DMA 引擎，每列 4 个 SPE 共享一个。
- PMU 前缀有硬件含义：`slave__*`、`alu__*`、`fpu__*`、`vpu__*`、`lsu__*`、`dma__*`、`rma__*`、`l0ic__*`、`l1ic__*`。
- `SM`、`warp`、`shared-memory bank conflict`、`occupancy`、`L1TEX` 等 NVIDIA 术语不应直接用于 SDAA，需要翻译到本硬件口径。
