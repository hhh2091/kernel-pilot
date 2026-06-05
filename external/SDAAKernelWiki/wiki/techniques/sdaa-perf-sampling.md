---
id: technique-sdaa-perf-sampling
title: "SDAA 设备端性能采样"
type: technique
architectures: [sdaa, teco-t1]
tags: [perf-sampling, profiler-cross-check]
confidence: verified
reproducibility: api-contract
related: [pattern-scheduling-bubbles, pattern-ldm-pressure, pattern-ace-feeding-writeback]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-rms-metrics-analysis]
---

# SDAA 设备端性能采样

SDAA C 在 `sdaa_perf.h` 中提供设备端性能采样接口。

## 核心接口

### perf_start

```cpp
void perf_start()
```

标记性能采样起始位置。需 `#include "sdaa_perf.h"`。

### perf_stop

```cpp
PerfData perf_stop()
```

标记采样结束。返回 `PerfData` 结构体。

**约束**：`perf_start`/`perf_stop` 必须 1:1 配对，**不支持嵌套**。

### PerfData

```cpp
typedef struct _perfdata {
    uint64_t latency;     // 周期计数，单位: cycles
    uint64_t cache_miss;  // 指令 cache miss 次数
} PerfData;
```

### perf_print

```cpp
void perf_print()
```

输出采样数据到终端。必须在采样后调用，放在 kernel 函数末尾（return 前）。

**输出字段**：`START LINE NUM`、`LATENCY`（cycles）、`CNT_L1IC_MISS`。

**约束**：每 SPE 最多保留 **10 组**采样数据，超出则只保留最后 10 组。

### clock

```cpp
unsigned long clock()
```

返回当前 SPE 时钟周期计数器值。需 `#include "sdaa_clock.h"`。

用法：在被测代码段前后各调用一次，差值即消耗周期。

## 设备信息查询

### SPM 空间查询

```cpp
size_t get_heap_size()    // 当前 SPE 堆总大小
size_t get_stack_size()   // 当前 SPE 栈总大小
size_t get_local_size()   // 当前 SPE local 空间总大小
```

## 设备端调试

### printf

```cpp
int printf(const char *format, ...)
```

内置接口，无需头文件。支持 `%d`, `%u`, `%f`, `%c`, `%s`, `%x/%X`, `%p`, `%%`。

环境变量 `SDAA_SYNC_PRINT=1` 强制按 SPE 编号升序打印；默认按执行顺序。

### abort

```cpp
void abort()
```

终止 device 端执行。`SDAA_ENABLE_COREDUMP_ON_EXCEPTION` 设则生成 Core Dump+终止 host；未设则 host 继续，`sdaaDeviceSynchronize()` 返回 abort 错误码。

### assert

```cpp
void assert(bool condition)
```

condition 为 false 时打印文件名+行号并终止。同样受 `SDAA_ENABLE_COREDUMP_ON_EXCEPTION` 控制。

## 性能测量公式

```
Performance = Instructions/Program × ExecutionCycles/Instruction × Time/ExecutionCycle
BW_theoretical = MaxMemoryFreq × NumChannels × 64/8 (bytes/sec)
BW_actual = DataVolume × Freq / ExecutionCycles (bytes/sec)
```

## KernelPilot 用法

1. benchmark harness 保留端到端 wall time。
2. device hot loop 周围插入 `perf_start`/`perf_stop`，只测关键阶段。
3. 对 DMA/RMA/matmul 版本，分别标记 load、compute、store、wait 区段。
4. 为减小 cache miss 偏差，循环执行被测代码多次取平均。
5. attempt ledger 记录 perf 区段名、shape、SPE 数、SPM 字节。

## 已知不足

- 无完整 profiler schema（zero-launch、cannot-launch、DMA/RMA/ACE counter 需从 optest/SDPTI/PMU 补齐）。
- 采样代码本身有扰动，仅用于阶段对比，不替代端到端 benchmark。
