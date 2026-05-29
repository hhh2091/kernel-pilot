# 内置的 Humanize 上游

- 来源：https://github.com/PolyArch/humanize
- 分支：dev
- 导入的提交：1c45548
- 导入命令：

```bash
git clone --recursive --branch dev --depth 1 https://github.com/PolyArch/humanize.git humanize
```

KernelPilot 补丁添加了 `humanize-kernel-agent-loop` 以及针对外部 `KernelWiki` 和 `ncu-report-skill` 技能源的安装器注入。内核优化循环使用 `--strict-success` 启动 RLCR，该标志会抑制最大迭代次数和停滞退出，直到满足验收目标或用户取消循环。
