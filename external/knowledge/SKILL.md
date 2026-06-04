---
name: kernel-knowledge
description: "KernelPilot 仓库知识入口，汇总 TECO T1 硬件、性能分析和本地 skill 使用方式。"
type: reference
---

# Kernel Knowledge

这是 KernelPilot 的本地知识入口 skill。

优先阅读以下资料以建立统一分析口径：

- `hardware_model.md`
- `teco-T1.md`
- `指令拍数和流水线派发.md`
- `rms_collect_metrics.analysis.md`
- `skills.md`

## 使用建议

- 当任务涉及 TECO T1 硬件模型、pipe0/pipe1、DMA/RMA、ACE、LDM 等术语时，先参考这里的知识文档。
- 当需要知道当前仓库有哪些本地 skill 以及适用场景时，查看 `skills.md`。
- 当需要执行算子优化循环时，优先使用 `humanize-teco-agent-loop` skill，而不是把本 skill 当成执行流。

## 关键文档

### 硬件与架构
- `hardware_model.md`
- `teco-T1.md`
- `指令拍数和流水线派发.md`

### 性能分析样例
- `rms_collect_metrics.analysis.md`
- `rms_collect_instrument_metrics.pipeline.html`

### Skill 索引
- `skills.md`
