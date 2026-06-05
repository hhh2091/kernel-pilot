---
id: technique-sdaa-simd-vectorization
title: "SDAA SIMD 向量化"
type: technique
architectures: [sdaa, teco-t1]
tags: [simd, simd-vectorization, p0-p1-overlap]
confidence: verified
reproducibility: api-contract
related: [hw-pipe0-pipe1, technique-p0-p1-overlap, kernel-sdaa-gemm]
sources: [doc-sdaa-c-programming-guide-v3-1-0, source-local-instruction-latency-pipeline]
---

# SDAA SIMD 向量化

SDAA C 提供显式向量类型与 SIMD intrinsic。适合 elementwise、reduction 局部累加、GEMM baseline、epilogue 和数据转换阶段。

## 向量类型

| 类型 | 元素 | 大小 |
|------|------|------|
| `intv16` | 16 × int32 | 64B |
| `uintv16` | 16 × uint32 | 64B |
| `shortv32` | 32 × int16 | 64B |
| `ushortv32` | 32 × uint16 | 64B |
| `halfv16` | 16 × float16 | 32B |
| `floatv16` | 16 × float32 | 64B |

## 完整 SIMD API

### Load/Store

| 接口 | 功能 | 对齐 |
|------|------|------|
| `simd_load(vec, src)` | 对齐向量加载 | 32B |
| `simd_store(vec, dst)` | 对齐向量存储 | 32B |
| `simd_loadu(vec, src)` | 非对齐加载 | 无 32B 要求 |
| `simd_storeu(vec, dst)` | 非对齐存储 | 无 32B 要求 |
| `simd_load_widen(vec, src)` | 对齐加载+扩展 (short→int, char→short, bf16→float) | 32B |
| `simd_store_narrow(vec, dst)` | 对齐存储+收缩 (int→short, short→char, float→bf16) | 32B |
| `simd_loadu_widen(vec, src)` | 非对齐加载+扩展 | 2B |
| `simd_storeu_narrow(vec, dst)` | 非对齐存储+收缩 | 2B |

### 标量拓展

| 接口 | 功能 |
|------|------|
| `simd_set(a0..a15)` | 由 16/32 标量构造向量 |
| `simd_stretch(ra)` | 标量广播到向量全部元素 |

### 比较-选择

| 接口 | 条件 |
|------|------|
| `simd_seleq(va, vb, vc)` | va[i]==0 → vb[i] 否则 vc[i] |
| `simd_selle(va, vb, vc)` | va[i]<=0 → vb[i] 否则 vc[i] |
| `simd_sellt(va, vb, vc)` | va[i]<0 → vb[i] 否则 vc[i] |

### 元素重组

| 接口 | 功能 |
|------|------|
| `simd_concat(va, vb, n)` | 按字节位置拼接两向量 |
| `simd_ins(ra, va, n)` | 标量插入向量指定位置 |

### 符号与类型转换

| 接口 | 功能 |
|------|------|
| `simd_copy_sign(va, vb)` | 取 va 符号位 + vb 指数和尾数 |
| `simd_cvt_f2h(va)` | floatv16 → halfv16 |
| `simd_cvt_h2f(va)` | halfv16 → floatv16 |

### 融合乘加 (FMA)

| 接口 | 运算 |
|------|------|
| `simd_fma(va, vb, vc)` | va × vb + vc |
| `simd_fms(va, vb, vc)` | va × vb − vc |
| `simd_fnma(va, vb, vc)` | −(va × vb) + vc |
| `simd_fnms(va, vb, vc)` | −(va × vb) − vc |

### 算术

| 接口 | 运算 | 支持类型 |
|------|------|---------|
| `simd_add` | + | 全部 |
| `simd_sub` | − | 全部 |
| `simd_mul` | × | 全部 |
| `simd_div` | ÷ | 全部 |
| `simd_rem` | % | int/short |
| `simd_fabs` | \|x\| | float only |
| `simd_redsum` | 横向求和→标量 | 全部 |

### 比较

| 接口 | 运算符 | 支持类型 |
|------|------|---------|
| `simd_cmplt` | < | 全部 |
| `simd_cmple` | <= | 全部 |
| `simd_cmpgt` | > | 全部 |
| `simd_cmpge` | >= | 全部 |
| `simd_cmpeq` | == | 全部 |
| `simd_cmpne` | != | 全部 |
| `simd_isnan` | isnan | float/half |
| `simd_max` | max | float/half |
| `simd_min` | min | float/half |

### 逻辑

| 接口 | 运算符 | 支持类型 |
|------|------|---------|
| `simd_and` | && | int/short |
| `simd_or` | \|\| | int/short |
| `simd_not` | ! | int/short |
| `simd_neg` | − | 全部 |

### 位运算

| 接口 | 运算符 | 支持类型 |
|------|------|---------|
| `simd_band` | & | int/short |
| `simd_bxor` | ^ | int/short |
| `simd_bor` | \| | int/short |
| `simd_bnor` | \| ~ | int/short |
| `simd_bnot` | ~ | int/short |

## 性能数据（SPM-resident, 单位: beats）

| 操作 | 周期 | 操作 | 周期 |
|------|------|------|------|
| `simd_load` | 12 | `simd_loadu` | 16 |
| `simd_store` | 7 | `simd_storeu` | 18 |
| `simd_set` | 3 | `simd_stretch` | 10 |
| `simd_fma/fms/fnma/fnms` | 15 | `simd_add/sub/mul` | 12 |
| `simd_div` | 1723 | `simd_mod` | 1670 |
| `simd_fabs` | 3 | `simd_redsum` | 3 |
| `simd_cmplt/le/gt/ge/eq` | 12 | `simd_cmpne` | 15 |
| `simd_isnan` | 21 | `simd_max/min` | 22 |
| `simd_and` | 100 | `simd_or` | 16 |
| `simd_not` | 11 | `simd_neg` | 11 |
| `simd_band/bxor/bor/bnot` | 10 | `simd_cvt_f2h/h2f` | 5 |

**关键观察**：`simd_div`(1723) 和 `simd_mod`(1670) 极其昂贵；`simd_and`(100) 比 `simd_band`(10) 慢 10x。

## 性能关键发现

- **SPM vs Global**：SIMD 数据在 SPM 上比 Global 快约 **63x**（`simd_load` 12 vs 758 beats）
- **向量化 vs 标量**：`simd_exp128` 比 `expf` 标量快约 **22x**
- **P0/P1 overlap**：与 DMA/RMA wait 和 SPM staging 配合使用收益最大

## 生成规则

1. 先确认数据在 lane 间独立；跨 lane 依赖应显式使用 reduction 或 shuffle 风格接口。
2. 对齐已知时优先 aligned load/store；边界处理单独拆出 tail path。
3. SIMD 数据尽量保持在 SPM 中，避免 Global 直连 SIMD。
4. 对 GEMM baseline，SIMD 只应作为过渡路径；大规模矩阵乘应进一步迁移到 matmul/ACE 路径。
5. 对 RMSNorm/layernorm，SIMD reduction 后仍需检查 sqrt/div 长延迟是否主导。
6. C++ 运算符（`+`, `-`, `*`, `/`, `<`, `>`, `<=`, `>=`, `==`, `!=`, `&&`, `||`, `!`, `&`, `|`, `^`, `~`）可等价替代对应 SIMD intrinsic。
