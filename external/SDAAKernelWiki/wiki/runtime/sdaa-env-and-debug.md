---
id: runtime-sdaa-env-and-debug
title: "SDAA 环境变量、设备信息与设备端调试"
type: runtime
architectures: [sdaa, teco-t1]
tags: [device-debug, perf-sampling, sdaa-c]
confidence: verified
reproducibility: api-contract
languages: [sdaa-c, tecocc]
related: [technique-sdaa-perf-sampling, compiler-tecocc-build-debug]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA 环境变量、设备信息与设备端调试

## 环境变量

### SDAA_SYNC_PRINT

控制 `printf` 输出顺序：

- 未设或 `0`（默认）：按 SPE **执行顺序**输出
- `export SDAA_SYNC_PRINT=1`：按 SPE ID **升序**输出

对比：
```
# 默认（执行顺序）：
threadIdx: 4, sum: 3
threadIdx: 0, sum: 3
threadIdx: 6, sum: 3

# SDAA_SYNC_PRINT=1（SPE 编号顺序）：
threadIdx: 0, sum: 3
threadIdx: 1, sum: 3
threadIdx: 2, sum: 3
```

### SDAA_ENABLE_COREDUMP_ON_EXCEPTION

控制 `abort()`/`assert()` 失败后的行为：

- **已设置**：生成 Core Dump 文件（含错误上下文）+ 终止 host 执行
- **未设置**：host 继续执行；后续 `sdaaDeviceSynchronize()` 返回相应错误码

## 设备端调试接口

### printf

```cpp
int printf(const char *format, ...)
```

内置接口，无需头文件。支持格式符：`%d`, `%u`, `%f`(6位小数), `%c`, `%s`, `%x/%X`, `%p`, `%%`。

### abort

```cpp
void abort()
```

终止 device 端程序。用于不可恢复错误（如除数为零）。

### assert

```cpp
void assert(bool condition)
```

condition 为 false 时打印文件名+行号后终止。用法：`assert(b != 0 && "b should not be zero");`

## 设备信息查询

通过 `sdaa_device_info.h` 获取 device 信息。SPM 空间查询接口（内置）：

```cpp
size_t get_heap_size()    // 当前 SPE 堆总大小
size_t get_stack_size()   // 当前 SPE 栈总大小
size_t get_local_size()   // 当前 SPE local 空间总大小
```

## 开发工具

- **TecoGDB**：基于 GNU GDB，支持真实硬件源码级调试（非仿真），覆盖 host+device。
- **sdaacfilt**：SDAA C 符号解码。解码示例：`_Z4testDv16_fS_` → `test(floatv16, floatv16)`。

## KernelPilot 规则

1. correctness 阶段用 `printf`/`assert`，benchmark 阶段必须移除或关闭。
2. device crash 时先最小化 shape，再用 TecoGDB 或 assert 定位。
3. perf sampling 结果和 host benchmark 分开记录。
4. 生成报告记录 `SDAA_SYNC_PRINT`、driver/runtime 版本和编译命令。
