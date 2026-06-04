# optest-agent 当前硬件模型口径

本文档用于统一 `optest-agent` 当前阶段的硬件分析口径。目标不是给出最终官方微架构说明，而是明确：

- 当前已经能确认的硬件组成。
- 当前 JSON / PMU 字段应该按什么硬件语义解释。
- 哪些概念可以借用 NCU 风格分析，哪些不能直接照搬。

## 1. 当前确认的硬件组成

### 1.1 顶层结构

- T1 芯片包含 `4` 个核组 `SPA`。
- 每个 `SPA` 独占一块 `HBM (16GB)`。
- 当前算子性能分析先聚焦单 `SPA` 视角。

### 1.2 单 SPA 结构

- 单 `SPA` 规模为 `4 x 8 = 32 SPE`。
- 当前分析时可把 `SPE` 视为最基础的执行核心。
- `SPE` 当前主频参考为 `2.5 GHz`。
- `ACE` 当前主频参考为 `1.25 GHz`，为 `SPE` 半频域。

### 1.3 执行与管线

- 当前执行模型口径为：`2 译码 - 2 发射 - 2 写回` 的超标量乱序执行。
- 当前至少存在两条主要发射/执行管线：`pipe0`、`pipe1`。
- `P0` 更偏计算类指令。
- `P1` 更偏访存、控制、DMA/RMA/ACE、同步类指令。
- `DMA`、`RMA`、主存访问、远程 `LDM` 访问、`ACE` 执行都应视为“不定延迟”。

### 1.4 存储与搬运

- 每个 `SPE` 具有 `256 KB LDM`。
- `LDM` 可按两个 `128 KB` bank 理解。
- `DMA` 引擎按列绑定，不是按行绑定。
- 单 `SPA` 为 `8` 列，因此有 `8` 个按列共享的 `DMA` 引擎。
- 每列 `4` 个 `SPE` 共享同一个 `DMA` 引擎。
- HBM 访问至少要考虑：
  - `32 B` 最小粒度
  - `128 B` PPU 包大小
  - 通道 / bank / row 切换成本

### 1.5 可见计算单元

- `ALU`：整数计算。
- `FPU`：标量浮点。
- `VPU`：向量计算。
- `ACE`：异步加速 / 矩阵相关单元。
- `LSU`：load/store 路径。
- `DMA` / `RMA` / `IO`：数据搬运与远程访问路径。
- `L0IC` / `L1IC`：指令缓存相关路径。

## 2. 当前 PMU 字段的硬件解释

`optest-agent` 当前采到的 PMU 字段，应优先按下面的硬件语义解释：

- `slave__*`
  - 以 `SPE` 核心侧执行、发射、local memory、同步、arbiter、DMA/RMA/IO 活动为主。
- `alu__*`
  - 整数计算路径。
- `fpu__*`
  - 标量浮点路径。
- `vpu__*`
  - 向量计算/向量访存路径。
- `lsu__*`
  - global/local/remote load-store 路径。
- `dma__*`
  - DMA 请求与仲裁相关。
- `rma__*`
  - 远程内存访问请求与仲裁相关。
- `l0ic__*` / `l1ic__*`
  - 指令缓存访问、miss 与相关等待。

## 3. 与 NCU 风格指标的对应原则

当前可以借用 NCU 风格“分析维度”，但不能直接照搬 NVIDIA 术语。

### 3.1 可以借用的分析维度

- 总体吞吐
- 内存层级
- 调度
- stall
- 访存形态
- 资源

### 3.2 不能直接照搬的术语

下面这些术语当前不应直接作为本硬件的原生概念输出：

- `SM`
- `warp`
- `Eligible Warps`
- `shared memory bank conflict`
- `occupancy`
- `waves/SM`
- `L1TEX`

### 3.3 当前应替换成的硬件本语

- `SM throughput` -> `SPE / pipe / ALU/FPU/VPU/ACE` 相关吞吐
- `scheduler / eligible warps` -> `pipe0/pipe1 launch / cannot_launch / zero_launch`
- `shared memory` -> `LDM / local memory`
- `global/shared access` -> `HBM/global memory / local memory / remote LDM`
- `tensor pipe` -> `ACE` 或向量/矩阵相关执行路径

## 4. 指令级分析口径

当前静态指令分析只可用于“估算热点方向”，不能单独作为瓶颈证据。

### 4.1 当前重点关注

- `P0` 计算压力
  - 向量浮点
  - 标量浮点
  - 整数向量/标量
  - `sqrt` / `div`
- `P1` 访存与控制压力
  - LDM load/store
  - DMA/RMA
  - 分支
  - `MEMB`
  - `SYNC/SYNR/SYNP`

### 4.2 特别注意

- `FSQRTS` / `FDIVS` 属于长拍且非完全流水。
- `MEMB` 会阻断后续指令继续发射。
- `DMA` / `RMA` / `ACE` 的延迟不能只靠“拍数表”推断，必须结合 profiler 或 PMU。

## 5. ACE 参考表当前用法

`ACE.xlsx` 当前包含以下工作表：

- `TFLOPS`
- `Cycle`
- `IO_AB`
- `IO_C`
- `write half`
- `下发_delay`

当前可将其理解为按 `m`、`k` 维度组织的 `ACE` 实测或经验表，用途主要是：

- 构建 `ACE` cost model。
- 做 roofline / 理论上限对比。
- 做 `ACE` 相关 shape-aware 估算。

当前不应把它当作：

- 真实运行时 PMU。
- 当前 kernel 的直接硬件采样结果。

## 6. 当前能确认与不能确认的边界

### 6.1 当前可以确认

- 单 `SPA = 32 SPE` 的分析口径。
- `DMA` 按列共享。
- `LDM` 是核心级本地存储。
- `pipe0 / pipe1` 是主要调度/发射观察窗口。
- `ACE` 是独立于普通 `SPE` 计算路径的重要单元。
- 当前 JSON 里的 `ALU/FPU/VPU/LSU/DMA/RMA/L0IC/L1IC/slave` 前缀是有硬件含义的。

### 6.2 当前还不能讲死

- 当前设备是否完整等价于某一份运行时头文件里的所有细节定义。
- `ACE` 的最终官方可观测指标全集。
- 是否存在可稳定暴露给用户的 `occupancy` 等价定义。
- 是否存在与 GPU `shared memory bank conflict` 一一对应的官方指标。
- 数据 cache / L2 层级在当前工具链里能否被稳定、直接采集。

## 7. 对 optest-agent 的直接约束

- 后续性能分析一律优先使用 `SPE/LDM/pipe/DMA/RMA/ACE` 这套口径。
- 在没有官方定义前，不输出 GPU 风格的 `warp/SM/shared-memory bank conflict/occupancy` 结论。
- `derived_*` 指标优先解释成：
  - 发射是否顺畅
  - 本地存储/全局存储/远程访问活跃度
  - 指令缓存是否有明显问题
  - DMA/RMA/IO 是否偏重
- 若后续需要对标 NCU 风格视图，应输出：
  - `已覆盖`
  - `弱对应`
  - `缺失`
  - `按本硬件口径的替代解释`
