# B200 int8_scaled_mm KernelPilot 提示词

将此内容作为一个端到端提示词复制使用。

```text
/humanize:humanize-kernel-agent-loop

所有 B200 工作请使用 ion-b200 远程 GPU 环境。所有 CUDA、Python、
pip、nvcc、构建、测试、基准测试和 Nsight Compute 命令必须在
ion-b200 上现有的 sglang_bbuf Docker 容器内运行，并选择 GPU0。

远程执行请使用以下命令模式：

ssh ion-b200 'docker exec sglang_bbuf bash -lc "CUDA_VISIBLE_DEVICES=0 <command>"'

不要直接在 ion-b200 主机上运行 Python、pip、nvcc、构建、测试、基准测试或性能分析。

任务：
在 NVIDIA B200 上针对以下聚焦用例优化 SGLang 的 int8_scaled_mm 内核：

- M=64
- N=2048
- K=2048
- out_dtype=fp16
- bias=true

目标：
在完全相同的形状、dtype、布局、bias 行为和 B200 GPU0 环境下，以中位延迟击败当前 SGLang 实现至少 2.5 倍。

范围：
- 在当前独立工作区根目录中工作。除非当前目录不可写，
  否则不要创建嵌套仓库。
- 构建可基准测试和可性能分析的 CUDA/C++ 或 CUDA 内联 PTX 候选方案。
- 优化首先聚焦于这个单一形状。
- 除非最小局部测试框架需要用于基线测量，否则不要更改 SGLang 行为或公开 API。

基线：
- 检查当前 SGLang 中 int8_scaled_mm 的实现路径。
- 在优化之前构建可复现的基线测试框架。
- 报告精确聚焦用例的 SGLang 基线延迟。
- 允许可选的辅助基线，如 torch._int_mm 或 fp16 GEMM，
  但验收目标是相对于 SGLang 的。

正确性：
- 与当前 SGLang 结果和 PyTorch 参考（可行时）进行比较。
- 在验证路径中包含 bias。
- 报告最大绝对误差、相对误差和使用的容差。
- 最终候选方案必须通过正确性检查，基准测试声明才有效。

基准测试：
- 使用预热和重复计时。
- 报告中位延迟、平均延迟、标准差、最小值、p10、p90 和相对于
  SGLang 基线的加速比。
- 将基准测试脚本和原始结果日志保存在工作区中。
- 每个声明的改进必须标识候选提交/文件版本和
  用于产生结果的命令。

优化指导：
- 当先前的 B200、SM100、CUTLASS、SGLang 或 int8 GEMM 证据有用时使用 KernelWiki。
- 当候选方案正确但目标未完全达成时使用 Nsight Compute 证据。
- 考虑 B200/SM100 特定路径，如适当时使用 tcgen05 INT8 MMA、TMEM/TMA、
  warp 特化、持久调度、Stream-K 或 split-K、
  集群形状选择、向量化加载/存储、共享内存暂存和
  融合 bias/输出尾声。
- 优先使用证据支持的编辑而非广泛重写。保留已测试变体和被拒绝想法的性能图。

完成：
- 继续迭代，直到最终正确的候选方案在聚焦用例上比 SGLang 基线快至少 2.5 倍，
  或直到至少六次实质性的证据支持尝试表明目标为何受阻。
- 最终报告必须包含基线数值、最终数值、加速比、
  正确性容差、构建/测试/基准测试命令、关键设计决策
  和未达目标时最有前景的后续工作。
```
