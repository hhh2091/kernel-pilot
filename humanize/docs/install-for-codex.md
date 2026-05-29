# 为 Codex 安装 Humanize 技能

本指南介绍如何为 Codex CLI 安装 KernelPilot 的 Humanize 套件，包括技能运行时（`$CODEX_HOME/skills`）、外部 KernelWiki / ncu-report-skill 技能，以及原生 Codex `Stop` 钩子（`$CODEX_HOME/hooks.json`）。

## 快速安装（推荐）

从任意位置执行一键安装：

```bash
tmp_dir="$(mktemp -d)" && git clone --recurse-submodules https://github.com/BBuf/kernel-pilot.git "$tmp_dir/kernel-pilot" && "$tmp_dir/kernel-pilot/humanize/scripts/install-skills-codex.sh"
```

从 KernelPilot 仓库根目录执行：

```bash
humanize/scripts/install-skills-codex.sh
```

或直接使用统一安装脚本：

```bash
humanize/scripts/install-skill.sh --target codex
```

该命令将会：
- 将 `humanize`、`humanize-gen-plan`、`humanize-refine-plan`、`humanize-rlcr`、`humanize-kernel-agent-loop`、`KernelWiki` 和 `ncu-report-skill` 同步到 `${CODEX_HOME:-~/.codex}/skills`
- 将运行时依赖复制到 `${CODEX_HOME:-~/.codex}/skills/humanize`
- 在 `${CODEX_HOME:-~/.codex}/hooks.json` 中安装/更新原生 Humanize Stop 钩子
- 当 `codex` 可用时，在 `${CODEX_HOME:-~/.codex}/config.toml` 中启用原生 `hooks` 功能
- 当 `bitlesson_model` 键尚未设置时，向 `~/.config/humanize/config.json` 写入一个 Codex/OpenAI `bitlesson_model`
- 当使用 `--target codex` 时，将该目标的运行时配置标记为 `provider_mode: "codex-only"`，使辅助模型路由保持在该 Codex 安装的 Codex/OpenAI 路径上
- 使用 RLCR 默认配置：`codex exec` 使用 `gpt-5.5:high`，`codex review` 使用 `gpt-5.5:high`

原生钩子功能需要 Codex CLI `0.114.0` 或更新版本。钩子功能已重命名为 `hooks`；仍使用 `codex_hooks` 的旧版 Codex 不受 Codex 安装路径支持。

## 验证

```bash
ls -la "${CODEX_HOME:-$HOME/.codex}/skills"
```

预期目录：
- `humanize`
- `humanize-gen-plan`
- `humanize-refine-plan`
- `humanize-rlcr`
- `humanize-kernel-agent-loop`
- `KernelWiki`
- `ncu-report-skill`

`humanize/` 中的运行时依赖：
- `scripts/`
- `hooks/`
- `prompt-template/`
- `templates/`
- `config/`
- `agents/`

已安装的文件/目录：
- `${CODEX_HOME:-~/.codex}/skills/humanize/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/humanize-gen-plan/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/humanize-refine-plan/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/humanize-rlcr/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/humanize-kernel-agent-loop/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/KernelWiki/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/ncu-report-skill/SKILL.md`
- `${CODEX_HOME:-~/.codex}/skills/humanize/scripts/`
- `${CODEX_HOME:-~/.codex}/skills/humanize/hooks/`
- `${CODEX_HOME:-~/.codex}/skills/humanize/prompt-template/`
- `${CODEX_HOME:-~/.codex}/skills/humanize/templates/`
- `${CODEX_HOME:-~/.codex}/skills/humanize/config/`
- `${CODEX_HOME:-~/.codex}/skills/humanize/agents/`
- `${CODEX_HOME:-~/.codex}/hooks.json`
- `${XDG_CONFIG_HOME:-~/.config}/humanize/config.json`（仅在 Humanize 配置键未设置时创建或更新）

验证原生钩子：

```bash
codex features list | rg '^hooks\s'
sed -n '1,220p' "${CODEX_HOME:-$HOME/.codex}/hooks.json"
```

预期结果：
- `hooks` 出现在 `codex features list` 中
- `hooks.json` 包含 `loop-codex-stop-hook.sh`
- `${XDG_CONFIG_HOME:-~/.config}/humanize/config.json` 中 `bitlesson_model` 设置为 Codex/OpenAI 模型，如 `gpt-5.5`
- 对于 `--target codex`，`${XDG_CONFIG_HOME:-~/.config}/humanize/config.json` 还包含该 Codex 运行时的 `provider_mode: "codex-only"`

## 常用选项

```bash
# 预览但不写入
humanize/scripts/install-skills-codex.sh --dry-run

# 自定义 Codex 技能目录
humanize/scripts/install-skills-codex.sh --codex-skills-dir /custom/codex/skills

# 仅重新安装原生钩子/配置
humanize/scripts/install-codex-hooks.sh
```

## 故障排除

如果已安装的技能中找不到脚本：

```bash
ls -la "${CODEX_HOME:-$HOME/.codex}/skills/humanize/scripts"
```

如果原生退出门控未触发：

```bash
codex features enable hooks
sed -n '1,220p' "${CODEX_HOME:-$HOME/.codex}/hooks.json"
```

如果安装程序报告您的配置或已安装的 Codex 仍在使用 `codex_hooks`，请先升级 Codex，或将 `${CODEX_HOME:-~/.codex}/config.toml` 更改为 `[features]\nhooks = true`。
