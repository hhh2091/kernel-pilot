# 按技术索引

| 技术 | Page ID | 主要用途 |
|---|---|---|
| 周期式 DMA 划分 | `technique-dma-periodic-partitioning` | 让 32 个 SPE 的聚合 HBM 访问更连续。 |
| SDAA DMA API | `technique-sdaa-dma-api` | 使用 blocking/async/stride DMA，约束 Global/SPM 数据路径。 |
| DMA 奇偶交错 | `technique-dma-odd-even-interleave` | 测试经验引擎顺序 `(0,2,4,6,1,3,5,7)`。 |
| DMA 队列预算 | `technique-dma-queue-budgeting` | 避免超过约 11 个读写请求的经验队列深度。 |
| ThreadGroup / sync | `technique-sdaa-thread-group-sync` | 管理 SPE group 与同步收敛。 |
| SDAA RMA/Broadcast API | `technique-sdaa-rma-broadcast-api` | 管理同一 SPA 内 SPE 间 SPM 数据传输。 |
| RMA 广播选择 | `technique-rma-broadcast-selection` | 选择点对点、列广播、双对角线行广播或跨步列广播。 |
| SDAA MatMul API | `technique-sdaa-matmul-api` | 使用阻塞/非阻塞 matmul 接口生成 GEMM/MatMul。 |
| SIMD 向量化 | `technique-sdaa-simd-vectorization` | 用显式向量类型和 intrinsic 优化 elementwise/reduction/GEMM baseline。 |
| Atomic | `technique-sdaa-atomic-api` | 作为跨分片 merge 或 correctness fallback，避免高争用热地址。 |
| Transpose | `technique-sdaa-transpose-api` | 处理 layout transform 和 GEMM B 矩阵预处理。 |
| 数学/高层接口 | `technique-sdaa-math-and-high-level-api` | 处理 math、activation、batch math 和 reduction baseline。 |
| 性能采样 | `technique-sdaa-perf-sampling` | 用 `sdaa_perf.h` 标记 hot section cycle。 |
| ACE 双缓冲 | `technique-ace-double-buffering` | 重叠 ACE 计算和 writeback。 |
| P0/P1 overlap | `technique-p0-p1-overlap` | 通过交错计算和访存/控制工作减少 issue 空泡。 |
