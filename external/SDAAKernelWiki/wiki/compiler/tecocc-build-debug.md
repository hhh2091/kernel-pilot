---
id: compiler-tecocc-build-debug
title: "TecoCC 编译、LTO、调试与符号解码"
type: compiler
architectures: [sdaa, teco-t1]
tags: [tecocc-lto, runtime-launch-overhead, compile-error]
confidence: verified
reproducibility: snippet
languages: [tecocc, sdaa-c, sdaa-cpp]
related: [lang-sdaa-c-programming-guide, migration-cuda-to-sdaa-c]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# TecoCC 编译、LTO、调试与符号解码

本页总结 SDAA C 编译与调试相关规则。

## 最小编译

快速入门中的最小编译形式：

```bash
tecocc test.scpp
```

默认产物为 `a.out`。

## LTO 与非 LTO

指南将编译分为 LTO 和非 LTO：

- LTO：通过 `-flto` 启用链接时优化；链接 SDAA C offload bundle 时使用 `--sdaa-link`。
- 非 LTO：普通 GNU 兼容 `.o` 生成和链接模式。

关键约束：

- 只有 LTO 模式支持从一个 `.scpp` 文件中的 `__global__` 或 `__device__` 函数调用另一个 `.scpp` 文件中定义的 `__device__` 函数。
- 如果使用 `--stack-on-global`，分阶段编译的所有阶段都应保持一致开启。

## 典型命令形态

```bash
# LTO object
tecocc user_kernel.scpp -O2 -flto -c -o user_kernel.o

# LTO link
tecocc user_kernel.o main.cpp -O2 -flto --sdaa-link -o a.out

# 非 LTO object
tecocc user_kernel.scpp -O2 -fPIC -c -o user_kernel.o

# 非 LTO link
tecocc user_kernel.o main.cpp -O2 -o a.out
```

## CMake 口径

`.scpp` 文件需要在 CMake 中设置 `LINKER_LANGUAGE` 为 `CXX`，并将 `CMAKE_CXX_COMPILER` 指向 `tecocc`。LTO 构建静态或动态库时需要在对象编译和链接阶段都传递相应 LTO / SDAA link 选项。

## 调试与工具

- `TecoGDB`：基于 GNU GDB 的源码级调试工具，用于调试 SPE 代码。
- `sdaacfilt`：SDAA C 符号解码工具，类似 `c++filt`，但增加了 SDAA C 数据类型支持。
- Device 侧支持 `printf`、`abort`、`assert`。

## KernelPilot 生成建议

- 单文件 seed kernel 优先使用简单 `tecocc file.scpp -O2 -o out`。
- 多文件或跨文件 `__device__` 调用时默认加 `-flto --sdaa-link`。
- 若出现 LTO 静态库索引错误，优先检查静态库是否按指南要求生成 index / ranlib。
- 所有编译命令应写入 `ledgers/sdaa-toolchain.md` 和 benchmark log。
