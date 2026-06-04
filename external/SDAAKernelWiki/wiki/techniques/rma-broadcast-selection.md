---
id: technique-rma-broadcast-selection
title: "RMA 广播模式选择"
type: technique
architectures: [teco-t1, sdaa]
tags: [rma, rma-broadcast-selection, rma-put-preference, double-diagonal-broadcast, strided-column-broadcast]
confidence: source-reported
reproducibility: pseudocode
related: [hw-rma, pattern-rma-contention]
sources: [source-local-teco-t1]
---

# RMA 广播模式选择

本地笔记记录，在某些 size 上 RMA 点对点可能优于行/列广播，且行广播可能没有充分利用 DMA 引擎。双对角线行广播可将每行数据拆给两列，从而使用更多引擎。

## 候选决策树

```text
if 通信是单向 producer -> consumer:
  先尝试 rma_put，再尝试 rma_get
if 数据在同一列内共享:
  尝试 column broadcast
if row broadcast 慢:
  拆分数据并尝试 double-diagonal row broadcast
if column broadcast 落后于 DMA-like access:
  尝试 strided column broadcast，并 sweep bsize
除非已经测量验证，否则避免 DMA_get return 与 RMA broadcast 重叠
```

## 测量项

记录传输 size、source/destination SPE set、route pattern、DMA 是否同时活跃，以及 achieved bandwidth。
