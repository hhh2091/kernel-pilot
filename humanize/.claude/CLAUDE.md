# Humanize 简介
这是一个 Claude Code 插件，提供带独立 AI 审查的迭代开发功能。使用 `/start-rlcr-loop` 启动 RLCR 循环，使用 `/cancel-rlcr-loop` 取消活跃循环。

# Humanize 项目规则
- 本项目的所有内容，包括但不限于实现、注释、测试和文档，均使用中文。
- 如果需要版本升级，请在以下三个文件中更新版本号：`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json` 和 `README.md`（"Current Version" 行）。
- 版本号格式必须为 `X.Y.Z`，其中 X/Y/Z 为数字。版本号不得包含 `X.Y.Z` 以外的任何内容。例如，好的版本号是 `9.732.42`；坏的版本号示例（不得使用）：`3.22.7-alpha`（多余的 "-alpha" 字符串）、`9.77.2 (2026-01-07)`（无用的日期/时间戳）。
- `commands/gen-plan.md` 中的计划模板（Phase 5 Plan Structure 部分）与 `prompt-template/plan/gen-plan-template.md` 有意保持同步。修改任一文件时，请确保同步更新另一个文件以保持一致性。
- 反之，对 `prompt-template/plan/gen-plan-template.md` 的更改也必须反映在 `commands/gen-plan.md` 的 Plan Structure 部分中。
- `directions.json` schema v1 定义在两处，必须保持同步：`scripts/validate-directions-json.sh` 中的 jq 验证表达式和 `commands/gen-idea.md` 中的 schema 文档（Step 4.5）。在任一处添加、删除或重命名字段时，请同步更新另一处。
- Worker 约束（硬上限、隔离规则、no-push 规则、sentinel 格式）文档分布在四处，必须保持同步：`commands/explore-idea.md`（coordinator phases）、`prompt-template/explore/worker-prompt.md`（worker instructions）、`scripts/validate-explore-idea-io.sh`（cap enforcement）和 `docs/usage.md`（user-facing option docs）。对上限值或约束的任何更改都必须在所有四处反映。
