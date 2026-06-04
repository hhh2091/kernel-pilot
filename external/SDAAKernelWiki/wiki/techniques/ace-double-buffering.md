---
id: technique-ace-double-buffering
title: "ACE 累加器双缓冲"
type: technique
architectures: [teco-t1, sdaa]
tags: [ace, ace-double-buffering, ldm]
confidence: source-reported
reproducibility: pseudocode
related: [hw-ace, pattern-ace-feeding-writeback]
sources: [source-local-teco-t1, source-local-ace-cost-table]
---

# ACE 累加器双缓冲

本地笔记中 ACE 暴露两个累加器缓冲区。一个缓冲区用于计算时，另一个可通过 `rt_ace_writeback` 写回 LDM。

## 伪代码

```text
active = 0
for tile in tiles:
  idle = 1 - active
  if tile > 0:
    rt_ace_writeback(buffer=idle, dst=ldm_output_previous)
  rt_ace_load_west(buffer=active, a_tile)
  rt_ace_load_north(buffer=active, b_tile)
  active = idle
```

在代码生成输出具体调用前，必须从官方头文件确认真实 API 签名。

## 测量项

用 ACE cycle / cost table 选择候选 shape，然后用 kernel time 和可用的 ACE/feed/writeback counter 确认。
