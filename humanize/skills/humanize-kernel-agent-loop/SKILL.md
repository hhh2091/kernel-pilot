---
name: humanize-kernel-agent-loop
description: "运行 Humanize 内核优化循环：恢复 K/R/W，使用一个干净的独立工作区，基于正确性和基准证据进行迭代，在先验知识有用时使用 KernelWiki，在需要性能分析时使用 ncu-report-skill。"
type: flow
---

# Humanize 内核代理循环

当用户需要自主 GPU 内核优化运行时使用此流程，而非通用软件功能循环。该技能为代理提供内核形态的工作区和审查循环，同时按需提供研究和性能分析工具。

风格刻意保持轻量：

- 当上游 PR、wiki 笔记、文档或已有内核有助于当前设计选择时，使用 `KernelWiki`。
- 当需要性能分析证据来解释基线、回归、平台期、意外提升或下一次优化编辑时，使用 `ncu-report-skill`。
- 不要仅为满足流程仪式而运行知识或性能分析步骤。当工具实质性地改变了下一步时，记录原因。

## 输入形态

在开始循环之前恢复或定义以下内容：

```text
K: kernel definition and semantics
R: correctness reference or oracle
W: workload distribution or focused benchmark case
```

仅在 `K`、`R`、`W`、目标 GPU、比较目标或硬性范围约束缺失且无法安全推断时才询问用户。

如果 `W` 包含多种模式，将它们作为分布进行优化和报告。如果 `W` 是一个聚焦的 shape，说明这一点并保持调度/调优决策简单。

## 已安装路径

安装程序注入以下路径：

```text
Humanize runtime: {{HUMANIZE_RUNTIME_ROOT}}
KernelPilot root: {{KERNELPILOT_ROOT}}
KernelWiki root: {{KERNELWIKI_ROOT}}
ncu-report-skill root: {{NCU_REPORT_SKILL_ROOT}}
```

如果 `{{KERNELWIKI_ROOT}}` 或 `{{NCU_REPORT_SKILL_ROOT}}` 未被注入，查找名为 `KernelWiki` 和 `ncu-report-skill` 的同级技能，或使用 KernelPilot 检出默认值 `external/KernelWiki` 和 `external/ncu-report-skill`。

## 循环应执行的操作

在此技能内部运行 Humanize 设置。用户不应需要手动运行 `gen-plan`、`refine-plan` 或 `humanize-rlcr`。

1. 将用户请求转换为一个小型内核特定计划，包含验收检查。
2. 选择或创建恰好一个干净的独立优化工作区。
3. 仅引导启动 RLCR 所需的最小脚手架、测试占位文件、账本和精炼计划。
4. 确保工作区是一个 git 仓库，包含一个干净的脚手架提交。
5. 使用 `--strict-success` 启动 RLCR，并验证存在活跃的 `.humanize/rlcr/<timestamp>/state.md`。
6. 读取 `.humanize/rlcr/<timestamp>/round-0-prompt.md`。
7. 然后才在 Humanize 审查下基于正确性和基准证据迭代候选内核。
8. 当先验知识可以指导设计时，使用 KernelWiki 或实时上游源。
9. 当性能分析证据可以回答当前问题时，使用 ncu-report-skill。
10. 仅在 `W` 确实需要时才按 shape 进行自动调优或调度。

这是一个循环，而不是固定的研究清单。一个好的轮次可能是一个微小的正确性修复、基准清理、基于 KernelWiki 的重新设计、NCU 性能分析摘要或一次自动调优，取决于证据所说。

## RLCR 前引导门控

此技能有严格的顺序要求：在 RLCR 激活之前，不要实现候选内核、运行长时间基准测试、收集 NCU 报告或编写最终报告。RLCR 前的工作限于：

- 选择工作区根目录。
- 编写脚手架、精炼计划、空或占位测试文件和账本。
- 创建 `.gitignore` 条目以保持 `.humanize*` 不被跟踪。
- 初始化 git 并提交脚手架。
- 运行 `setup-rlcr-loop.sh`。

如果工作区没有 git 仓库，在脚手架提交之前初始化它：

```bash
git init
git add .gitignore README.md workloads/ src/ bindings/ tests/ benchmarks/ dispatch/ ledgers/ profile-artifacts/
git commit -m "Initialize kernel optimization workspace"
```

调整路径列表以匹配实际存在的脚手架，并仅在存在时添加可选构建文件如 `setup.py` 或 `python/`，但不要添加 `.humanize/`。如果 git 未配置用户身份，设置本地身份如 `git config user.name KernelPilot` 和 `git config user.email kernelpilot@example.invalid`。

`setup-rlcr-loop.sh` 成功后，立即验证 RLCR 是否活跃：

```bash
find .humanize/rlcr -maxdepth 2 -name state.md -print
```

如果没有 `state.md`，停止并报告 RLCR 未启动。不要在 Humanize 循环之外继续进行内核实现。

## 工作区根目录

整个循环使用一个工作区根目录。这是包含 `README.md`、`src/`、`tests/`、`benchmarks/`、`ledgers/` 和 `.humanize/` 的目录。

选择规则：

