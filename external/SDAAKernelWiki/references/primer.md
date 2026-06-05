# SDAAKernelWiki Primer

回答较宽泛的 SDAA / TECO T1 优化问题前，先用这个 topic map 快速定位页面。

## 硬件页面

| 主题 | Page ID | 路径 | 说明 |
|---|---|---|---|
| SPA/SPE 拓扑 | `hw-spa-spe` | `wiki/hardware/spa-spe.md` | 单 SPA = 32 SPE，4 x 8 排布；当前分析从单 SPA 出发。 |
| LDM 本地存储 | `hw-ldm` | `wiki/hardware/ldm.md` | 每 SPE 256 KB，两个 128 KB bank；不是 NVIDIA shared memory。 |
| SDAA 存储模型 | `hw-sdaa-memory-model` | `wiki/hardware/sdaa-memory-model.md` | Host、Global、SPM 及 SPM heap/stack/local 规则。 |
| DMA 引擎模型 | `hw-dma` | `wiki/hardware/dma.md` | 8 个按列绑定的 DMA 引擎；每个引擎对应 4 个 SPE；128B PPU 包。 |
| RMA Mesh 通信 | `hw-rma` | `wiki/hardware/rma.md` | 2D mesh，节点全双工；路线/节点冲突重要。 |
| ACE 矩阵单元 | `hw-ace` | `wiki/hardware/ace.md` | 1.25 GHz 矩阵/异步单元，带双累加器缓冲。 |
| HBM channel-bank-row | `hw-hbm-channel-bank-row` | `wiki/hardware/hbm-channel-bank-row.md` | 16 channel、128B channel 单元、行局部性约束。 |
| pipe0 / pipe1 | `hw-pipe0-pipe1` | `wiki/hardware/pipe0-pipe1.md` | P0 偏计算，P1 偏访存/控制/DMA/RMA/ACE/sync。 |

## 技术页面

| 技术 | Page ID | 适用场景 |
|---|---|---|
| 周期式划分 | `technique-dma-periodic-partitioning` | 让 32 个 SPE 合起来访问更连续的 HBM 区间，而不是单 SPE 块状访问。 |
| DMA 奇偶交错 | `technique-dma-odd-even-interleave` | 测试经验引擎顺序 `(0,2,4,6,1,3,5,7)`。 |
| DMA 队列预算 | `technique-dma-queue-budgeting` | 将 outstanding DMA 读写请求控制在经验队列深度附近。 |
| SDAA DMA API | `technique-sdaa-dma-api` | 官方 DMA / stride / async API 约束。 |
| SDAA RMA/Broadcast API | `technique-sdaa-rma-broadcast-api` | 官方 SPE 间 SPM 传输与广播接口约束。 |
| SDAA MatMul API | `technique-sdaa-matmul-api` | 阻塞/非阻塞 matmul、SPM 对齐和 GEMM 生成约束。 |
| SDAA SIMD | `technique-sdaa-simd-vectorization` | 显式向量类型、SIMD intrinsic 和 tail 处理。 |
| 性能采样 | `technique-sdaa-perf-sampling` | `sdaa_perf.h` 的 hot-section cycle 采样入口。 |
| Atomic | `technique-sdaa-atomic-api` | atomic add/sub/cas/inc 与 reduction fallback。 |
| Transpose | `technique-sdaa-transpose-api` | 同步/异步 transpose 与 layout transform。 |
| 数学/高层接口 | `technique-sdaa-math-and-high-level-api` | math、batch math、activation、reduction 的生成入口。 |
| RMA 广播选择 | `technique-rma-broadcast-selection` | 选择点对点、列广播、双对角线行广播或跨步列广播。 |
| ACE 双缓冲 | `technique-ace-double-buffering` | 重叠 ACE 计算和 writeback。 |
| P0/P1 overlap | `technique-p0-p1-overlap` | 通过交错计算和访存/控制工作减少 issue 空泡。 |

## 诊断模式

| 症状 | 模式页面 | 候选技术 |
|---|---|---|
| zero-launch 或 cannot-launch 偏高 | `pattern-scheduling-bubbles` | P0/P1 overlap、wait 放置、profiler 交叉验证 |
| local-memory access / unarb 偏高 | `pattern-ldm-pressure` | LDM locality、bank-aware layout、double buffering |
| DMA requests 低但耗时差 | `pattern-dma-hbm-underutilization` | 周期划分、128B/2KB 对齐、DMA 奇偶交错 |
| RMA + DMA 冲突 | `pattern-rma-contention` | RMA put 优先、广播模式选择、避免共享返回路径冲突 |
| ACE 低于 roofline | `pattern-ace-feeding-writeback` | ACE 双缓冲、west/north feeding 平衡、ACE 表查找 |
| 编译或 CUDA 迁移失败 | `pattern-sdaa-compile-porting-errors` | TecoCC、`.scpp`、LTO、CUDA block/warp/shared memory 翻译 |

## 算子案例

| 算子 | Page ID | 说明 |
|---|---|---|
| RMSNorm / RMSLayerNorm | `kernel-rmsnorm-pmu-analysis` | 展示调度空泡、部分 SPE 激活、LDM 压力和 DMA 未饱和。 |
| GEMM / MatMul | `kernel-sdaa-gemm` | 从 baseline、SIMD、matmul/ACE、Broadcast 到 double buffering 的生成路线。 |
| 算子开发 | `kernel-sdaa-operator-development` | 将 PDF 算子开发指南映射成 KernelPilot K/R/W、build、benchmark 和 ledger。 |

## 官方编程指南导入页

| 主题 | Page ID | 说明 |
|---|---|---|
| SDAA C 指南来源 | `doc-sdaa-c-programming-guide-v3-1-0` | 671 页 PDF 的结构化摘要来源页；PDF 原件不保留。 |
| Quickstart | `example-sdaa-quickstart` | `.scpp`、`tecocc`、launch、sync 的最小 smoke test。 |
| SDAA C 语言 | `lang-sdaa-c-programming-guide` | kernel launch、关键字、数据类型、头文件、device 限制。 |
| Host Runtime | `runtime-sdaa-host-api` | device、memory、copy、sync 和 stream API。 |
| 环境变量/调试 | `runtime-sdaa-env-and-debug` | `SDAA_SYNC_PRINT`、printf/assert/abort、device info、TecoGDB、sdaacfilt。 |
| TecoCC / Debug | `compiler-tecocc-build-debug` | 编译、LTO、CMake、TecoGDB、sdaacfilt。 |
| CUDA 迁移 | `migration-cuda-to-sdaa-c` | 将 grid/block/warp/shared memory 翻译到 SDAA。 |
| 指南示例集合 | `example-sdaa-programming-guide-examples` | 向量、SPMD 矩阵乘、SUMMA、自定义 atomic 和算子示例路线。 |
