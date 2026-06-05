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

PDF 第 6、11、12 章覆盖环境变量、程序调试和开发工具；第 7 章还列出设备信息、printf、abort、assert 等设备端辅助接口。

## 环境变量

- `SDAA_SYNC_PRINT`：用于控制或辅助同步打印行为。使用 printf 调试并行 kernel 时，应记录该变量状态，避免把输出顺序误判为执行顺序。

## 设备端辅助接口

指南列出的调试相关能力包括：

- `printf`：设备端打印，适合 smoke test 和小规模 shape。
- `abort`：设备端主动终止。
- `assert`：设备端断言。
- 设备信息接口：通过 `sdaa_device_info.h` 获取 device 相关信息。
- 性能采样：通过 `sdaa_perf.h` 的 `perf_start`、`perf_stop`、`perf_print`、`clock`、`PerfData` 标记热区。

## 开发工具

- TecoGDB：用于调试 SPE 侧代码。
- `sdaacfilt`：用于 SDAA C 符号解码，特别是包含 SDAA 数据类型或 device 符号时。

## KernelPilot 规则

1. correctness 阶段可以用 `printf/assert`，benchmark 阶段必须移除或关闭。
2. 出现 device crash 时先最小化 shape，再用 TecoGDB 或 assert 定位。
3. 任何 perf sampling 结果都应和 host benchmark 分开记录。
4. 生成报告时记录 `SDAA_SYNC_PRINT`、driver/runtime 版本和编译命令。
