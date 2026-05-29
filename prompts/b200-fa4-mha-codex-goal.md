# B200 FA4 MHA Codex Goal 提示词

将此内容作为一个 Codex Goal 提示词复制使用。

```text
/goal 在 NVIDIA B200 的独立优化工作区中实现一个 FA4 可比的 BF16 纯前向 MHA 注意力内核，直到最终正确的实现在配置的 B200 用例上以至少 5% 的几何平均 TFLOPS 击败官方 FlashAttention-4，通过 PyTorch/FP32 预言机正确性检查和来自同一 ion-b200 GPU0 容器的基准测试日志验证。

环境和命令边界：
- 所有 B200 工作请使用 ion-b200 远程 GPU 环境。
- 所有 CUDA、Python、pip、nvcc、构建、测试、基准测试和 Nsight Compute
  命令必须在 ion-b200 上现有的 sglang_bbuf Docker 容器内运行，
  并选择 GPU0。
- 远程执行请使用以下命令模式：

  ssh ion-b200 'docker exec sglang_bbuf bash -lc "CUDA_VISIBLE_DEVICES=0 <command>"'

- 不要直接在 ion-b200 主机上运行 Python、pip、nvcc、构建、测试、基准测试或性能分析。
- 不要在主机上 pip install flash-attn。容器中已经安装了
  FlashAttention-4；将其作为主要性能基线使用。

目标范围：
- 不要调用 Humanize 内核代理循环、RLCR 或 `/humanize`；这是一个
  Codex Goal 工作流。
- 在独立优化工作区中构建候选方案，该工作区有自己的
  构建、测试框架、基准测试脚本、源码谱系记录和调度路径。
- "独立"不意味着干净室或从零开始。不要从候选执行路径中调用官方
  FlashAttention-4，但公开/参考内核源码可以在许可证兼容且已记录的情况下
  被研究、复制、移植、改编或简化。
- 仅前向传播。
- 无反向传播。
- 无 GQA。
- 无服务或框架集成。

工作负载：
- 操作类型：稠密多头注意力前向。
- dtype: BF16。
- head_dim: 128。
- num_heads: 16。
- total tokens: 32768。
- 基准测试用例：
  - batch=8, seqlen=4096
  - batch=4, seqlen=8192
  - batch=2, seqlen=16384
  - batch=1, seqlen=32768
  - 同时测试 causal=false 和 causal=true。

实现源策略：
- 此次运行为基线感知的内核演化，而非盲目内核合成。
- 将官方 FlashAttention-4、CUTLASS/CuTe SM100 示例、TileLang
  内核和其他公开 Blackwell 注意力内核视为参考和移植材料。可以在许可证兼容的情况下研究或用作
  CUDA/C++/CUTLASS/CuTe 移植和规范辅助代码的源码。
  请记录确切的源路径、提交或安装版本，以及改编了什么。
- 最终候选实现必须是从工作区自有的 C++/CUDA 源码构建的原生 CUDA 内核，
  例如使用 nvcc 或等效 CUDA 扩展构建编译的 `.cu`、`.cuh`、`.cpp` 或 `.h`
  文件。Python 允许用于测试框架、绑定、基准测试脚本和调度粘合代码，但
  不能作为主要内核实现。
- 不要使用官方 FlashAttention-4、`flash_attn.cute.flash_attn_func`、
  `FlashAttentionForwardSm100`、在 FA4 CuTe DSL 内核类上使用 Python `cute.compile`、
  TileLang、Triton、torch SDPA 或任何其他预构建注意力算子
  作为候选执行路径。这些源码只能被检查或移植到本工作区拥有的原生 C++/CUDA/CUTLASS/CuTe 代码中。
- 第一个面向性能的候选方案应为基线派生或规范辅助派生，除非有测量依据表明不应如此。
  原始内核仅可作为测试框架/正确性冒烟测试，而不能作为主要优化谱系。
- 当存在官方或事实上的规范辅助时，不要手工推导 tcgen05 SmemDescriptor 编码、TMEM 布局、TMA
  重排、warpgroup 同步协议或 Blackwell MMA 指令包装器。优先移植辅助并通过微用例验证。
- 使用 CUDA C++、CUTLASS/CuTe C++ 模板、生成的 CUDA 辅助代码和
  可选内联 PTX，当它们使 Blackwell 特定细节更可靠时。

验证表面：
- 在优化声明之前，在同一 ion-b200 GPU0 容器中建立不可变的官方 FlashAttention-4 基线。
- 匹配 BF16 Q、K 和 V 在 head_dim=128 下的标准缩放点积注意力前向语义。
- 仅在 causal=true 时应用因果掩码。
- 在内核中使用数值稳定的在线 softmax/LSE 兼容公式。
- 将 PyTorch/FP32 注意力作为语义正确性预言机。官方
  FlashAttention-4 是性能基线和有用的交叉检查，但它也是一个具有自己归约顺序的分片 BF16 实现。
- 不要对所有用例使用固定的 5e-3 绝对差异作为 FA4 的硬正确性门槛。
  在可行时使用 SGLang 风格的动态数值边界：将候选方案相对于 PyTorch/FP32 预言机的误差
  与 PyTorch BF16 或重排序 BF16 参考的误差进行比较，并要求候选方案保持在该数值误差规模的小倍数内，
  同时通过 NaN/Inf 检查。
- 如果测试框架无法廉价计算动态边界，请将语义通过/失败门槛保持在
  PyTorch/FP32 预言机上，并将 FA4 比较用作诊断证据。可以使用放松的 FA4 交叉检查（如 abs <= 2e-2 和 rel <= 0.10）来
  捕获严重偏差，但应将其记录为方法论而非语义预言机。
- 最终候选方案必须通过正确性检查，基准测试声明才有效。
- 尽可能遵循 Dao-AILab/flash-attention benchmarks/benchmark_attn.py 方法论，
  包括预热和重复逻辑。
- 报告每个用例的平均延迟、标准差、TFLOPS 和几何平均 TFLOPS。
- 将基准测试脚本和原始结果日志保存在工作区中。
- 在记录第一个基线后，不要更改 FA4 基线、基准测试公式、预热/重复策略或
  目标用例，除非用户明确要求更改方法论。如果发现基准测试 bug，请记录
  前后方法论。

允许的知识和性能分析工具：
- 当先前的 B200、SM100、FlashAttention-4、CUTLASS、CuTe、
  TileLang 或注意力内核证据可以指导设计选择时使用 KernelWiki。
- 当正确的候选方案未明显达到目标或性能分析证据将改变下一步编辑时，
  使用 ncu-report-skill / Nsight Compute。
- 在尝试手写 Blackwell 原语之前，检查相关的上游/参考实现
  并记录此次运行为移植、简化还是刻意避免。包装或导入上游
  Python/DSL 内核对象不是有效的候选实现。

迭代策略：
- 首先确定官方 FA4 源路径/版本、至少一个可检查和移植的规范
  Blackwell 辅助源、基线命令、正确性命令、基准测试命令、第一个候选方向、
  主要风险和提升证据。
- 建立证明测试框架所需的最小正确性冒烟测试，
  然后立即转向基线派生或规范辅助派生的性能候选方案。
- 不要花费多轮优化一个结构上无法接近 FA4 的原始谱系。
- 如果一个正确的候选方案在一次具备张量核心能力的尝试后比官方 FA4 慢 3 倍以上，
  请停止对该谱系的局部微调，并重置为更强的原生 CUDA/CUTLASS/CuTe 移植父版本。
- 如果一个张量核心/TMEM/tcgen05 微用例在两次聚焦迭代后仍不正确，
  请停止手工推导该路径，转而使用规范辅助提取或不同的父实现。
- 考虑 B200/SM100 特定特性和注意力模式，如 TMA、
  有用的 TMEM、tcgen05/张量核心 MMA 选择、warp 特化、
  持久调度、split-Q 或 split-K 调度、在线 softmax/LSE、
  因果掩码效率、向量化 BF16 内存流量以及占用率与寄存器压力权衡。
- 当测量证据表明不同的序列长度或因果模式需要不同的 CTA、
  warpgroup、TMEM 或寄存器压力权衡时，允许使用形状特化内核、模板/配置变体、
  因果/非因果路径以及调度器或自动调优表。
- 最终评分可以使用每个配置用例的最快正确变体，但
  每个调度的变体必须通过其分配用例的正确性检查。
- 每个候选方案后，记录名称、父版本、更改的文件、假设、
  正确性结果、每个用例的基准测试结果、收集的性能分析证据（如有）、
  提升/拒绝原因以及下一个最佳实验。保留性能图
  和谱系记录，以便未来的工程师可以重建选定的路径。

完成标准：
- 仅当最终正确的实现在同一 GPU0 容器中所有配置的 B200 用例上
  以至少 5% 的几何平均 TFLOPS 击败官方 FlashAttention-4，且基准测试日志和
  正确性结果已保存时，才标记 Goal 完成。
- 如果基准测试无法运行、正确性无法验证或在可用工作区中没有可信的
  FA4+5% 路径，请停止并提交报告，将确认的结果、最佳正确候选方案、失败的方向、
  阻塞因素、剩余不确定性以及将解锁进展的下一个源材料或性能分析证据分开列出。
- 最终报告必须包含 FlashAttention-4 基线数值、最终数值、
  几何平均 TFLOPS、正确性容差、构建/测试/基准测试命令、源码谱系和关键设计决策。
```
