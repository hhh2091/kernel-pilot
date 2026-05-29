# 为 Claude Code 安装 KernelPilot Humanize

## 前提条件

- [codex](https://github.com/openai/codex) -- OpenAI Codex CLI（用于代码审查）。使用 `codex --version` 验证。
- `jq` -- JSON 处理器。使用 `jq --version` 验证。
- `git` -- Git 版本控制。使用 `git --version` 验证。

## 方式一：KernelPilot 市场安装（推荐）

克隆 KernelPilot 及其外部技能子模块，将仓库根目录添加为 Claude Code 市场，安装 Humanize 插件，并暴露 KernelWiki / ncu-report-skill 技能：

```bash
git clone --recurse-submodules https://github.com/BBuf/kernel-pilot.git
cd kernel-pilot

humanize/scripts/install-skills-claude.sh
```

对于已有的克隆仓库，请先初始化子模块：

```bash
git submodule update --init --recursive
```

安装脚本会执行市场安装、链接 `KernelWiki` 和 `ncu-report-skill`、安装 KernelWiki 查询依赖项，并使用绝对路径 `HUMANIZE_RUNTIME_ROOT`、`KERNELPILOT_ROOT`、`KERNELWIKI_ROOT` 和 `NCU_REPORT_SKILL_ROOT` 填充 Claude Code 的已安装技能缓存；如果存在任何未替换的占位符，脚本将会报错。手动更新插件后也请使用该安装脚本，因为 Claude Code 在 `plugin install` 过程中不会替换 `SKILL.md` 中的占位符。

手动等效操作：

```bash
claude plugin marketplace add ./
claude plugin install humanize@KernelPilot

mkdir -p ~/.claude/skills
ln -s "$PWD/external/KernelWiki" ~/.claude/skills/KernelWiki
ln -s "$PWD/external/ncu-report-skill" ~/.claude/skills/ncu-report-skill
python3 -m pip install -r external/KernelWiki/requirements.txt
humanize/scripts/install-skills-claude.sh --skip-pip
```

安装后请重启 Claude Code。如果您希望在现有的 Claude Code 会话中运行市场命令，可以使用以下等效的斜杠命令：

```text
/plugin marketplace add /path/to/kernel-pilot
/plugin install humanize@KernelPilot
```

## 方式二：单次会话本地开发

如果您已在本地克隆了该插件：

```bash
claude --plugin-dir /path/to/kernel-pilot/humanize \
  --add-dir /path/to/kernel-pilot
```

此命令仅在当前 Claude Code 会话中加载该插件。如需技能发现功能，请单独添加外部技能：

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/kernel-pilot/external/KernelWiki ~/.claude/skills/KernelWiki
ln -s /path/to/kernel-pilot/external/ncu-report-skill ~/.claude/skills/ncu-report-skill
```

## 方式三：仅安装上游 Humanize

如果您只需要通用的 Humanize RLCR，而不需要 KernelPilot 的内核循环或外部内核技能，请安装上游 Humanize 市场：

```text
/plugin marketplace add PolyArch/humanize
/plugin install humanize@PolyArch
```

上游插件适用于通用的实现循环，但不提供本仓库中的 `humanize-kernel-agent-loop`、`KernelWiki` 或 `ncu-report-skill`。

## 验证安装

安装 KernelPilot 市场后，您应该可以看到 Humanize 命令和内核循环技能：

```text
/humanize:start-rlcr-loop
/humanize:gen-plan
/humanize:refine-plan
/humanize:ask-codex
humanize-kernel-agent-loop
KernelWiki
ncu-report-skill
```

您也可以在终端中检查已安装的插件：

```bash
claude plugin list
claude plugin details humanize@KernelPilot
```

## 监控设置（可选）

将监控辅助工具添加到您的 shell 中，以实现实时进度跟踪：

```bash
# 添加到您的 .bashrc 或 .zshrc
source ~/.claude/plugins/cache/KernelPilot/humanize/<LATEST.VERSION>/scripts/humanize.sh
```

然后使用：

```bash
humanize monitor rlcr
```

## 其他安装指南

- [为 Codex 安装](install-for-codex.md)

## 后续步骤

请参阅[使用指南](usage.md)了解详细的命令参考和配置选项。
