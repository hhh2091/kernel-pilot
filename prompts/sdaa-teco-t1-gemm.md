# SDAA TECO T1 GEMM KernelPilot 提示词

将此内容作为一个端到端提示词复制使用。

```text
/humanize:humanize-kernel-agent-loop

所有 SDAA 工作请使用当前本机太初显卡环境。不要把任务改写为 CUDA、
NVIDIA、Nsight Compute、B200 或远程 ion-b200 任务。所有编译、测试、
基准测试和性能分析命令必须在当前 SDAA 主机上运行，并选择设备 0。

目标设备快照：
- 采集时间：Thu Jun 4 15:22:29 2026
- TECO-SMI：1.15.0
- SDAADriver：3.1.0
- SDAARuntime：3.1.0
- GPU Index：0
- GPU Name：TECO_AICARD_01
- Bus-Id：00000000:0F:00.0
- Health：OK
- SPE-Util：0%
- Memory：0MB / 65536MB
- 温度/功耗：35C / 87W

环境规则：
- 运行前先执行 `teco-smi` 并把完整输出保存到
  `profile-artifacts/environment/teco-smi.txt`。
- 探测并记录本机 SDAA 工具链：编译器、运行时库、头文件、示例代码、
  profiler、计时 API、设备选择环境变量和 BLAS/GEMM 库。不要猜测命令名。
- 不要安装、升级或重装 SDAA Driver、SDAARuntime、内核模块或系统级工具。
- 如果实际工作必须在容器中运行，先发现现有容器和挂载方式，再记录使用原因；
  不要新建未经用户确认的远程环境。
- 不要把 CUDA API、nvcc、Triton、CUTLASS、cuBLAS、torch CUDA 或 Nsight
  Compute 放到候选执行路径中。它们只能作为概念参考，不能作为 SDAA 目标实现。

任务契约：
- 任务名称：SDAA TECO T1 GEMM 端到端优化生成种子任务
- 目标算子：GEMM
- 语义：`C = A @ B`
- 默认布局：A、B、C 均为 row-major，A 形状为 `[M, K]`，
  B 形状为 `[K, N]`，C 形状为 `[M, N]`。
- 默认转置：不转置。
- 默认附加项：无 bias、无 activation、无 batch、无 split output。
- 默认 dtype 策略：先建立 FP32 正确性和基准框架；随后探测 SDAA/ACE
  是否支持 FP16、BF16、TF32 或 INT8 GEMM 路径。如果工具链和硬件文档证实支持，
  增加一个低精度高吞吐主线，但不要牺牲 FP32 参考验证。
- 最终产物：一个可由 KernelPilot 继续迭代的 SDAA GEMM 工作区，
  包含源代码、构建脚本、正确性测试、基准测试、性能地图、记录簿和知识库引用。

循环引导：
- 在实现内核候选方案或运行长时间基准测试之前，确保 Humanize RLCR
  循环在选定工作区中处于活动状态。
- 工作区必须是一个 git 仓库，并包含一个干净的脚手架提交。
- 确认 `.humanize/rlcr/<timestamp>/state.md` 存在，并且循环使用
  `--strict-success` 启动。如果 RLCR 未启动，请停止并报告设置失败，
  不要在循环外继续优化。
- Round 0 必须在编辑内核之前输出短计划，列出：工具链发现命令、
  基线命令、正确性命令、基准测试命令、第一条候选谱系、主要风险和预期收益证据。

K/R/W 输入契约：
- K：SDAA GEMM 候选实现，优先使用本机 SDAA C/C++/设备端编程接口、
  官方示例或现有项目中的 SDAA kernel 模式。
- R：CPU FP64 或 FP32 参考实现；如果 Paddle SDAA、vendor BLAS 或
  其他 SDAA 框架 GEMM 可用，可作为交叉检查和性能基线，但不能替代 CPU 语义参考。
- W：固定的 GEMM 工作负载集合，覆盖小矩阵、方阵、长瘦矩阵、短胖矩阵和大矩阵。

默认工作负载：
- square_512：M=512, N=512, K=512
- square_1024：M=1024, N=1024, K=1024
- square_2048：M=2048, N=2048, K=2048
- square_4096：M=4096, N=4096, K=4096
- tall_narrow：M=4096, N=128, K=4096
- wide_short：M=128, N=4096, K=4096
- mlp_up：M=1024, N=8192, K=2048
- mlp_down：M=8192, N=1024, K=2048
- large_square_optional：M=8192, N=8192, K=8192，仅当单次测试时间和显存占用可控时加入最终评分。

工作负载规则：
- 前 8 个用例是默认评分集。不要在记录第一个基线后修改评分集。
- 可以添加诊断 microbench 或 tile sweep，但必须和评分集分开记录。
- 如果某个形状因工具链或内存限制不可运行，记录精确失败原因、命令和日志；
  不要静默删除该形状。

基线：
- 必须建立至少两个基线：
  1. CPU 参考正确性基线。
  2. SDAA 侧性能基线。优先级为：vendor GEMM/BLAS 或框架 GEMM、
     现有 SDAA 示例 GEMM、朴素 SDAA GEMM。
- 如果 vendor GEMM/BLAS 存在，把它作为强基线和性能上界参考。
- 如果没有 vendor GEMM/BLAS，先实现一个朴素但正确的 SDAA GEMM，
  并将其作为可复现优化基线。
- 在记录第一个基线后，不要更改计时公式、预热次数、重复次数、评分形状或
  GFLOPS/TFLOPS 计算公式，除非发现明确 bug；如果修复 bug，必须在记录簿中保留前后方法论。

正确性：
- 与 CPU 参考逐形状比较。
- 每次验证都报告 max_abs_error、max_rel_error、mean_abs_error、NaN/Inf 检查结果和容差。
- FP32 默认容差建议从 `abs <= 1e-3`、`rel <= 1e-3` 开始，
  但可根据 K 维累加误差用证据调整。
- FP16/BF16/INT8 路径必须有独立容差说明，并说明累加类型、输出类型和量化/反量化语义。
- 最终候选必须先通过正确性检查，性能声明才有效。
- 不要削弱正确性测试、改变参考语义或缩小输入范围来让候选通过。

基准测试：
- 每个形状至少包含 warmup、repeat、同步、异常值检查和原始日志。
- 报告 median、mean、std、min、p10、p90、GFLOPS/TFLOPS、相对基线加速比。
- 对 GEMM 使用 `2 * M * N * K` FLOPs 计算吞吐。
- 记录设备空闲状态、温度、功耗、SPE-Util 和显存占用快照。
- 将脚本保存在 `benchmarks/`，将原始结果保存在 `profile-artifacts/`，
  将汇总表保存在 `benchmarks/performance-map.json`。

SDAAKernelWiki 使用要求：
- 每轮优化前查询 `external/SDAAKernelWiki`，并在记录簿中写入使用过的 page id。
- 至少检查以下页面或等价查询结果：
  - `source-local-teco-t1`
  - `hw-spa-spe`
  - `hw-ace`
  - `hw-dma`
  - `hw-hbm-channel-bank-row`
  - `hw-pipe0-pipe1`
  - `technique-ace-double-buffering`
  - `technique-dma-periodic-partitioning`
  - `technique-dma-odd-even-interleave`
  - `technique-dma-queue-budgeting`
  - `pattern-ace-feeding-writeback`
  - `pattern-dma-hbm-underutilization`
- 推荐命令：
  `python3 external/SDAAKernelWiki/scripts/query.py "GEMM ACE DMA HBM" --compact`
  `python3 external/SDAAKernelWiki/scripts/get_page.py hw-ace`
  `python3 external/SDAAKernelWiki/scripts/get_page.py technique-ace-double-buffering`
- 如果本地知识库与实际工具链冲突，以实测和工具链文档为准，并把冲突写入
  `ledgers/sdaa-wiki-feedback.md`，用于后续补充 SDAAKernelWiki。

SDAA 优化指导：
- 第一阶段先做可观测性：确定 kernel launch、device memory、LDM/shared local memory、
  DMA、ACE、SPE/SPA片上层级、同步和计时 API 的真实写法。
- 第二阶段做可正确运行的朴素 GEMM：每个候选都要能被测试、计时和回滚。
- 第三阶段做 tile 化和数据搬运优化：显式评估 M/N/K tile、LDM 占用、
  寄存器压力、SPE 并行度、访存对齐和输出写回。
- 第四阶段探索 ACE 路径：如果 ACE GEMM 或矩阵指令可用，优先建立
  ACE microbenchmark，再接入 GEMM 主线。
- 优先考虑双缓冲或流水化，让 DMA 搬运、ACE/计算和 writeback 重叠。
- 对 DMA/HBM 相关候选，检查 128B 对齐、连续访问、2KB 聚合搬运、
  per-SPE 4KB/8KB/16KB 搬运粒度、奇偶 DMA 引擎交错和队列深度预算。
- 对 HBM bank/channel 敏感形状，尝试 stride、tile leading dimension、
  分块顺序和 SPE 映射，避免所有 SPE 同步打到同一 HBM 热点。
- 对小 M 或小 N 形状，不要盲目套大方阵 tile；允许形状特化 kernel
  或调度表。
- RMA 只在跨 SPE 数据复用收益明确时使用；如果与 DMA/HBM 竞争导致退化，
  记录证据并回退。

实现源策略：
- 这次运行是 SDAA 目标上的算子优化生成，不是 CUDA 移植任务。
- 可以研究公开 GEMM、BLAS、Paddle custom device、SDAA 示例或本仓库知识库，
  但最终候选执行路径必须由当前工作区中的 SDAA 目标源码构建。
- 可以保留多个候选谱系：naive、tiled、DMA staged、ACE accelerated、
  shape-specialized、scheduler/autotune。
- 允许按形状调度多个正确候选；最终评分可使用每个形状最快的正确变体，
  但调度规则必须可复现并写入 `dispatch/` 或 `benchmarks/performance-map.json`。

记录簿要求：
- `ledgers/lineage.jsonl`：每个候选一行，包含名称、父候选、
  改动文件、假设、知识库 page id、正确性结果、基准结果和保留/拒绝原因。
- `ledgers/rejected-ideas.md`：记录失败方向，尤其是正确性失败、只赢单个形状、
  DMA 退化、ACE feed 不足或 writeback 瓶颈。
- `ledgers/sdaa-toolchain.md`：记录工具链、编译参数、运行时路径、设备选择方式、
  profiler 使用方式和环境变量。
- `benchmarks/performance-map.json`：记录每个形状的 CPU 参考、SDAA 基线、
  当前最佳候选、加速比、吞吐和选择原因。

阶段策略：
- Phase 1：环境发现、脚手架、CPU 参考、SDAA baseline、固定评分集和正确性测试。
- Phase 2：朴素 SDAA GEMM 到 tiled GEMM，确保每次优化都有基准证据。
- Phase 3：DMA/LDM/HBM 调优，围绕数据搬运和 SPE 利用率建立 microbench 证据。
- Phase 4：ACE 加速路径；先验证矩阵微内核，再接入完整 GEMM。
- Phase 5：按形状调度、autotune 表和最终全量评分。
- 如果一个方向连续五次聚焦迭代仍无法正确或没有可信改进，记录证据后切换方向。

验收目标：
- 硬性验收：
  1. 所有默认评分形状都有正确性结果。
  2. 所有可运行评分形状都有 SDAA baseline 和最终候选性能。
  3. 最终候选在默认评分集上的几何平均延迟必须比朴素 SDAA baseline
     至少快 2 倍。
  4. 如果 vendor GEMM/BLAS 可用，必须报告最终候选相对 vendor baseline
     的几何平均差距；如果不能超过 vendor baseline，必须说明差距来自
     compute、DMA、HBM、writeback、调度还是工具链限制。
- 拉伸目标：
  - 在至少一个代表性大矩阵或 MLP 形状上接近 vendor GEMM/BLAS 的 80%
    或超过 vendor baseline 5%，以实测为准。
  - 形成可复用的 SDAA GEMM 生成模板，让后续算子优化任务能够复用
    build/test/benchmark/ledger/dispatch 结构。

完成：
- 继续迭代，直到硬性验收全部满足，或至少六次实质性、有记录的候选尝试
  证明当前工具链或硬件资料缺口阻塞了目标。
- 不要用“尽力而为”替代正确性和基准证据。
- 最终报告必须包含：环境快照、工具链版本、评分形状、基线数值、最终数值、
  几何平均加速比、相对 vendor baseline 差距、正确性容差、构建/测试/基准命令、
  使用过的 SDAAKernelWiki page id、关键设计决策、仍缺的 SDAA 资料和下一步补充计划。
```
