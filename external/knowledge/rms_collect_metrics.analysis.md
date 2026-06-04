# JSON 瓶颈分析视图: rms_collect_metrics.json

- 输入文件: `/data/dnn/gupeng/optest-agent/runs/rms_collect_metrics.json`
- 字段总数: `825`

## 初步结论

- [high] 当前 demo 只激活了少量 SPE，但 DMA engine 已全覆盖: 当前运行形态更像“计算并行度只开了部分 SPE”，不是“DMA 列资源没有铺开”；对这个 RMS demo，活跃 SPE 只有总量的一部分，但活跃 DMA engine 已覆盖全部 8 列。
- [high] 调度/发射侧压力明显: zero-launch 与 cannot-launch 指标偏高，说明 pipe 发射不够顺畅，当前更像调度空泡或 wait 驱动型流水问题。
- [medium] LDM / local-memory 压力存在: local-memory 访问密度较高，且出现一定未仲裁等待，说明 LDM 使用和局部数据搬运值得重点检查。
- [medium] 当前不像典型 HBM / DMA 饱和: global-load 与 DMA-request 密度都不高，当前没有看到典型 HBM/DMA 饱和证据；但仅凭现有 JSON 仍无法验证 128B 对齐、chunk 大小、通道映射和跨行访问模式。
- [medium] 指令缓存问题不突出: icache miss rate 较低，当前不像代码体积或指令缓存 miss 导致的主瓶颈。
- [medium] 端到端 runtime / driver 开销不可忽略: runtime 或 driver 总时长已超过 kernel 总时长，若关注端到端性能，需要同时优化 launch/API 开销。

## 直观换算

### 时间与 Cycle

| 指标 | 当前值 | 说明 |
|---|---|---|
| kernel 平均耗时 (us) | `49.363631068` | 把 `kernel_duration_ns_avg` 换算成微秒，更适合直接感知单次 kernel 大小。 |
| kernel 平均 SPE cycle | `116498.16932` | 按当前 `SPE` 频率换算的单次 kernel 周期数。 |

### 执行形态与 DMA 结构

| 指标 | 当前值 | 说明 |
|---|---|---|
| 活跃 SPE 占比 (%) | `25` | 这次 kernel 实际参与执行的 SPE 占 32 个 SPE 的比例。 |
| 活跃 DMA engine 占比 (%) | `100` | 这次 kernel 真正被活跃 SPE 用到的 DMA engine 占 8 个引擎的比例。 |
| 活跃 SPE 数量 | `8` | 这次 kernel 实际参与执行的 SPE 数量。 |
| 活跃 DMA engine 数量 | `8` | 按列绑定规则推导出的活跃 DMA engine 数量。 |
| 单 SPE 主 DMA chunk 大小 (bytes) | `32768` | 单个活跃 SPE 主体 DMA chunk 的大小。 |
| 单 SPE 尾 DMA chunk 大小 (bytes) | `10624` | 若存在尾块，这是单个活跃 SPE 最后一个 DMA chunk 的大小。 |
| 单 SPE DMA chunk 数量 | `8` | 单个活跃 SPE 在一次 kernel 中需要发起多少个 DMA chunk。 |
| 对齐检查粒度 (bytes) | `128` | 当前 DMA 对齐检查采用的字节粒度。 |
| DMA size 是否 128B 对齐 | `True` | 仅从 DMA 传输大小看，是否都是 128B 整数倍。 |
| DMA offset 是否 128B 对齐 | `True` | 仅从 DMA offset/stride 看，是否都是 128B 整数倍。 |
| 严格整体 128B 对齐结论 | `None` | 若当前值是 `None`，表示还缺少 device base address，不能下严格结论。 |

### 调度直观指标

