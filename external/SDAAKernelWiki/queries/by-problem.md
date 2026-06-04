# 按问题索引

| 症状 | 模式 | 候选页面 |
|---|---|---|
| 调度空泡 | `pattern-scheduling-bubbles` | `hw-pipe0-pipe1`, `technique-p0-p1-overlap` |
| LDM 压力 | `pattern-ldm-pressure` | `hw-ldm`, `technique-p0-p1-overlap` |
| DMA/HBM 未打满 | `pattern-dma-hbm-underutilization` | `hw-dma`, `hw-hbm-channel-bank-row`, `technique-dma-periodic-partitioning`, `technique-dma-odd-even-interleave` |
| RMA 竞争 | `pattern-rma-contention` | `hw-rma`, `technique-rma-broadcast-selection` |
| ACE feeding/writeback | `pattern-ace-feeding-writeback` | `hw-ace`, `technique-ace-double-buffering` |
