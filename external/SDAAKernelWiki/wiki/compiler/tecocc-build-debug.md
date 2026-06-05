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

## 最小编译

```bash
tecocc test.scpp               # 默认产物 a.out
```

## 完整命令行标志参考

| 标志 | 功能 |
|------|------|
| `-flto` | 开启 LTO 模式 |
| `--sdaa-link` | LTO 链接 clang-offload-bundler 捆绑包（必需） |
| `-v` | 显示编译器版本 |
| `--verbose` | 输出各编译阶段详细命令行 |
| `--sdaa-compile-host-device` | 编译 host+device（默认） |
| `--sdaa-device-lib-path=<v>` | device 端库搜索路径 |
| `--sdaa-device-lib=<v>` | 链接 device 端 `.bc` 库 |
| `--sdaa-static-device-lib=<v>` | 链接 device 端静态库 |
| `--sdaa-host-only` | 仅编译 host 端 |
| `--sdaa-device-only` | 仅编译 device 端 |
| `--sdaa-path=<v>` | SDAA C 库安装路径 |
| `-sdaa-static-lib` | LTO 模式打包 host 端 `.a` |
| `-nosdaainc` | 不添加默认 device 头文件 |
| `-nosdaalib` | 不链接默认 device 库 |
| `--stack-on-global` | 栈从 SPM 切换到 Global |
| `--sdaa-arch=pcx_100` | 为 PCX 架构生成 |

### SDAADriver 版本兼容性

| TecoCC | 默认 Launch API | 覆盖标志 |
|--------|----------------|---------|
| < v1.3.0 | v0.6.0 前旧接口 | 无 |
| v1.3.0–v1.3.4 | v0.6.0–v0.9.0 中间 | `-sdaa-new-launch-api` / `-fno-sdaa-new-launch-api` |
| > v1.3.4 | v0.9.0+ 新接口 | `-use-new-sdaa-driver` / `-fno-use-new-sdaa-driver` |

## LTO vs 非 LTO

- **LTO**：`-flto` 启用。host/device 分别生成 `.bc`→链接时合并 device `.bc`→转换 host `.bc`→最终链接。
- **非 LTO**：默认。device→预处理→编译→汇编→链接成 device 二进制；host 嵌入 device 二进制→编译→链接。

**关键约束**：
- 只有 LTO 支持跨 `.scpp` 调用 `extern __device__` 函数。
- `--stack-on-global` 分阶段编译每个阶段都必须开启；同一可执行文件所有函数须一致。

## 六种编译方式

### LTO 动态链接
```bash
tecocc k1.scpp -O2 -flto -c -o k1.o
tecocc k2.scpp -O2 -flto -c -o k2.o
tecocc k1.o k2.o -O2 -flto -fPIC -shared --sdaa-link -o tmp.so
tecocc main.cpp tmp.so -O2 -o out
```

### LTO 静态链接
```bash
tecocc k1.scpp k2.scpp -O2 -flto -c -o objs.o
tecocc objs.o -O2 -flto --sdaa-link -shared -sdaa-static-lib -o tmp.a
tecocc main.cpp tmp.a -O2 -o out
```

### LTO 直接生成
```bash
tecocc k1.scpp k2.scpp main.cpp -flto --sdaa-link -O2 -fPIC -o a.out
```

### 非 LTO 动态链接
```bash
tecocc k1.scpp -O2 -fPIC -c -o k1.o
tecocc k2.scpp -O2 -fPIC -c -o k2.o
tecocc k1.o k2.o -O2 -fPIC -shared -o tmp.so
tecocc main.cpp tmp.so -O2 -o out
```

### 非 LTO 静态链接（系统 ar）
```bash
tecocc k1.scpp -O2 -fPIC -c -o k1.o
tecocc k2.scpp -O2 -fPIC -c -o k2.o
ar -rcs tmp.a k1.o k2.o
tecocc main.cpp tmp.a -O2 -o out
```

### 非 LTO 直接生成
```bash
tecocc k1.scpp k2.scpp main.cpp -O2 -o a.out
```

## 编译优化

### Loop Unrolling

```cpp
#pragma clang loop unroll(enable)     // 编译器自行判断
#pragma clang loop unroll(disable)    // 禁止展开
#pragma clang loop unroll(full)       // 完全展开
#pragma clang loop unroll_count(N)    // 展开 N 次
```

`unroll_count(8)` 最优，约 **3.58x** vs 无展开。

### FMA Contraction

| 标志 | 效果 |
|------|------|
| `-ffp-contract=fast` | 启用融合（默认），~1.95x vs off |
| `-ffp-contract=on` | 遵循 `#pragma FP_CONTRACT` |
| `-ffp-contract=off` | 禁用融合 |

### LTO 收益

LTO 开启后跨模块内联、死代码消除、常量传播——benchmark 约 **2.07x** speedup。

## CMake 集成

`.scpp` 文件需设置 `LANGUAGE CXX`。LTO 静态库 CMake 示例：

```cmake
set(CMAKE_CXX_COMPILER "tecocc")
file(GLOB_RECURSE SRC_TMP "*.scpp")
add_library(tmp_objs OBJECT ${SRC_TMP})
set_source_files_properties(${SRC_TMP} PROPERTIES LANGUAGE CXX)
target_compile_options(tmp_objs PRIVATE -flto)
add_custom_target(tmp ALL
    COMMAND tecocc $<TARGET_OBJECTS:tmp_objs> -flto --sdaa-link -shared -sdaa-static-lib -fuse-ld=lld -o libtmp.a
    COMMAND_EXPAND_LISTS)
add_dependencies(tmp tmp_objs)
add_executable(static_test main.cpp)
add_dependencies(static_test tmp)
target_link_libraries(static_test PRIVATE -L. -ltmp -fuse-ld=lld)
```

## 调试工具

- **TecoGDB**：基于 GNU GDB，支持 host+device 源码级真实硬件调试。
- **sdaacfilt**：SDAA C 符号解码。`nm --extern-only test.o | sdaacfilt`

## KernelPilot 生成建议

- 单文件 kernel：非 LTO 直接生成。
- 多文件 + 跨文件 device 调用：LTO 动态/静态链接。
- 默认 `-O2`，探索性可加 `-ffp-contract=fast`。
- 所有编译命令写入 `ledgers/sdaa-toolchain.md`。