| 指标 | 当前值 | 说明 |
|---|---|---|
| 整体 zero-launch 占比 (%) | `15.4909455047` | 发射空泡占比，越高越像 pipe 发射不顺或 wait 驱动流水。 |
| 整体 zero-latency launch 占比 (%) | `9.2620009021` | 零延迟发射占比，可辅助观察 issue 是否吃满。 |
| pipe0 zero-latency 占比 (%) | `19.4179229205` | pipe0 侧发射空泡信号。 |
| pipe1 zero-latency 占比 (%) | `15.1678301948` | pipe1 侧发射空泡信号。 |
| pipe0 launch 占比 (%) | `42.9311153338` | pipe0 在双 pipe 总 launch 中的占比。 |
| pipe1 launch 占比 (%) | `57.0688846662` | pipe1 在双 pipe 总 launch 中的占比。 |
| 每次 kernel 平均 zero-launch cycles | `1393.76699029` | 把累计 zero-launch cycles 摊到单次 kernel，更直观看空泡严重程度。 |
| 每次 kernel 平均 zero-latency cycles | `833.330097087` | 把累计 zero-latency cycles 摊到单次 kernel。 |
| 每次 kernel 平均 pipe0 cannot-launch 计数 | `3468.52427184` | pipe0 不能发射的平均计数；当前字段口径是计数，不强行改写成 cycles。 |
| 每次 kernel 平均 pipe1 cannot-launch cycles | `929.495145631` | pipe1 不能发射等待的平均周期数。 |

### LDM / DMA / icache 直观指标

| 指标 | 当前值 | 说明 |
|---|---|---|
| icache miss rate (%) | `0.119139441353` | 把 miss rate 直接换算成百分比，更方便判断是否明显异常。 |
| 每 1000 次 icache access 的 miss 次数 | `1.19139441353` | 把比例换算成每千次访问 miss 数，更符合直觉。 |
| 每次 kernel 平均 icache miss cycles | `638.912621359` | 把累计 icache miss 等待摊到单次 kernel。 |
| 每次 kernel 平均 local-memory unarb cycles | `133.475728155` | local-memory 未仲裁等待的平均周期数。 |
| 每次 kernel 平均 DMA requests | `1.03883495146` | 把累计 DMA request 摊到单次 kernel。 |
| 每次 kernel 平均 DMA GET requests | `1.01941747573` | 把累计 DMA GET request 摊到单次 kernel。 |
| host/device memcpy 聚合带宽 (GiB/s) | `0.0653969328654` | 这是 SDPTI 采到的 host/device memcpy 聚合带宽，不是 kernel 内部 DMA 引擎有效带宽。 |

### 端到端开销直观指标

| 指标 | 当前值 | 说明 |
|---|---|---|
| runtime API 平均耗时 (us) | `38.8356783626` | 单次 runtime API 调用平均耗时。 |
| driver API 平均耗时 (us) | `20.9473062016` | 单次 driver API 调用平均耗时。 |
| runtime 总时长 / kernel 总时长 | `3.91835642529` | 大于 1 说明从端到端角度看，runtime 开销已超过 kernel 本体总时长。 |
| driver 总时长 / kernel 总时长 | `2.12585461487` | 大于 1 说明 driver 开销已超过 kernel 本体总时长。 |

## 按瓶颈方向分组

### 更像调度问题

| 字段 | 当前值 |
|---|---|
| `derived_zero_launch_ratio` | `0.154909455047` |
| `derived_launch_zero_latency_ratio` | `0.092620009021` |
| `derived_nonempty_zero_launch_ratio` | `0.0821130824562` |
| `derived_pipe0_zero_latency_ratio` | `0.194179229205` |
| `derived_pipe1_zero_latency_ratio` | `0.151678301948` |
| `derived_pipe0_cannot_launch_per_launch` | `0.783599718371` |
| `derived_pipe1_cannot_launch_per_launch` | `0.157968118616` |
| `derived_pipe0_launch_share` | `0.429311153338` |
| `derived_pipe1_launch_share` | `0.570688846662` |
| `slave__inst_zero_launch_cycles` | `143558` |
| `slave__inst_launch_zero_latency_cycles` | `85833` |
| `slave__pipe0_inst_cannot_launch` | `357258` |
| `slave__pipe1_inst_cannot_launch_cycles` | `95738` |

### 更像 LDM / local-memory 问题

| 字段 | 当前值 |
|---|---|
| `derived_local_memory_access_per_inst` | `0.252166864208` |
| `derived_pipe_local_memory_access_per_inst` | `0.179661760329` |
| `derived_pipe_local_memory_direct_access_per_inst` | `0.175885412044` |
| `derived_local_memory_unarb_cycles_per_inst` | `0.0179458127307` |
| `derived_local_memory_violate_cycles_per_inst` | `0.000304144193065` |
| `slave__local_memory_access` | `193181` |
| `slave__pipe_local_memory_access` | `137636` |
| `slave__pipe_local_memory_direct_access` | `134743` |
| `lsu__local_access_local_memory_unarb_cycles` | `13748` |

### 更像 HBM / DMA 问题

