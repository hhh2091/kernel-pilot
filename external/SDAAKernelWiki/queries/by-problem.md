# 按问题索引

| 症状 | 模式 | 候选页面 |
|---|---|---|
| 调度空泡 | `pattern-scheduling-bubbles` | `hw-pipe0-pipe1`, `technique-p0-p1-overlap` |
| LDM 压力 | `pattern-ldm-pressure` | `hw-ldm`, `technique-p0-p1-overlap` |
| DMA/HBM 未打满 | `pattern-dma-hbm-underutilization` | `hw-dma`, `hw-hbm-channel-bank-row`, `technique-dma-periodic-partitioning`, `technique-dma-odd-even-interleave` |
| RMA 竞争 | `pattern-rma-contention` | `hw-rma`, `technique-rma-broadcast-selection` |
| ACE feeding/writeback | `pattern-ace-feeding-writeback` | `hw-ace`, `technique-ace-double-buffering` |
| 编译失败 | `pattern-sdaa-compile-porting-errors` | `compiler-tecocc-build-debug`, `lang-sdaa-c-programming-guide` |
| CUDA 迁移不匹配 | `pattern-sdaa-compile-porting-errors` | `migration-cuda-to-sdaa-c`, `hw-sdaa-memory-model` |
| reduction 或 atomic 热点 | `technique-sdaa-atomic-api` | `technique-sdaa-simd-vectorization`, `technique-sdaa-math-and-high-level-api` |
| layout transform 成本高 | `technique-sdaa-transpose-api` | `technique-sdaa-dma-api`, `kernel-sdaa-gemm` |
| quickstart / smoke test 失败 | `example-sdaa-quickstart` | `runtime-sdaa-host-api`, `compiler-tecocc-build-debug`, `runtime-sdaa-env-and-debug` |
