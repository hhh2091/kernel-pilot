# 按技术索引

| 技术 | Page ID | 主要用途 |
|---|---|---|
| 周期式 DMA 划分 | `technique-dma-periodic-partitioning` | 让 32 个 SPE 的聚合 HBM 访问更连续。 |
| DMA 奇偶交错 | `technique-dma-odd-even-interleave` | 测试经验引擎顺序 `(0,2,4,6,1,3,5,7)`。 |
| DMA 队列预算 | `technique-dma-queue-budgeting` | 避免超过约 11 个读写请求的经验队列深度。 |
| RMA 广播选择 | `technique-rma-broadcast-selection` | 选择点对点、列广播、双对角线行广播或跨步列广播。 |
| ACE 双缓冲 | `technique-ace-double-buffering` | 重叠 ACE 计算和 writeback。 |
| P0/P1 overlap | `technique-p0-p1-overlap` | 通过交错计算和访存/控制工作减少 issue 空泡。 |
