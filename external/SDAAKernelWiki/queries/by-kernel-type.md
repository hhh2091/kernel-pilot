# 按算子类型索引

| 算子类型 | 页面 |
|---|---|
| RMSNorm / reduction | `kernel-rmsnorm-pmu-analysis`, `technique-sdaa-math-and-high-level-api`, `technique-sdaa-atomic-api`, `pattern-scheduling-bubbles`, `pattern-ldm-pressure` |
| Memory copy / DMA-heavy | `hw-dma`, `hw-hbm-channel-bank-row`, `technique-dma-periodic-partitioning`, `technique-dma-odd-even-interleave` |
| Broadcast / communication | `hw-rma`, `technique-rma-broadcast-selection`, `pattern-rma-contention` |
| GEMM / matmul | `kernel-sdaa-gemm`, `technique-sdaa-matmul-api`, `technique-sdaa-simd-vectorization`, `technique-sdaa-rma-broadcast-api`, `technique-ace-double-buffering`, `pattern-ace-feeding-writeback` |
| Elementwise / activation | `technique-sdaa-simd-vectorization`, `technique-sdaa-math-and-high-level-api`, `hw-pipe0-pipe1`, `technique-p0-p1-overlap`, `hw-ldm` |
| Transpose / layout | `technique-sdaa-transpose-api`, `technique-sdaa-dma-api`, `hw-sdaa-memory-model` |
| Atomic update | `technique-sdaa-atomic-api`, `example-sdaa-programming-guide-examples` |
| Operator development | `kernel-sdaa-operator-development`, `example-sdaa-quickstart`, `example-sdaa-programming-guide-examples` |
| CUDA migration | `migration-cuda-to-sdaa-c`, `pattern-sdaa-compile-porting-errors`, `lang-sdaa-c-programming-guide` |