| 字段 | 当前值 |
|---|---|
| `derived_global_load_access_per_inst` | `0.000403350024279` |
| `derived_global_store_access_per_inst` | `1.3053398844e-06` |
| `derived_dma_requests_per_inst` | `0.000139671367631` |
| `derived_dma_get_requests_per_inst` | `0.000137060687862` |
| `derived_dma_put_get_requests_per_inst` | `0.000140976707515` |
| `derived_io_requests_per_inst` | `0.0017569874844` |
| `lsu__gld_global_memory_access` | `309` |
| `lsu__gst_global_memory_access` | `1` |
| `dma__requests` | `107` |
| `dma__get_requests` | `105` |
| `dma__put_get_requests` | `108` |
| `memcpy_bandwidth_gib_per_s` | `0.0653969328654` |

### 更像指令缓存问题

| 字段 | 当前值 |
|---|---|
| `derived_icache_miss_rate` | `0.00119139441353` |
| `l1ic__icache_access` | `580832` |
| `l1ic__icache_miss` | `692` |
| `l1ic__icache_miss_cycles` | `65808` |
| `l0ic_bubbles` | `0` |
| `l0ic__inst_read` | `279416` |

### 更像 runtime / launch 开销

| 字段 | 当前值 |
|---|---|
| `kernel_duration_ns_total` | `5084454` |
| `kernel_duration_ns_avg` | `49363.631068` |
| `runtime_api_duration_ns_total` | `19922703` |
| `driver_api_duration_ns_total` | `10808810` |
| `runtime_api_record_count` | `513` |
| `driver_api_record_count` | `516` |

## NCU 对标口径

| NCU 维度 | 当前覆盖 | 本硬件替代表达 | 可用字段 |
|---|---|---|---|
| 总体吞吐 | `weak` | SPE / pipe / ALU-FPU-VPU 相关吞吐与发射信号 | `kernel_duration_ns_avg`, `slave__inst_executed`, `slave__inst_launched`, `alu__pipe0_inst_integet_op_executed`, `alu__pipe1_inst_integet_op_executed`, `vpu__inst_vector_integet_op_executed` |
| 内存层级 | `weak` | LDM / global / DMA / icache 层面的弱对应 | `derived_icache_miss_rate`, `derived_local_memory_access_per_inst`, `derived_global_load_access_per_inst`, `derived_dma_requests_per_inst` |
| 调度 | `partial` | pipe0/pipe1 launch / zero-launch / cannot-launch | `derived_zero_launch_ratio`, `derived_launch_zero_latency_ratio`, `derived_pipe0_zero_latency_ratio`, `derived_pipe1_zero_latency_ratio`, `derived_pipe0_cannot_launch_per_launch`, `derived_pipe1_cannot_launch_per_launch`, `derived_pipe0_launch_share`, `derived_pipe1_launch_share` |
| stall | `partial` | icache miss、LDM wait、cannot-launch、sync/memb wait | `l1ic__icache_miss_cycles`, `derived_local_memory_unarb_cycles_per_inst`, `slave__syn_wait_cycles`, `slave__memb_wait_cycles`, `slave__pipe0_inst_cannot_launch`, `slave__pipe1_inst_cannot_launch_cycles` |
| 访存形态 | `weak` | global/local/vector access 密度 | `derived_global_load_access_per_inst`, `derived_global_store_access_per_inst`, `derived_local_memory_access_per_inst`, `derived_vector_memory_access_per_inst` |
| shared memory | `weak` | LDM / local memory，当前没有 bank conflict 直接指标 | `derived_local_memory_access_per_inst`, `derived_pipe_local_memory_access_per_inst`, `derived_local_memory_unarb_cycles_per_inst`, `derived_local_memory_violate_cycles_per_inst` |
| 资源 | `missing` | 当前缺少 registers / occupancy / spills 等直接指标 | - |

## 按 T1 文档仍缺的运行时字段

- `dma_stride_bytes / dma_access_pattern`: 当前还无法区分块划分、周期划分和跨步模式；这会影响对 HBM 通道打满程度的判断。
- `concurrent_dma_queue_depth`: T1 文档提到 DMA 读写共队列且队列长度经验值约 11；没有这个字段，难以判断是否触发队列拥塞。
- `rma_mode / broadcast_mode`: 若后续算子使用 RMA/行列广播，这些字段能帮助判断是不是更适合点对点、列广播或双对角线广播。
