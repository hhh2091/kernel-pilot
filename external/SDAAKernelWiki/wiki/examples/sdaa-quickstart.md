---
id: example-sdaa-quickstart
title: "SDAA C 快速入门最小闭环"
type: example
architectures: [sdaa, teco-t1]
tags: [quickstart, sdaa-c, tecocc]
confidence: verified
reproducibility: snippet
languages: [sdaa-c, tecocc]
related: [lang-sdaa-c-programming-guide, runtime-sdaa-host-api, compiler-tecocc-build-debug]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA C 快速入门最小闭环

PDF 第 3 章的 quickstart 对 KernelPilot 的价值是建立最小 Host-Device 闭环。

## 完整最小程序

```cpp
__global__ void kernel_entry()
{
    printf("Hello AI Card\n");
}

int main()
{
    sdaaSetDevice(0);
    kernel_entry<<<1>>>();
    sdaaDeviceSynchronize();
    return 0;
}
```

关键元素：
- `__global__`：kernel 函数标识（返回 `void`）
- `sdaaSetDevice(0)`：指定 SPA 0 为目标设备
- `<<<1>>>`：launch 语法（placeHolder 可填任意值，stream 可缺省）
- `sdaaDeviceSynchronize`：等待所有 SPE 完成

## 编译与运行

```bash
tecocc test.scpp -o test
./test
```

输出 `Hello AI Card` 共 `threadDim` 次（每个 SPE 一次）。

## 带数据搬移的最小闭环

```cpp
__global__ void add_one(int *data, int n)
{
    for (int i = threadIdx; i < n; i += threadDim) {
        data[i] = data[i] + 1;
    }
}

int main()
{
    const int N = 1024;
    int *host = (int*)malloc(N * sizeof(int));
    for (int i = 0; i < N; i++) host[i] = i;

    sdaaSetDevice(0);
    int *dev = NULL;
    sdaaMalloc((void**)&dev, N * sizeof(int));
    sdaaMemcpy(dev, host, N * sizeof(int), sdaaMemcpyHostToDevice);
    add_one<<<1>>>(dev, N);
    sdaaDeviceSynchronize();
    sdaaMemcpy(host, dev, N * sizeof(int), sdaaMemcpyDeviceToHost);
    sdaaFree(dev);

    // Verify
    for (int i = 0; i < N; i++) {
        if (host[i] != i + 1) { printf("FAIL at %d\n", i); return 1; }
    }
    printf("PASS\n");
    free(host);
    return 0;
}
```

## 生成约束

- 源文件使用 `.scpp`，让 TecoCC 识别 SDAA C 扩展关键字。
- `__global__` kernel 返回 `void`。
- Host 侧先 `sdaaSetDevice`，launch 后 `sdaaDeviceSynchronize`。
- 跨文件 kernel 声明用 `extern __global__ void kernel(...)`，编译加 `-flto --sdaa-link`。

## KernelPilot seed

在 SDAA 算子 workspace 中，先保留一个 quickstart smoke test。只有 smoke test 通过后，才开始引入 K/R/W、device memory、DMA 和 benchmark。
