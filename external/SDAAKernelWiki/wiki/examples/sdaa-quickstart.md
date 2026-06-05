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

PDF 第 3 章给出的 quickstart 对 KernelPilot 的价值是建立最小 Host-Device 闭环：`.scpp` 源文件、device kernel、host runtime、launch、同步和 `tecocc` 编译。

## 最小结构

```text
__global__ void kernel_entry() {
  printf("Hello AI Card\n");
}

int main() {
  sdaaSetDevice(0);
  kernel_entry<<<1>>>();
  sdaaDeviceSynchronize();
}
```

编译入口：

```text
tecocc test.scpp
./a.out
```

## 生成约束

- 源文件使用 `.scpp`，让 TecoCC 识别 SDAA C 扩展关键字。
- `__global__` kernel 返回 `void`。
- Host 侧先调用 `sdaaSetDevice`，launch 后调用 `sdaaDeviceSynchronize`。
- 该 quickstart 只证明工具链闭环，不证明数据搬运、正确性 oracle 或性能。

## KernelPilot seed

在 SDAA GEMM 或其他算子 workspace 中，先保留一个 quickstart smoke test。只有 smoke test 通过后，才开始引入 K/R/W、device memory、DMA 和 benchmark。
