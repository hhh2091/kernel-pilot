---
id: runtime-sdaa-host-api
title: "SDAARuntime Host 侧常用接口"
type: runtime
architectures: [sdaa, teco-t1]
tags: [global-memory, runtime-launch-overhead]
confidence: verified
reproducibility: snippet
languages: [sdaa-c, sdaa-cpp]
related: [lang-sdaa-c-programming-guide, hw-sdaa-memory-model]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAARuntime Host 侧常用接口

本页总结《SDAA C 编程指南 v3.1.0》中列出的 Host 侧常用 Runtime 接口。更完整的 Runtime API 仍需参考独立的 SDAARuntime 用户手册。

## 常用接口

| 接口 | 用途 |
|---|---|
| `sdaaDeviceReset` | 销毁当前进程中当前设备上的已分配资源并重置状态。 |
| `sdaaSetDevice` | 指定 kernel 运行在哪个设备/SPA 上。 |
| `sdaaGetDevice` | 获取当前线程使用的设备。 |
| `sdaaGetDeviceCount` | 获取设备数量。 |
| `sdaaDeviceSynchronize` | 等待当前设备完成之前提交的任务。 |
| `sdaaMalloc` | 申请设备端 Global 存储空间。 |
| `sdaaFree` | 释放设备端 Global 存储空间。 |
| `sdaaMemcpy` | 在 Host 内存和 Device Global 存储之间传输数据。 |
| `sdaaMemset` | 初始化 Global 存储空间。 |
| `sdaaStreamCreate` | 创建异步流。 |

## 生成器默认 Host 流程

```text
sdaaGetDeviceCount
sdaaSetDevice
sdaaMalloc inputs/outputs
sdaaMemcpy H2D
kernel<<<1 or 1, stream>>>
sdaaDeviceSynchronize
sdaaMemcpy D2H
check correctness
sdaaFree
```

## 注意事项

- `sdaaSetDevice(0)` 在指南快速入门中用于选择 0 号 SPA/设备目标；实际多卡或多 SPA 环境需由 `teco-smi` 和 runtime 查询结果确认。
- Host/Device 传输使用 `sdaaMemcpy`，Device 内部 Global/SPM 或 SPE 间搬运不要用 Host Runtime 接口建模，应使用 DMA/RMA/Broadcast 页面。
- KernelPilot benchmark 应分离 Host runtime / driver 开销和 device kernel 时间；小 kernel 很容易被 launch/API 开销主导。
