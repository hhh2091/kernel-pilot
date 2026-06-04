---
id: technique-dma-periodic-partitioning
title: "跨 SPE 的周期式 DMA 划分"
type: technique
architectures: [teco-t1, sdaa]
tags: [dma, hbm, periodic-partitioning, dma-alignment]
confidence: source-reported
reproducibility: pseudocode
related: [hw-hbm-channel-bank-row, hw-dma, pattern-dma-hbm-underutilization]
sources: [source-local-teco-t1]
---

# 跨 SPE 的周期式 DMA 划分

核心思想是从完整 SPA 视角看访存。单个 SPE 的块可以是连续的，但 32 个 SPE 合起来的访问可能稀疏或不利于 row locality。周期式划分让每个 SPE 访问跨步 chunk，使聚合访问覆盖 HBM channel 和 bank。

## 伪代码

```text
for spe in 0..31:
  for chunk in assigned_chunks:
    global_offset = base + (chunk * 32 + spe) * block_bytes
    dma_get(ldm_ptr + chunk * block_bytes, global_ptr + global_offset, block_bytes)
```

`block_bytes` 应按 128B 对齐。可行时验证 2KB group 上的聚合覆盖。

## 测量项

采集：

- base address alignment
- per-SPE bytes
- 每个 phase 的 aggregate SPA bytes
- DMA request count 和 queue depth
- runtime bandwidth 与 PMU DMA counters