- 如果当前目录已经是空的或预期的优化工作区，直接使用当前目录。
- 如果当前目录是大型框架检出（如 SGLang、vLLM 或 PyTorch），为实验创建一个同级的独立工作区。
- 如果当前目录已包含 `.humanize/`、`ledgers/`、`src/` 或此任务的先前脚手架，不要创建另一个嵌套仓库。除非用户明确要求新工作区，否则从该根目录继续。
- 切勿在另一个优化仓库内创建 git 仓库。如果嵌套仓库已存在，在继续之前停止并报告分支情况。
- 从包含内核代码和账本的同一工作区根目录运行 Humanize/RLCR。不要在一个仓库中保持 RLCR 状态而在另一个仓库中提交代码。

在选定的工作区根目录创建以下骨架：

```text
.gitignore
.humanize/kernel-agent/refined-plan.md
README.md
workloads/
src/<task_name>/
bindings/
tests/
benchmarks/
dispatch/
ledgers/attempt-ledger.md
ledgers/optimization-ledger.md
ledgers/lineage.jsonl
ledgers/research-digest.md
ledgers/tuning-decisions.md
benchmarks/performance-map.json
profile-artifacts/README.md
```

保持源框架检出为只读，除非用户明确要求就地框架补丁。

在第一次脚手架提交之前，`.gitignore` 应保护本地 Humanize 状态：

```gitignore
.humanize*
```

精炼计划文件应为 RLCR 存在但默认不被跟踪：

```bash
git check-ignore .humanize/kernel-agent/refined-plan.md
if git ls-files --error-unmatch .humanize/kernel-agent/refined-plan.md >/dev/null 2>&1; then
  git rm --cached .humanize/kernel-agent/refined-plan.md
fi
```

从工作区根目录提交脚手架和测试文件，而非 `.humanize/` 循环状态。此提交必须在运行 RLCR 设置之前存在。

## 轻量验收检查

精炼计划应保持这些检查可见，而不将它们变成大型仪式：

- `K`、`R`、`W`、目标 GPU、比较基线和硬性排除项是明确的。
- 正确性测试在相关用例上比较候选输出与 `R`。
- 基准测试报告每用例延迟和足够的环境元数据以公平比较各次尝试。
- 尝试账本记录已测试的版本，包括失败的正确性、回归和放弃的想法。
- 优化账本仅记录具有可测量改进的正确版本。
- 谱系记录选定候选发生变化的原因。
- 外部代码或源码级借用记录 URL/路径、提交或版本、相关时的许可证/通知以及适配内容。
- 最终输出命名选定的内核、基准结果、已知回退和不支持的模式。

## 使用 KernelWiki

当已有工作可以帮助回答以下问题时，使用 `KernelWiki` 技能：

- SGLang、vLLM、FlashInfer、PyTorch、CUTLASS、Triton 或 TensorRT-LLM 是否已经解决了类似的内核问题？
- 对于此内存布局、dtype、tensor-core 路径、调度问题或尾效应症状，是否有已知的 Blackwell/Hopper 技术？
- 当前设计是否缺少明显的上游技巧？

从 `{{KERNELWIKI_ROOT}}` 运行命令：

```bash
cd {{KERNELWIKI_ROOT}}
python3 scripts/query.py "FlashAttention SM100 MLA topk" --limit 5 --compact
python3 scripts/query.py --repo sglang --tag tma --compact
python3 scripts/grep_wiki.py "tcgen05|tmem" --only prs
python3 scripts/get_page.py kernel-flash-attention-sm100-mla-topk --follow-sources
```

将结果作为证据使用，而非作为规则手册。如果某个来源直接影响实现代码，将其追溯到 PR 页面、制品、官方文档或上游源路径。

## 使用 ncu-report-skill

当性能分析证据会改变下一个决策时，使用 `ncu-report-skill`。良好的触发条件包括：

- 基线不清晰，代表性性能分析可以定位热路径或瓶颈。
- 正确的候选出现回归或平台期。
- 候选出乎意料地快或慢。
- 下一次编辑取决于了解问题是内存、占用率、调度、tensor-core 利用率还是尾效应。
- 审查者要求提供性能分析支持的证据。

NCU 报告应简小且可操作：将报告路径、关键指标、诊断和一个具体的下一步编辑保存在 `profile-artifacts/` 或尝试账本中。当编译/测试/基准证据对当前步骤已经足够时，不要因性能分析而阻塞进度。

## 进度检查

- 如果尝试挂起或超时，在目标大小基准测试之前，在硬超时下缩减到最小可执行 shape 或 tile。
- 如果重复轮次遇到相同阻碍，将下一轮缩小到更小的可证伪里程碑或重置设计。
- 如果正确的候选远低于目标，使用先验知识、性能分析或更简单的基线比较来决定谱系是否值得继续。

## RLCR 启动

编写并提交工作区脚手架后，从选定的工作区根目录内启动循环：

```bash
"{{HUMANIZE_RUNTIME_ROOT}}/scripts/setup-rlcr-loop.sh" .humanize/kernel-agent/refined-plan.md --yolo --strict-success
```

如果设置以非零退出，报告错误而不是绕过门控。循环默认使用 Humanize 配置的审查模型和严格成功模式，因此最大迭代和停滞检查会触发恢复提示，而不是在达到验收目标之前结束运行。调用者仍可传递显式覆盖如 `--max` 或模型标志。

设置成功后：

1. 读取 `.humanize/rlcr/<timestamp>/round-0-prompt.md`。
2. 执行当前轮次。
3. 提交更改。
4. 编写所需的轮次摘要。
5. 正常停止以便 Humanize Stop 钩子可以审查。

如果钩子阻止退出，遵循生成的下一轮提示。
