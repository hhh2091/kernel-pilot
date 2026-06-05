# SDAAKernelWiki

SDAAKernelWiki 是面向 SDAA / 太初 T1 算子优化的本地结构化知识库。它复用了 KernelWiki 有价值的组织方式，但将 NVIDIA 术语替换为 SDAA 硬件本语。

## 内容范围

- `SPA/SPE`、`SPM/LDM`、`Global memory`、`DMA`、`RMA`、`ACE`、`pipe0/pipe1`、HBM channel-bank-row 行为等硬件页面。
- 官方 `SDAA C 编程指南 v3.1.0` 的结构化来源页，以及语言、runtime、compiler/debug、CUDA 迁移页面。
- 周期式 DMA 划分、128B/2KB 对齐 DMA、DMA 奇偶引擎顺序、RMA/Broadcast、SDAA matmul、SIMD、atomic、transpose、math/high-level API、perf sampling、ACE 双缓冲、P0/P1 overlap 等技术页面。
- 调度空泡、LDM 压力、DMA/HBM 未打满、RMA 竞争、ACE feeding/writeback 问题等诊断页面。
- 面向 KernelPilot 的 GEMM 优化生成路线、quickstart 示例、指南示例集合和算子开发映射。
- 指向 `external/knowledge` 的本地来源页。
- 说明可靠 SDAA 算子优化生成仍缺哪些材料的缺口分析。
- 面向算子团队协作的资料需求清单：`docs/operator-team-request-gap-analysis.md`。

## 快速命令

```bash
python3 scripts/query.py "DMA 128B 2KB channel bank" --compact
python3 scripts/query.py "SDAA C matmul GEMM" --compact
python3 scripts/query.py --tag simd-vectorization --compact
python3 scripts/query.py --tag ace --compact
python3 scripts/query.py --symptom ldm-pressure --compact
python3 scripts/query.py "math activation reduction atomic transpose" --compact
python3 scripts/get_page.py technique-dma-periodic-partitioning --follow-sources
python3 scripts/get_page.py kernel-sdaa-gemm --follow-sources
python3 scripts/get_page.py example-sdaa-programming-guide-examples
python3 scripts/validate.py
```

## 关键文档

- `docs/gap-analysis.md`：SDAAKernelWiki 面向算子优化生成的总体缺口。
- `docs/operator-team-request-gap-analysis.md`：对比成熟 KernelWiki 后，向 SDAA 算子团队索取资料的优先级清单。

## 范围边界

当前内容由 `external/knowledge` 中的本地 KernelPilot 材料和 `SDAA C 编程指南 v3.1.0` 结构化摘要组成。知识库刻意保持保守：官方 API 规则标记为 `verified`，本地经验规则标记为 `source-reported` 或 `inferred`，缺失的 profiler schema、真实可运行样例和 cost-model 验证集中记录在 `docs/gap-analysis.md`。
