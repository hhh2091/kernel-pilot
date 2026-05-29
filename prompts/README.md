# KernelPilot 提示词

这些是用于 KernelPilot 内核优化循环的端到端提示词卡片。
它们遵循
[kernel-design-agents 提示词风格](https://github.com/mit-han-lab/kernel-design-agents/tree/main/prompts)
的清晰性，但将工作压缩为每个任务一个提示词，而不是分阶段的提示词。FA4 卡片源自
[KernelPilot issue #1](https://github.com/BBuf/kernel-pilot/issues/1)。

| 提示词 | 目标 |
| --- | --- |
| [B200 int8_scaled_mm](b200-int8-scaled-mm.md) | 在 B200 上针对一个聚焦形状优化 SGLang `int8_scaled_mm`，目标是相比 SGLang 基线至少实现 2.5 倍加速。 |
| [B200 FA4 MHA](b200-fa4-mha.md) | 构建一个独立的 BF16 纯前向 MHA 内核，在配置的 B200 用例上以至少 5% 的几何平均 TFLOPS 击败官方 FlashAttention-4。 |

每个提示词旨在作为一个完整的任务粘贴使用。提示词本身指定了所需的远程 GPU 技能和验收目标。

## Codex Goal 变体

这些变体保留了原始任务目标，但将其表达为 Codex
`/goal` 完成契约，而不是 Humanize 内核代理循环提示词。

| 提示词 | 目标 |
| --- | --- |
| [B200 int8_scaled_mm Codex Goal](b200-int8-scaled-mm-codex-goal.md) | 在 B200 上针对一个聚焦形状优化 SGLang `int8_scaled_mm`，目标是相比 SGLang 基线至少实现 2.5 倍加速。 |
| [B200 FA4 MHA Codex Goal](b200-fa4-mha-codex-goal.md) | 构建一个独立的 BF16 纯前向 MHA 内核，在配置的 B200 用例上以至少 5% 的几何平均 TFLOPS 击败官方 FlashAttention-4。 |

## 推荐的 Claude Code 启动方式

使用 Opus、最大推理努力度以及绕过权限提示的方式启动 Claude Code，然后再粘贴这些端到端提示词卡片之一：

```bash
claude --permission-mode bypassPermissions --model opus --effort max
```

## Opus 4.7 B200 int8_scaled_mm 运行

下图来自使用
[B200 int8_scaled_mm](b200-int8-scaled-mm.md) 提示词的 Opus 4.7 模型运行。

[![Opus 4.7 B200 int8_scaled_mm 优化结果](https://raw.githubusercontent.com/BBuf/kernel-pilot/main/prompts/opus47-b200-int8-scaled-mm-result.png)](https://raw.githubusercontent.com/BBuf/kernel-pilot/main/prompts/opus47-b200-int8-scaled-mm-result.png)
