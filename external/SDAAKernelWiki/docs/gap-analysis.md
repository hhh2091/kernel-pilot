---
id: docs-gap-analysis
title: "SDAAKernelWiki 面向算子优化生成的缺口分析"
sources: [source-local-hardware-model, source-local-teco-t1, source-local-instruction-latency-pipeline, source-local-rms-metrics-analysis, source-local-ace-cost-table]
---

# SDAAKernelWiki 缺口分析

## 当前覆盖范围

当前 wiki 已经能支撑第一阶段的 SDAA 算子优化推理：

- 硬件词表：SPA、SPE、LDM、DMA、RMA、ACE、pipe0、pipe1、HBM、mesh。
- 数据搬运规则：128B DMA 包、2KB 聚合 HBM channel 目标、全 SPA 视角的周期划分、DMA 队列深度、DMA 奇偶引擎顺序。
- 通信规则：RMA 点对点 vs 广播、行/列广播、双对角线行广播、DMA/RMA 共享路径。
- 计算规则：P0/P1 发射拆分、SIMD 寄存器宽度、长延迟 sqrt/div、ACE 累加器双缓冲和 cost table 查找。
- PMU 分析词表：zero-launch、cannot-launch、local-memory unarb、DMA request density、icache miss、runtime/driver overhead。

## 距离可靠算子优化生成还缺什么

1. **官方编程模型参考**
   - 稳定的 `tecocc`、kernel launch 语法、`__global__`、`__device__`、`__local__`、sync API、DMA/RMA API、ACE API 和约束文档。
   - `rt_ace_load_west`、`rt_ace_writeback`、DMA get/put、RMA get/put/broadcast、sync 变体的精确函数签名。

2. **可运行算子样例**
   - elementwise、reduction、RMSNorm/LayerNorm、memcpy、broadcast、GEMM/ACE matmul、RMA communication 的最小正确 kernel。
   - 每个样例都应包含 K/R/W、构建命令、正确性 oracle 和 benchmark 命令。

3. **Profiler schema 和指标定义**
   - PMU / SDPTI / optest metrics 的规范 JSON schema。
   - `zero_launch`、`cannot_launch`、local-memory unarb、DMA/RMA counter、ACE counter、cycle 归一化和 active-SPE 逻辑的定义。
   - 字段到 pattern 的映射，以及阈值和置信度规则。

4. **ACE cost model 验证**
   - 将 `ACE.xlsx` 转成机器可读的 CSV/JSON。
   - 明确 TFLOPS、cycle、IO_AB、IO_C、writeback、dispatch delay 的单位。
   - 用真实 GEMM / MatMul kernel 在多个 shape 上验证表格预测。

5. **内存映射事实**
   - 确认 HBM 地址映射、channel/bank/row bit field 和 row size 是否随 SKU 或 runtime mode 改变。
   - 构建 microbenchmark，覆盖 128B 对齐、2KB 聚合访问、每 SPE 8/16KB 区间、DMA 奇偶顺序、队列深度限制和 RMA 路线。

6. **代码生成模板**
   - SPE 划分、DMA 双缓冲、RMA 广播选择、ACE tiled matmul、P0/P1 overlap、sync/wait 放置模板。
   - 每个模板都需要明确 knob、合法范围和测量检查项。

7. **KernelPilot loop 集成**
   - KernelPilot 应在 attempt ledger 中记录 SDAAKernelWiki page id。
   - SDAA 任务应先查询本 wiki，再应用 NVIDIA KernelWiki 规则。
   - 优化工作区需要 SDAA 专用脚手架：build script、correctness harness、profiler collection、benchmark parser 和 cost-model helper。

## 推荐补充顺序

1. 固化本 wiki 的 schema 和词表。
2. 将 query / validate 纳入 CI 或本地测试。
3. 将 ACE.xlsx 转成 JSON，并增加 `ace_cost.py` helper。
4. 增加 3 个可运行 seed kernel：memcpy/DMA、RMSNorm、ACE matmul。
5. 增加 profiler parser 和当前 optest JSON 的阈值规则。
6. 增加 KernelPilot SDAA 工作区脚手架和 ledger。
7. 用真实优化尝试记录和性能声明扩展知识库。

## SDAA 算子优化生成的 Ready 标准

系统达到可用状态时，一个新算子请求应能生成：

1. K/R/W 和目标硬件范围。
2. 面向 SPA/SPE/LDM/DMA/RMA/ACE 的第一版候选映射。
3. 带 SDAAKernelWiki 页面引用的预期瓶颈。
4. 可运行的正确性和 benchmark harness。
5. 能将 metrics 映射回 wiki pattern 的 profiler 采集步骤。
6. 基于测量证据的下一步编辑建议。
