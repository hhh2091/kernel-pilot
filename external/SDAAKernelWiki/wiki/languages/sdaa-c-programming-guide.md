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

本页总结《SDAA C 编程指南 v3.1.0》中对 KernelPilot 最重要的语言规则。它应替代旧页面中"仍缺精确签名"的部分，作为生成 SDAA C skeleton 的首选入口。

## Host-Device 模型

SDAA C 使用 Host-Device 主从异构模型。Host 侧负责设备选择、Global 存储申请、Host/Device 数据传输、kernel launch 和同步；Device 侧由太初 AI 加速卡执行大规模并行计算。

从设备侧看，太初 AI 加速卡由多个 SPA 构成；每个 SPA 包含多个 SPE。SDAA C 的 SPMD 模型是在一个 SPA 内让所有 SPE 执行同一份程序，并通过 `threadIdx` / `threadDim` 划分数据。

## Kernel Launch 语法

```cpp
kernel<<<placeHolder, stream>>>(args...);
kernel<<<placeHolder>>>(args...);
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `placeHolder` | `size_t` | 当前暂无实际含义，可填任意值 |
| `stream` | `sdaaStream_t` | SDAA stream，可缺省 |

一次 launch 在目标 SPA 内启动 `threadDim` 个 SPE 执行同一 kernel。

## 关键字详细语义

### __host__

Host 端函数标识。在 Host 侧调用并执行。**可省略**（默认即为 `__host__`）。

### __global__

Kernel 函数标识。在 Host 侧通过 `<<<...>>>` launch，在 Device 侧执行。

**约束**：返回类型必须为 `void`。不支持可变参数。

### __device__

Device 侧函数或变量标识。只能在 Device 侧调用/访问，调用者必须也是 `__device__` 或 `__global__` 函数。

### __local__

SPM local 空间全局变量标识。只能作为全局变量使用。

**约束**：**不支持初始化**。查询可用空间大小用 `get_local_size()`。

```cpp
__local__ int num[512];
__local__ short n;
```

### __scoped_local__

Device 函数内 SPM local 静态位置变量修饰符。

**关键规则**：
- 仅在 `--stack-on-global` 开启时生效。
- 生效时与 `__local__` 共享 SPM local 空间。
- 仅在声明函数内可见，函数作用域生命周期。
- 支持初始化；每次函数调用重新初始化（未显式初始化则值未定义）。
- 地址在程序启动时确定，运行期间不变（静态存储位置）。
- **不支持递归函数**。
- `--stack-on-global` 未开启时被忽略（当作普通栈变量）。

```cpp
__device__ void func() {
    __scoped_local__ int num[512];
    __scoped_local__ short n = 1;
}
```

### threadIdx / threadDim

| 关键字 | 类型 | 含义 |
|--------|------|------|
| `threadIdx` | `unsigned long` | 当前 SPE ID |
| `threadDim` | `unsigned long` | 当前 SPA 内 SPE 总数 |

## 数据类型

### 扩展标量类型

| 类型 | 大小 | 说明 |
|------|------|------|
| `half` | 2B | IEEE-754: 1 符号 + 5 指数 + 10 尾数 |
| `bfloat16` | 2B | 1 符号 + 8 指数 + 7 尾数；当前仅支持指针操作（配合 `simd_load_widen`/`simd_store_narrow`） |

### 向量类型

| 类型 | 元素 | 大小 |
|------|------|------|
| `intv16` | 16 × signed int | 64B |
| `uintv16` | 16 × unsigned int | 64B |
| `shortv32` | 32 × signed short | 64B |
| `ushortv32` | 32 × unsigned short | 64B |
| `halfv16` | 16 × half | 32B |
| `floatv16` | 16 × float | 64B |

各元素独立，一个元素上的操作不影响其他元素。

## 头文件与命名空间

| 头文件 | 用途 |
|--------|------|
| `sdaa_atomic.h` | 原子操作 |
| `sdaa_matmul.h` | 矩阵乘 |
| `sdaa_transpose.h` | 转置操作 |
| `sdaa_perf.h` | 性能采样 |
| `sdaa_device_info.h` | 设备信息查询 |
| `scl.h` | 高层函数接口 |

| 命名空间 | 范围 |
|---------|------|
| `sdaa` | 基础接口（线程组、同步、DMA、RMA、Broadcast、原子、matmul） |
| `sdaa::scl` | 高层函数接口（batch math、activation、reduction） |

## 设备端代码限制

**不支持**：

- C++ exception / try-catch
- RTTI
- STL 标准库
- 全局对象构造析构
- 跨越 Host/Device 边界的虚函数表
- `new` 关键字
- `__global__` 可变参数
- 线程私有操作
- 局部静态变量
- C/C++ 原生原子操作（用 SDAA C `atomic_*` 替代）
- 进程终止函数：`exit()`、`atexit()`
- 全部文件操作函数：`fopen`、`fclose`、`fread`、`fwrite`、`fprintf`、`fscanf`、`fgetc` 等

### C++11 支持

| 支持 | 不支持 |
|------|--------|
| C99 预处理器、static_assert、auto、constexpr、nullptr、lambda、range-for、decltype、noexcept、alignas、alignof、强类型 enum、变参模板、右值引用、NSDMI、用户定义字面量、继承构造函数、委托构造函数、defaulted/deleted 函数、显式转换运算符、属性、内联命名空间 | 原子操作、并发动态初始化和析构 |

## 常用 Host Runtime 接口

| 接口 | 作用 |
|------|------|
| `sdaaDeviceReset` | 销毁当前设备所有已分配资源并重置 |
| `sdaaSetDevice(device_id)` | 指定 kernel 运行的目标 SPA |
| `sdaaGetDevice(&dev_id)` | 获取当前线程使用的设备 ID |
| `sdaaGetDeviceCount(&count)` | 获取可用设备数量 |
| `sdaaDeviceSynchronize()` | 等待当前设备完成之前提交的所有任务 |
| `sdaaMalloc((void**)&ptr, size)` | 申请 Device Global 存储 |
| `sdaaFree(ptr)` | 释放 Device Global 存储 |
| `sdaaMemcpy(dst, src, size, dir)` | Host↔Device 数据传输 |
| `sdaaMemset(ptr, val, size)` | 初始化 Global 存储 |
| `sdaaStreamCreate(&stream)` | 创建异步流 |

## 代码生成契约

### 最小编译闭环

```bash
tecocc test.scpp          # .scpp 后缀让 tecocc 识别 SDAA C 关键字
./a.out
```

### 规范 Host 模板

```cpp
int main() {
    int dev_count = 0;
    sdaaGetDeviceCount(&dev_count);
    sdaaSetDevice(0);

    float *dev_ptr = NULL;
    sdaaMalloc((void**)&dev_ptr, size);
    sdaaMemcpy(dev_ptr, host_ptr, size, sdaaMemcpyHostToDevice);

    kernel<<<1>>>(dev_ptr);
    sdaaDeviceSynchronize();

    sdaaMemcpy(host_ptr, dev_ptr, size, sdaaMemcpyDeviceToHost);
    sdaaFree(dev_ptr);
    return 0;
}
```

### 跨文件 Kernel 声明

当 kernel 和 host 代码在不同 `.scpp` 文件时，host 文件需声明：

```cpp
extern __global__ void test(float *data1, float *data2, int number);
```

编译需使用 LTO：
```bash
tecocc device.scpp host.scpp -flto --sdaa-link -o lto.out
```

### KernelPilot 生成要求

1. `.scpp` 源文件。
2. Host 侧 `sdaaSetDevice`。
3. 必要的 `sdaaMalloc` / `sdaaMemcpy` / `sdaaFree`。
4. `__global__` kernel，返回 `void`。
5. `kernel<<<1>>>(...)` 或显式 stream launch。
6. `sdaaDeviceSynchronize`。
7. `tecocc` 编译命令写入 ledger。

如果 kernel 需要跨 `.scpp` 调用 `__device__` 函数，编译链路应使用 LTO。
