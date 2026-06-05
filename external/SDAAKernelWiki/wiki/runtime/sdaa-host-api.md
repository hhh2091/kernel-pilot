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

## 完整接口列表

| 接口 | 签名 | 用途 |
|------|------|------|
| `sdaaDeviceReset` | `void sdaaDeviceReset()` | 销毁当前进程中当前设备上的已分配资源并重置状态 |
| `sdaaSetDevice` | `void sdaaSetDevice(int device_id)` | 指定 kernel 运行在哪个设备/SPA 上 |
| `sdaaGetDevice` | `void sdaaGetDevice(int *device_id)` | 获取当前线程使用的设备 ID |
| `sdaaGetDeviceCount` | `void sdaaGetDeviceCount(int *count)` | 获取可用设备数量 |
| `sdaaDeviceSynchronize` | `void sdaaDeviceSynchronize()` | 等待当前设备完成之前提交的所有任务 |
| `sdaaMalloc` | `void sdaaMalloc(void **ptr, size_t size)` | 申请 Device Global 存储空间 |
| `sdaaFree` | `void sdaaFree(void *ptr)` | 释放 Device Global 存储 |
| `sdaaMemcpy` | 见下方 | Host↔Device Global 数据传输 |
| `sdaaMemset` | `void sdaaMemset(void *ptr, int value, size_t num)` | 初始化 Global 存储 |
| `sdaaStreamCreate` | `void sdaaStreamCreate(sdaaStream_t *stream)` | 创建异步流 |

### sdaaMemcpy

```cpp
void sdaaMemcpy(void *dst, const void *src, size_t size, sdaaMemcpyKind kind)
```

`kind` 取值：
- `sdaaMemcpyHostToDevice`：Host → Device Global
- `sdaaMemcpyDeviceToHost`：Device Global → Host

## 规范 Host 程序模板

```cpp
int main()
{
    // 1. 检查可用设备
    int dev_count = 0;
    sdaaGetDeviceCount(&dev_count);

    // 2. 选择目标设备
    sdaaSetDevice(0);

    // 3. 准备 host 数据
    float *host_in  = (float*)malloc(size);
    float *host_out = (float*)malloc(size);
    // ... 初始化 host_in ...

    // 4. 分配 Device Global 内存
    float *dev_data = NULL;
    sdaaMalloc((void**)&dev_data, size);

    // 5. Host → Device 传输
    sdaaMemcpy(dev_data, host_in, size, sdaaMemcpyHostToDevice);

    // 6. 创建 stream（可选）+ Launch kernel
    sdaaStream_t stream;
    sdaaStreamCreate(&stream);
    kernel<<<1, stream>>>(dev_data);
    // 或: kernel<<<1>>>(dev_data);

    // 7. 同步
    sdaaDeviceSynchronize();

    // 8. Device → Host 传输
    sdaaMemcpy(host_out, dev_data, size, sdaaMemcpyDeviceToHost);

    // 9. 正确性检查
    // ... compare host_out vs expected ...

    // 10. 释放
    sdaaFree(dev_data);
    free(host_in);
    free(host_out);
    return 0;
}
```

## 注意事项

- `sdaaSetDevice(0)` 在指南快速入门中用于选择 0 号 SPA/设备目标；多卡或多 SPA 环境由 `teco-smi` 和 runtime 查询确认。
- Host/Device 传输使用 `sdaaMemcpy`，Device 内部搬运使用 DMA/RMA/Broadcast，不可混用。
- KernelPilot benchmark 应分离 Host runtime/driver 开销和 device kernel 时间；小 kernel 容易被 launch/API 开销主导。
- `abort()`/`assert()` 失败后，若未设 `SDAA_ENABLE_COREDUMP_ON_EXCEPTION`，`sdaaDeviceSynchronize()` 返回相应错误码。
