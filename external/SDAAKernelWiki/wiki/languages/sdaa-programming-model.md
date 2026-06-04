---
id: lang-sdaa-programming-model
title: "SDAA 编程模型笔记"
type: language
architectures: [teco-t1, sdaa]
tags: [spa, spe, ldm, dma, rma, ace]
confidence: source-reported
reproducibility: concept
languages: [sdaa-cpp, tecocc]
related: [hw-spa-spe, hw-dma, hw-rma, hw-ace]
sources: [source-local-teco-t1]
---

# SDAA 编程模型笔记

当前本地笔记描述：

- `threadIdx`：SPE ID。
- `threadDim`：SPA 中 SPE 的数量。
- `__global__`：kernel 定义。
- `kernel<<<1>>>(args)`：笔记中记录的一种 launch 形式。
- `__device__`：device-side 函数标记。
- `__local__`：类似 SPM/LDM 的 local storage 标记。
- `sync_threads()`：SPA 级同步，另有面向指定 SPE group 的变体。
- 数据搬运包括 host/device copy、same-core movement、DMA、RMA，以及行/列/自定义 SPE group 广播。

该页面目前还不足以支撑代码生成，因为精确头文件、函数签名、类型约束、编译器参数和示例仍缺失。见 `docs/gap-analysis.md`。
