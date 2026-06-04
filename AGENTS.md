# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目概述

KernelPilot 是一个自主 GPU 内核优化框架，围绕 RLCR（Ralph-Loop with Codex Review）迭代开发循环构建，用于 CUDA/GPU 内核调优。核心流程：定义内核(K)、正确性参考(R)、工作负载(W) -> 创建独立工作区 -> 迭代实现/测试/基准 -> 通过 KernelWiki 查阅先验知识 -> 通过 ncu-report-skill 进行 Nsight Compute 分析 -> 由 Codex 审查门控下一轮。默认预算 84 次迭代。

## 常用命令

```bash
# 安装插件（Codex 环境）
humanize/scripts/install-skills-Codex.sh

# 运行全部测试
humanize/tests/run-all-tests.sh

# 运行单个测试
humanize/tests/test-<name>.sh

# 控制测试并行度
HUMANIZE_TEST_JOBS=4 humanize/tests/run-all-tests.sh

# 启动可视化仪表盘
humanize/viz/scripts/viz-start.sh

# 启动 RLCR 循环（在 Codex 中使用斜杠命令）
/humanize:start-rlcr-loop
/humanize:cancel-rlcr-loop

# 规划流程
/humanize:gen-idea
/humanize:explore-idea
/humanize:gen-plan
/humanize:refine-plan
```

## 架构

项目采用分层架构，无传统编译构建系统——主体由 Shell 脚本、Markdown 模板、JSON 配置和少量 Python/JS 组成。

### Layer 1: Humanize（核心迭代循环引擎）

从 `github.com/PolyArch/humanize` vendored 而来（分支 `dev`，提交 `1c45548`）。提供 RLCR 循环基础设施：

- **Hook 系统**（`humanize/hooks/`）：拦截 Codex 的 Write/Edit/Read/Bash 工具调用，强制执行约束（禁止编辑 state 文件、循环期间禁止 git push、plan 文件不可变等）
- **状态管理**：循环状态存储在 `.humanize/rlcr/<timestamp>/state.md`
- **Stop Hook**：在退出前触发 Codex 审查，审查结果门控下一轮

### Layer 2: KernelPilot（GPU 内核优化特化）

通过 `humanize-kernel-agent-loop` skill 为内核优化定制循环：

- **K/R/W 输入契约**：内核、参考实现、工作负载三元组
- **工作区脚手架**：`src/`, `tests/`, `benchmarks/`, `ledgers/`, `dispatch/`, `profile-artifacts/`
- **接受检查**与增量调度
- 安装脚本（`install-skills-Codex.sh`）负责路径注入，使 skill 能定位外部工具

### Layer 3: 外部技能（知识与分析）

- **KernelWiki**（`external/KernelWiki/`，git submodule）：2,692 个合并 PR 页面的语料库，来自 SGLang/vLLM/PyTorch/FlashAttention/CUTLASS/Triton 等项目，提供 `query.py`/`grep.py`/`get_page.py` 查询接口
- **ncu-report-skill**（`external/ncu-report-skill/`，git submodule）：Nsight Compute 分析工作流文档

### 支撑基础设施

- **Prompt 模板**（`humanize/prompt-template/`）：~60 个模板，按 block/Codex/codex/explore/idea/plan 子目录组织
- **Agent 定义**（`humanize/agents/`）：plan 合规检查器、plan 理解测验、草稿相关性检查器、bitlesson 选择器
- **可视化仪表盘**（`humanize/viz/`）：Flask+WebSocket Web 仪表盘，支持文件监视和日志流式传输
- **Prompt 卡片**（`prompts/`）：端到端优化任务定义，可直接粘贴到 Codex 使用

## 项目约定

- 所有实现、注释、测试和文档必须使用英文，禁止 Emoji 和 CJK 字符
- 版本号格式为 `X.Y.Z`（纯数字），版本变更需同步更新三个文件：`humanize/.Codex-plugin/plugin.json`、`humanize/.Codex-plugin/marketplace.json`、`humanize/README.md`（"Current Version" 行）
- `commands/gen-plan.md` 中的 plan 模板（Phase 5 Plan Structure 部分）与 `prompt-template/plan/gen-plan-template.md` 保持同步，修改任一文件需同步另一个
- `directions.json` schema v1 定义在两处需保持同步：`scripts/validate-directions-json.sh` 中的 jq 校验表达式与 `commands/gen-idea.md` 中的 schema 文档（Step 4.5）
- Worker 约束（硬上限、隔离规则、no-push 规则、sentinel 格式）文档分布在四处需保持同步：`commands/explore-idea.md`、`prompt-template/explore/worker-prompt.md`、`scripts/validate-explore-idea-io.sh`、`docs/usage.md`

## 技术栈

| 层次 | 技术 |
|------|------|
| 主要语言 | Bash/Shell（~110 个 .sh 文件） |
| Web 仪表盘 | Python (Flask, flask-sock) + JavaScript + HTML/CSS |
| 配置/元数据 | JSON |
| 模板/文档 | Markdown |
| CI/CD | GitHub Actions（6 个工作流，运行在 ubuntu-latest，依赖 zsh 和 jq） |
| 外部依赖 | KernelWiki（Python，pip 依赖）、ncu-report-skill |
