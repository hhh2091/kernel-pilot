---
id: technique-sdaa-transpose-api
title: "SDAA Transpose 接口"
type: technique
architectures: [sdaa, teco-t1]
tags: [transpose, spm, dma]
confidence: verified
reproducibility: api-contract
kernel_types: [transpose]
languages: [sdaa-c]
related: [technique-sdaa-dma-api, hw-sdaa-memory-model]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA Transpose 接口

头文件 `sdaa_transpose.h`，命名空间 `sdaa`。

## API 完整签名

### transpose（阻塞）

```cpp
void transpose(void *dst, const void *src, unsigned int height, unsigned int width,
               size_t element_size)
```

同 SPA 内 Global→Global、SPM→SPM 或 Global→SPM。

| 参数 | 约束 |
|------|------|
| `element_size` | 仅 **2B**（half/short）或 **4B**（float/int） |
| 地址对齐 | 对齐到元素类型：2B 对齐（half/short），4B 对齐（float/int） |
| SPM 开销 | 2B 元素=额外 2KB SPM 堆；4B 元素=额外 1KB SPM 堆 |

**限制**：不支持 in-place transpose。

### transpose_async（非阻塞）

```cpp
void transpose_async(void *dst, const void *src, unsigned int height, unsigned int width,
                     size_t element_size, MemoryStride stride, TransposeDirect direct,
                     TransposeHandle &handle)
```

| 参数 | 约束 |
|------|------|
| `dst` | **SPM only** |
| `src` | **Global only** |
| `height` | **32**（2B 元素）或 **16**（4B 元素） |
| `width` | **32**（2B 元素）或 **16**（4B 元素） |
| `element_size` | 仅 **2B** 或 **4B** |
| `stride` | src stride 仅 Global 支持；均为 0=连续 |
| `direct` | 仅 `TransposeGlobalToSpm` |
| `handle` | `TransposeHandle&` |

**对齐**：Global 和 SPM 地址均需 **64B 对齐**（Global 数组可用 `__attribute__((aligned(64)))`）。

**硬件 tile 约束**：

| element_size | height | width | tile 大小 |
|-------------|--------|-------|----------|
| 2B (half/short) | 32 | 32 | 2048B |
| 4B (float/int) | 16 | 16 | 1024B |

### TransposeHandle

```cpp
TransposeHandle::TransposeHandle()
```

默认构造函数。同 handle 的多个 `transpose_async` 可被一个 `transpose_wait` 同步。

### transpose_wait

```cpp
void transpose_wait(TransposeHandle &handle)
```

等待同 handle 的所有 `transpose_async` 完成。

### check_transpose_async

```cpp
unsigned int check_transpose_async(void *dst, const void *src, unsigned int height,
                                   unsigned int width, size_t element_size,
                                   MemoryStride stride, TransposeDirect direct,
                                   TransposeHandle &handle)
```

返回 `TransposeAsyncStatus` 位掩码：

| 位 | bit 0=1 时含义 |
|----|---------------|
| 1 | 地址未对齐 (TRANSPOSE_ASYNC_ERR_ADDR_UNALIGNED) |
| 2 | height/width 非法 (TRANSPOSE_ASYNC_ERR_SIZE_ILLEGAL) |
| 3 | 方向非法 (TRANSPOSE_ASYNC_ERR_DIRECT_ILLEGAL) |
| 4 | stride 参数错误 (TRANSPOSE_ASYNC_ERR_STRIDE_PARAM) |

## 使用模式

1. `check_transpose_async(...)` 验证参数 → 若返回 `TRANSPOSE_ASYNC_SUCC`
2. `transpose_async(dst, src, h, w, elem_size, {0,0}, TransposeGlobalToSpm, handle)`
3. `transpose_wait(handle)`
4. `free(dst)` 释放 SPM

## 生成规则

1. 开发版使用 `check_transpose_async` 验证参数。
2. 异步 transpose 应与 DMA/matmul 阶段建立清晰依赖。
3. GEMM B 矩阵预处理如 layout 重排可复用多次，考虑单独 kernel 或 host 端预处理。
4. 小 shape 时 transpose 开销可能超收益，保留 no-transpose fallback。
