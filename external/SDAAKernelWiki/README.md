# SDAAKernelWiki

SDAAKernelWiki 是面向 SDAA / 太初 T1 算子优化的本地结构化知识库。它复用了 KernelWiki 有价值的组织方式，但将 NVIDIA 术语替换为 SDAA 硬件本语。

## 内容范围

- `SPA/SPE`、`LDM`、`DMA`、`RMA`、`ACE`、`pipe0/pipe1`、HBM channel-bank-row 行为等硬件页面。
- 周期式 DMA 划分、128B/2KB 对齐 DMA、DMA 奇偶引擎顺序、RMA 广播选择、ACE 双缓冲、P0/P1 overlap 等技术页面。
- 调度空泡、LDM 压力、DMA/HBM 未打满、RMA 竞争、ACE feeding/writeback 问题等诊断页面。
- 指向 `external/knowledge` 的本地来源页。
- 说明可靠 SDAA 算子优化生成仍缺哪些材料的缺口分析。

## 快速命令

```bash
python3 scripts/query.py "DMA 128B 2KB channel bank" --compact
python3 scripts/query.py --tag ace --compact
python3 scripts/query.py --symptom ldm-pressure --compact
python3 scripts/get_page.py technique-dma-periodic-partitioning --follow-sources
python3 scripts/validate.py
```

## 范围边界

当前内容基于 `external/knowledge` 中的本地 KernelPilot 材料。知识库刻意保持保守：经验规则标记为 `source-reported` 或 `inferred`，缺失的 profiler / compiler / runtime 事实集中记录在 `docs/gap-analysis.md`。
