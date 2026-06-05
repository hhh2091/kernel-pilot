---
id: lang-sdaa-c-programming-guide
title: "SDAA C 语言规范与 Kernel 编程模型"
type: language
architectures: [sdaa, teco-t1]
tags: [spa, spe, spm, global-memory, simd]
confidence: verified
reproducibility: snippet
languages: [sdaa-c, sdaa-cpp, tecocc]
related: [lang-sdaa-programming-model, hw-sdaa-memory-model, runtime-sdaa-host-api, compiler-tecocc-build-debug]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA C 语言规范与 Kernel 编程模型

本页总结《SDAA C 编程指南 v3.1.0》中对 KernelPilot 最重要的语言规则。它应替代旧页面中“仍缺精确签名”的部分，作为生成 SDAA C skeleton 的首选入口。

## Host-Device 模型

SDAA C 使用 Host-Device 主从异构模型。Host 侧负责设备选择、Global 存储申请、Host/Device 数据传输、kernel launch 和同步；Device 侧由太初 AI 加速卡执行大规模并行计算。

从设备侧看，太初 AI 加速卡由多个 SPA 构成；每个 SPA 包含多个 SPE。SDAA C 的 SPMD 模型是在一个 SPA 内让所有 SPE 执行同一份程序，并通过 `threadIdx` / `threadDim` 划分数据。

## Kernel launch 形态

Kernel 函数由 `__global__` 修饰，返回类型必须为 `void`。Host 侧通过 CUDA 风格的尖括号语法 launch：

```cpp
kernel<<<placeHolder, stream>>>(args...);
kernel<<<placeHolder>>>(args...);
```

关键点：

- `placeHolder` 当前暂无实际含义，指南说明可填任意值。
- `stream` 是 SDAA stream，可缺省。
- 一次 launch 会在目标 SPA 内启动 `threadDim` 个 SPE 执行同一 kernel。
- `.scpp` 后缀用于让 `tecocc` 识别 SDAA C 关键字。

## 关键字

| 关键字 | 语义 | 生成注意事项 |
|---|---|---|
| `__host__` | Host 端函数，可缺省 | 用于显式标注 Host 函数。 |
| `__global__` | Kernel 函数，在 Host 侧 launch、Device 侧运行 | 返回类型需要为 `void`。 |
| `__device__` | Device 侧函数或变量 | 可被 `__device__` 或 `__global__` 函数调用。 |
| `__local__` | SPM local 空间全局变量 | 只能作为全局变量使用，不支持初始化。 |
| `__scoped_local__` | Device 函数内 SPM local 静态位置变量 | 仅在 `--stack-on-global` 生效；不支持递归函数使用。 |
| `threadIdx` | 当前 SPE ID | 用于划分当前 SPA 内任务。 |
| `threadDim` | 当前 SPA 内 SPE 总数 | 用于编写可扩展 SPMD 循环。 |

## 数据类型

标量类型在 C/C++ 基本类型基础上扩展：

- `half`：16 bit 半精度浮点，符合 IEEE-754 half 存储格式。
- `bfloat16`：16 bit bfloat；指南说明当前主要支持指针操作，可配合 widen/narrow SIMD 接口。

向量类型：

| 类型 | 元素 |
|---|---|
| `intv16` | 16 个 signed int |
| `uintv16` | 16 个 unsigned int |
| `shortv32` | 32 个 signed short |
| `ushortv32` | 32 个 unsigned short |
| `halfv16` | 16 个 half |
| `floatv16` | 16 个 float |

## 设备端限制

生成 device 代码时避免：

- C++ exception / try-catch。
- RTTI、STL、全局对象构造析构。
- `new`。
- `__global__` 可变参数。
- 线程私有操作、局部静态变量。
- C/C++ 原生原子操作。
- 文件 IO、`exit`、`atexit` 等 host 风格进程/文件接口。

原子操作应使用 SDAA C 提供的 `atomic_*` 接口。

## 头文件与命名空间

常用头文件：

- `sdaa_atomic.h`
- `sdaa_matmul.h`
- `sdaa_transpose.h`
- `sdaa_perf.h`
- `sdaa_device_info.h`
- `scl.h`

命名空间：

- `sdaa`：基础接口，包括线程组、SPE 同步、数据搬运、原子、matmul 等。
- `sdaa::scl`：高层次函数接口。

## 代码生成契约

生成一个最小 SDAA C kernel 时，应至少包含：

1. `.scpp` 源文件。
2. Host 侧 `sdaaSetDevice`。
3. 必要的 `sdaaMalloc` / `sdaaMemcpy` / `sdaaFree`。
4. `__global__` kernel。
5. `kernel<<<1>>>(...)` 或显式 stream launch。
6. `sdaaDeviceSynchronize`。
7. `tecocc` 编译命令。

如果 kernel 需要跨 `.scpp` 调用 `__device__` 函数，编译链路应使用 LTO，见 `compiler-tecocc-build-debug`。
