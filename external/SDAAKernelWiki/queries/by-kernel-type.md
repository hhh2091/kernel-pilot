# 按算子类型索引

| 算子类型 | 页面 |
|---|---|
| RMSNorm / reduction | `kernel-rmsnorm-pmu-analysis`, `pattern-scheduling-bubbles`, `pattern-ldm-pressure` |
| Memory copy / DMA-heavy | `hw-dma`, `hw-hbm-channel-bank-row`, `technique-dma-periodic-partitioning`, `technique-dma-odd-even-interleave` |
| Broadcast / communication | `hw-rma`, `technique-rma-broadcast-selection`, `pattern-rma-contention` |
| GEMM / matmul | `hw-ace`, `technique-ace-double-buffering`, `pattern-ace-feeding-writeback` |
| Elementwise | `hw-pipe0-pipe1`, `technique-p0-p1-overlap`, `hw-ldm` |
