---
id: pattern-sdaa-compile-porting-errors
title: "SDAA C 编译与迁移错误"
type: pattern
architectures: [sdaa, teco-t1]
tags: [compile-error, porting-mismatch, cuda-migration, tecocc-lto]
confidence: verified
symptoms: [compile-error, porting-mismatch]
candidate_techniques: [compiler-tecocc-build-debug, migration-cuda-to-sdaa-c, lang-sdaa-c-programming-guide]
related: [compiler-tecocc-build-debug, migration-cuda-to-sdaa-c, lang-sdaa-c-programming-guide]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA C 编译与迁移错误

该模式覆盖从 CUDA/C++ 迁移到 SDAA C 或接入 KernelPilot harness 时的常见失败。它的目标不是优化性能，而是让 K/R/W 能稳定编译、运行和复现。

## 常见信号

| 信号 | 首查方向 |
|---|---|
| 编译器不识别 SDAA 关键字 | 文件扩展名是否为 `.scpp`，编译器是否为 `tecocc`。 |
| CMake 链接语言错误 | `.scpp` 源文件是否设置 `LINKER_LANGUAGE CXX`。 |
| LTO 静态库索引错误 | 检查 `-flto`、`--sdaa-link` 和静态 device library 流程。 |
| CUDA warp/block 相关符号缺失 | 按 `migration-cuda-to-sdaa-c` 重写并行模型。 |
| device 代码使用 C++ 高级特性失败 | 检查异常、RTTI、STL、new、文件 IO、local static 等限制。 |

## 处理顺序

1. 用最小 `Hello AI Card` kernel 验证 `sdaaSetDevice`、launch、`sdaaDeviceSynchronize`。
2. 固定 `.scpp`、`tecocc` 和 runtime link 方式。
3. 在 device 代码中移除不支持的 C++ 语言特性。
4. 把 CUDA launch geometry 翻译成 `threadIdx` / `threadDim` 和显式数据分片。
5. 运行 correctness harness，再进入性能优化。

## KernelPilot 记录项

- 编译命令、运行命令、driver/runtime 版本。
- 是否启用 LTO、`--stack-on-global` 或 device-only 编译。
- 迁移前的 CUDA 假设与迁移后的 SDAA 表达。
