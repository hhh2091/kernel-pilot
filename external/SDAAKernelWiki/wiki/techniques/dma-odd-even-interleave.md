---
id: technique-dma-odd-even-interleave
title: "DMA 奇偶引擎交错"
type: technique
architectures: [teco-t1, sdaa]
tags: [dma, dma-odd-even-interleave, hbm]
confidence: source-reported
reproducibility: pseudocode
related: [hw-dma, pattern-dma-hbm-underutilization]
sources: [source-local-teco-t1]
---

# DMA 奇偶引擎交错

本地 T1 笔记记录，将 DMA 引擎顺序设置为 `(0, 2, 4, 6, 1, 3, 5, 7)`，在某种高带宽 DMA 模式下可以避免交叉开关流量冲突。

## 伪代码

```text
logical_col_to_dma_engine = [0, 2, 4, 6, 1, 3, 5, 7]
engine = logical_col_to_dma_engine[spe_col]
```

把它作为候选映射，而不是普适规则。目标 shape 下需要与自然列顺序 benchmark 对比。

## 测量项

在相同 128B 对齐和队列深度下，对比自然顺序与奇偶顺序的 bandwidth、DMA wait 和总 kernel time。
