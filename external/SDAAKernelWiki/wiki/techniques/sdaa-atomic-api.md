---
id: technique-sdaa-atomic-api
title: "SDAA Atomic 接口与生成约束"
type: technique
architectures: [sdaa, teco-t1]
tags: [atomics, global-memory, spm]
confidence: verified
reproducibility: api-contract
kernel_types: [atomic, reduction]
languages: [sdaa-c]
related: [kernel-sdaa-gemm, technique-sdaa-simd-vectorization]
sources: [doc-sdaa-c-programming-guide-v3-1-0]
---

# SDAA Atomic 接口与生成约束

PDF 第 7 章列出 SDAA C atomic 接口，第 13 章将 atomic 作为性能调优主题，第 15 章包含自定义 atomic 示例。

## 公共约束

所有原子操作共享以下前置条件：

- **头文件**：`#include <sdaa_atomic.h>`
- **命名空间**：`using namespace sdaa;`
- **存储空间**：目标指针必须在 Global 内存中
- **保证**：所有 atomic 操作对同一内存地址的访问保证串行化（serialized）

## API 家族完整签名

### atomic_inc

```cpp
int64_t atomic_inc(int64_t *val)
```

将目标值原子加 1，返回旧值。

| 参数 | 说明 |
|------|------|
| `val` | Global 内存中的操作数指针 |

**语义**：每个 SPE 获得单调递增的值：1, 2, 3, 4, 5...（与线程执行顺序无关）。若 `val` 已通过 `sdaaMalloc` 预初始化，序列从 `*val+1` 开始。

### atomic_add

```cpp
int32_t atomic_add(int32_t *val, int32_t num)
int64_t atomic_add(int64_t *val, int64_t num)
float   atomic_add(float *val, float num)
double  atomic_add(double *val, double num)
```

原子加 `num` 到目标，返回旧值。

| 参数 | 说明 |
|------|------|
| `val` | Global 内存中的操作数指针 |
| `num` | 加数 |

**返回**：加之前的旧值，类型匹配操作数。

### atomic_add_noret

```cpp
void atomic_add_noret(int32_t *val, int32_t num)
void atomic_add_noret(int64_t *val, int64_t num)
```

原子加 `num` 到目标，**无返回值**。

**注意**：不支持 `float` 和 `double` 重载（与 `atomic_add` 不同）。

### atomic_sub

```cpp
int32_t atomic_sub(int32_t *val, int32_t num)
int64_t atomic_sub(int64_t *val, int64_t num)
```

原子减 `num`，返回旧值。

**注意**：不支持 `float` 和 `double` 重载。

### atomic_sub_noret

```cpp
void atomic_sub_noret(int32_t *val, int32_t num)
void atomic_sub_noret(int64_t *val, int64_t num)
```

原子减 `num`，**无返回值**。

### atomic_cas (Compare-And-Swap)

```cpp
int32_t atomic_cas(int32_t *val, int32_t compare, int32_t new_val)
int64_t atomic_cas(int64_t *val, int64_t compare, int64_t new_val)
```

若 `*val == compare`，原子设置 `*val = new_val`。始终返回 `*val` 的旧值。

| 参数 | 说明 |
|------|------|
| `val` | Global 内存中的操作数指针 |
| `compare` | 与 `*val` 比较的值 |
| `new_val` | 比较成功时写入的新值 |

**语义**：
- 一个 SPE 成功（CAS 匹配），获得旧 `compare` 值；其他所有 SPE 获得 `new_val`。
- 若 compare 失败：无 SPE 写入，所有 SPE 获得未变的旧值。
- 判断"胜者"：`old == compare`

**模式**：可在循环中使用 CAS 实现任意自定义原子操作。

### atomic_cas_bool

```cpp
bool atomic_cas_bool(int32_t *val, int32_t compare, int32_t new_val)
bool atomic_cas_bool(int64_t *val, int64_t compare, int64_t new_val)
```

与 `atomic_cas` 语义相同，但返回 `bool`：成功为 `true`，失败为 `false`。

更便于锁获取模式。

## 生成规则

1. reduction 首选分层规约：SIMD lane 内规约 → SPE 内 SPM 规约 → SPE group 规约；atomic 作为跨分片合并 fallback。
2. 如果 atomic 返回值未使用，优先选择 no-return 版本（`atomic_add_noret` / `atomic_sub_noret`），减少不必要依赖。
3. 高争用地址应避免所有 SPE 同时 atomic；改用分桶（per-SPE bucket）或分阶段 merge。
4. 用 atomic 实现 correctness 原型后，必须通过 profiler 或 benchmark 判断是否成为瓶颈。
5. 使用 `atomic_cas` 在循环中可以实现任意 fetch-and-op 模式，适合实现自定义原子语义。

## 类型支持对照表

| 操作 | int32 | int64 | float | double |
|------|-------|-------|-------|--------|
| `atomic_inc` | - | ✓ | - | - |
| `atomic_add` | ✓ | ✓ | ✓ | ✓ |
| `atomic_add_noret` | ✓ | ✓ | ✗ | ✗ |
| `atomic_sub` | ✓ | ✓ | ✗ | ✗ |
| `atomic_sub_noret` | ✓ | ✓ | ✗ | ✗ |
| `atomic_cas` | ✓ | ✓ | ✗ | ✗ |
| `atomic_cas_bool` | ✓ | ✓ | ✗ | ✗ |

## 测量项

- atomic 调用次数和目标地址分布。
- SPE 并发度、热点 bucket、端到端时间。
- 与无 atomic 的两阶段 reduction 对比。
