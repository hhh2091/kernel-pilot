---
id: migration-cuda-to-sdaa-c
title: "CUDA 到 SDAA C 迁移规则"
type: migration
architectures: [sdaa, teco-t1]
tags: [cuda-migration, sdaa-c, spa, spe, spm]
confidence: verified
reproducibility: concept
related: [lang-sdaa-c-programming-guide, hw-spa-spe, hw-sdaa-memory-model]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# CUDA 到 SDAA C 迁移规则

SDAA C 不是 CUDA 的逐项语法替换。迁移时必须先翻译到 SPA/SPE/SPM/DMA/RMA/ACE 模型。

## 线程与 Launch 对照

| CUDA 概念 | SDAA C 等价 | 说明 |
|-----------|------------|------|
| `threadIdx.x` | `threadIdx` | 当前 SPE ID |
| `blockDim.x` | `threadDim` | 当前 SPA 内 SPE 总数 |
| `blockIdx.x` | 无等价物 | 重新设计为数据分片或多 SPA 调度 |
| `gridDim.x` | 无等价物 | 无 Grid 概念 |
| Warp (32 threads) | 无等价物 | 不要迁移 warp-level intrinsic |
| `__shared__` | SPM（`__local__` 或 `malloc`） | SPE 私有片上存储 |
| `cudaStream_t` | `sdaaStream_t` | 通过 `sdaaStreamCreate` 创建 |

### 线程 ID 迁移模式

```c
// CUDA:
for (size_t i = blockIdx.x * blockDim.x + threadIdx.x; i < size; i += blockDim.x * gridDim.x)

// SDAA C:
for (size_t i = threadIdx; i < size; i += threadDim)
```

### Kernel Launch 迁移

```c
// CUDA:
kernel<<<gridDim, blockDim, 0, stream>>>(args...)

// SDAA C:
kernel<<<placeHolder, stream>>>(args...)
// placeHolder 暂无实际含义，可填任意值；stream 可缺省
```

## 内存模型迁移

| CUDA | SDAA C | 关键差异 |
|------|--------|---------|
| Global memory | Global 存储 (16GB/SPA) | 通过 `sdaaMalloc` 分配 |
| Shared memory | SPM heap/local/stack | SPE 私有，不支持跨 SPE 直接访问 |
| Shared memory bank conflict | LDM bank 分析 | 不能直接套用 CUDA bank conflict 规则 |
| Global coalescing | DMA 128B 包 + HBM channel 覆盖 | 翻译为 2KB 聚合 + channel-bank-row 规则 |
| Block 内共享 | RMA/Broadcast 或 per-SPE SPM 副本 | 显式通信，非隐式共享 |

## 不支持迁移的 CUDA 特性

- C++ exception / try-catch
- RTTI、STL、全局对象构造析构
- `new`（用 `sdaaMalloc` 或 SPM `malloc`）
- `__global__` 可变参数
- 线程私有操作、局部静态变量
- C/C++ 原生原子操作（用 `sdaa_atomic.h` 接口）
- 文件 IO、`exit`、`atexit`
- Warp shuffle / warp-level intrinsic

## 编译对照

| CUDA (nvcc) | SDAA C (tecocc) |
|-------------|-----------------|
| `.cu` 文件 | `.scpp` 文件 |
| 默认 GPU 架构 | `--sdaa-arch=pcx_100` |
| `nvcc -arch=sm_xx` | `-O2` 优化级别 |
| PTX/JIT | 默认非 LTO；LTO 用 `-flto --sdaa-link` |

## VSCode 配置

```json
"files.associations": { "scpp": "cpp" },
"C_Cpp.default.forcedInclude": [
    "/opt/tecoai/extras/llvm/lib/clang/11.0.0/include/__clang_sdaa_runtime_wrapper.h"
],
"C_Cpp.default.includePath": [
    "/opt/tecoai/include/",
    "/opt/tecoai/extras/llvm/lib/clang/11.0.0/include/"
],
"C_Cpp.default.defines": ["__SDAA__", "__clang__"]
```

## 迁移规则

1. 先写 SDAA K/R/W，不要从 CUDA launch geometry 机械推导。
2. 用 `threadIdx`/`threadDim` 表达 SPA 内并行。
3. 需要跨 SPE 通信时显式选择 RMA、Broadcast 或 Global staging。
4. CUDA warp reduction 重写成 SIMD lane reduction + SPE group reduction。
5. 每个迁移候选记录替换依据和无法保留的 CUDA 假设。
