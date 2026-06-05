---
id: example-sdaa-programming-guide-examples
title: "SDAA C 编程指南示例集合"
type: example
architectures: [sdaa, teco-t1]
tags: [quickstart, simd-vectorization, matmul, atomics, broadcast]
confidence: verified
reproducibility: concept
kernel_types: [vector, matmul, atomic, reduction]
languages: [sdaa-c, tecocc]
related: [example-sdaa-quickstart, kernel-sdaa-gemm, technique-sdaa-atomic-api, technique-sdaa-simd-vectorization]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA C 编程指南示例集合

PDF 第 15/16 章提供的完整可运行示例。SDAAKernelWiki 保留为结构化参考，可转成 KernelPilot seed。

## 示例类别

| 示例 | seed 方向 | 关键 API | 编译 |
|------|----------|---------|------|
| 向量运算 | elementwise SIMD | `simd_load`/`simd_store`/`simd_sqrt`/`simd_exp` | LTO |
| SPMD 矩阵乘 | GEMM baseline | `memcpy_async`/`memcpy_wait`/`matmul_init`/`matmul_compute`/`matmul_store` | 非 LTO |
| SUMMA 矩阵乘 | 多 SPE 协作 | `BroadcastHandle`/`ThreadGroup`/`broadcast()` | 非 LTO |
| 自定义 atomic | reduction/冲突更新 | `atomic_cas_bool`+CAS 循环 | 非 LTO |
| 加法算子 | 最小自定义 op | `malloc`/`memcpy` SPM staging | 非 LTO |
| 矩阵乘算子 | GEMM 完整流程 | `MatmulHandle`/`matmul_compute` split-k | 非 LTO |

## 示例 1：向量运算（SIMD elementwise）

Device 侧关键模式：
```cpp
__local__ floatv16 __A, __B, vres0, vres1, vres2;

__global__ void test(float *data1, float *data2, int number)
{
    if (threadIdx == 0) {
        simd_load(__A, data1);
        simd_load(__B, data2);
        vres0 = simd_sqrt(__B);
        vres1 = simd_exp(vres0);
        vres2 = (__A * vres0 + __B);      // vector FMA
        simd_store(vres1, data1);
        simd_store(vres2, data2);
    }
}
```

编译：`tecocc device.scpp host.scpp -flto --sdaa-link -o out`

## 示例 2：SPMD 矩阵乘（DMA + Matmul）

关键模式：SPE 均分数据 + 非阻塞 DMA + matmul API。
```cpp
__global__ void matmul_func(char *input, char *weight, char *output, int m, int k, int n)
{
    unsigned int slice = m / threadDim;
    short *spm_input  = (short*)malloc(slice * k * sizeof(short));
    short *spm_weight = (short*)malloc(k * n * sizeof(short));
    short *spm_output = (short*)malloc(slice * n * sizeof(short));

    memcpy_async(spm_input,  input  + threadIdx * slice * k * sizeof(short),
                 slice * k * sizeof(short), 0, {0,0}, MemcpyGlobalToSpm);
    memcpy_async(spm_weight, weight, k * n * sizeof(short), 0, {0,0}, MemcpyGlobalToSpm);
    memcpy_wait();

    matmul_compute_func(spm_input, spm_weight, spm_output, slice, k, n);

    memcpy(output + threadIdx * slice * n * sizeof(short), spm_output, slice * n * sizeof(short));
    free(spm_output); free(spm_weight); free(spm_input);
}
```

## 示例 3：SUMMA 矩阵乘（Broadcast）

SPE 按 4×8 网格组织，行列广播分发子块。
```cpp
// 构建行列广播 mask
unsigned long gen_broadcast_mask(Mask_Flag is_row) {
    int x = threadIdx % 8, y = threadIdx / 8;
    unsigned long mask = 0;
    if (is_row == MASK_ROW) {
        for (int i = 0; i < 8; i++) mask |= (1UL << (y * 8 + i));
    } else { // MASK_COL
        for (int i = 0; i < 32; i += 8) mask |= (1UL << (x + i));
    }
    return mask;
}

// 使用
ThreadGroup row_tg(row_mask);
BroadcastHandle handle_row(&row_tg);
broadcast(dst_spm, src_spm, size, 0, {0,0}, root_spe, BroadcastSpmToSpm, handle_row);
```

## 示例 4：自定义原子浮点加（CAS）

```cpp
__device__ void atomic_add_float(float* val, float num) {
    int* addr = (int*)val;
    int old;
    do {
        old = *addr;
        float expect = num + *(float*)&old;
    } while (!atomic_cas_bool(addr, old, *(int*)&expect));
}
```

## 示例 5：算子开发工作流（6 步）

1. 分配 host 内存 + 初始化输入
2. 分配 Global 内存 + 数据搬入（`sdaaMalloc`/`sdaaMemcpy`）
3. 分配 SPM 内存 + 数据搬入（`memcpy`/`memcpy_async`）+ SPM 计算
4. 结果搬出 SPM→Global（`memcpy`）
5. 结果搬出 Global→Host（`sdaaMemcpy`）
6. 正确性验证（CPU vs Device，如 float 容差 5e-7）

## 整理为 seed 的要求

每个示例进入 KernelPilot 需补齐：
1. **K**：device kernel 最小实现
2. **R**：CPU reference + 误差阈值
3. **W**：shape、dtype、layout、随机种子、边界 shape
4. **build**：`tecocc` 或 CMake 命令
5. **run**：correctness、benchmark、perf sampling
6. **ledger**：引用 SDAAKernelWiki page id
