---
id: source-local-ace-cost-table
title: "ACE.xlsx cost model 表"
source_category: empirical-table
path: external/knowledge/ACE.xlsx
captured_at: 2026-06-04
tags: [ace]
---

# ACE.xlsx cost model 表

本地来源摘要：

`ACE.xlsx` 包含经验或模型化的 ACE 表：

- `TFLOPS`：按 `m`、`k` 组织的吞吐表。
- `Cycle`：按 `m`、`k` 组织的 cycle 表。
- `IO_AB`：A/B feeding 带宽或代价表。
- `IO_C`：C 输出带宽或代价表。
- `write half`：writeback 相关表。
- `下发_delay`：按 `m`、`k` 组织的 issue/dispatch delay 表。

该文件适合作为 ACE shape 选择和 roofline 检查的 cost-model 输入。不要把它当成某个具体 kernel run 的 PMU 数据。
