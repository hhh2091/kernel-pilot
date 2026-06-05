# KernelPilot 中 KernelWiki 的组成、查询机制

## 1. KernelWiki 

Skill.md

````markdown
KernelWiki 知识库说明文档
---
## 配置说明
**名称：KernelWiki**
**适用场景**：用户咨询英伟达 Blackwell（SM100架构，B200芯片）、Hopper（SM90架构，H100芯片）GPU内核优化相关问题时启用；覆盖方向：tcgen05/TMEM/CLC/NVFP4、双SM协同、线程束特化、FlashAttention-4、DeepGEMM、FlashMLA、MoE混合专家、分组矩阵乘、Blackwell平台CuTe-DSL/PTX/Triton开发，或是需要CUTLASS/SGLang/vLLM/FlashInfer/PyTorch相关落地PR源码参考。
**禁用场景**：普通通用CUDA问题、CPU侧框架集成、分布式系统（DeepEP/EPLB/DualPipe）相关内容不使用本知识库。
**入参格式**：`[自然语言问题] | [--tag 标签 --type kernel] | [页面编号]`
**可用工具**：Bash、文件读取、字符检索、路径匹配

---
# KernelWiki — Blackwell & Hopper 内核优化知识库
> **知识截止日期：2026-04-27**
所有上游合并PR、技术博客摘要、版本适配记录均以该日期前开源社区正式状态为准（配置文件：`data/refresh-cutoff.yaml`）；如需更新知识库时效，执行配套刷新脚本即可延后截止日期。

本工具用于检索结构化、带交叉索引的GPU内核优化知识库，聚焦英伟达 Blackwell(SM100)、Hopper(SM90)架构；知识库收录：**2179条已合并PR、48篇技术综述文档、7场优化竞赛方案、20篇行业博客、11份官方文档摘要**。

## 启用规则
用户提出下述问题时，启用本知识库：
### 启用范围
1. **Blackwell(SM100)内核编程**：tcgen05 MMA张量核、TMEM片上共享存储、CLC缓存控制、双SM协同计算、NVFP4数据格式、FP8/FP4块缩放量化、PDL/GDC硬件特性
2. **主流内核实现**：FlashAttention-4、DeepGEMM、FlashMLA、NSA注意力、GatedDeltaNet、NVFP4通用矩阵乘/向量乘、融合版MoE、门控双路GEMM
3. **性能调优场景**：SM算力利用率低、访存瓶颈、寄存器溢出压力、计算密集型瓶颈、尾部算子低效、流水线阻塞等性能劣化问题
4. **Blackwell专用领域语言**：CuTe DSL、内嵌PTX汇编的CUDA C++、Triton框架Blackwell适配开发
5. **Hopper迁移至Blackwell**：WGMMA张量指令替换为tcgen05、寄存器累加改TMEM片上存储累加器的改造方案
6. **源码PR溯源**：vLLM/SGLang/FlashInfer/CUTLASS/PyTorch针对SM100的功能落地实现细节
7. **竞赛优化方案**：GPU Mode NVFP4黑客松、MLSys2026 FlashInfer赛道获奖实现

### 禁止启用范围
- 和Blackwell/Hopper张量核无关的通用CUDA基础问题
- 主机侧框架业务集成（模型加载、请求调度、调度策略设计）
- 分布式训练相关：DeepEP、EPLB、DualPipe不在知识库覆盖范畴

## 知识库查询用法
所有命令在知识库根目录（本`SKILL.md`所在文件夹）执行；脚本自动定位知识库根路径，**无需配置环境变量**。

### 方式1：统一检索（自然语言提问首选）
```bash
# 自然语言查询：Blackwell上门控双路GEMM算子融合实现
python3 scripts/query.py "how to fuse gate-up dual GEMM on Blackwell"
# 按标签+算子类型筛选
python3 scripts/query.py --tag nvfp4 --type kernel
# 指定开源仓库，限制返回条数
python3 scripts/query.py --repo cutlass --limit 20
# 按性能问题筛选，精简输出
python3 scripts/query.py --symptom tail-effect --compact
```
可选过滤参数：
`--type`算子类型、`--tag`硬件/技术标签、`--repo`开源仓库、`--language`编程语言、`--architecture`GPU架构、`--symptom`性能故障、`--confidence`可信度、`--limit`结果条数、`--compact`精简输出、`--paths-only`仅返回文档路径。
> 参数支持别名匹配：`--tag UMMA`自动匹配tcgen05，`--architecture B200`自动匹配sm100。

### 方式2：通过页面ID/路径调取单篇文档
```bash
# 按页面ID读取
python3 scripts/get_page.py kernel-flash-attention-4
# 读取指定PR文档
python3 scripts/get_page.py pr-cutlass-2472
# 附带溯源源码链接
python3 scripts/get_page.py kernel-flash-attention-4 --follow-sources
# 仅输出正文内容
python3 scripts/get_page.py kernel-flash-attention-4 --body-only
```

### 方式3：全文正则检索（知识库正文+PR文档）
```bash
# 检索tcgen05.fence相关代码片段
python3 scripts/grep_wiki.py "tcgen05\\.fence"
# 仅在知识库文档中检索「2-CTA反向算子」
python3 scripts/grep_wiki.py "2-CTA backward" --only wiki
# 多关键词任意匹配：nvfp4 + block_scale
python3 scripts/grep_wiki.py "nvfp4" "block_scale" --any
```

### 方式4：预生成交叉索引目录（存放于`queries/`）
- `queries/by-problem.md`：性能故障→优化思路→可用技术方案
- `queries/by-technique.md`：15项主流优化技术，附带适配架构、落地可信度、参考源码数量
- `queries/by-hardware-feature.md`：tcgen05/TMEM/CLC/TMA/NVFP4等硬件特性→关联知识库文档+PR记录
- `queries/by-kernel-type.md`：GEMM/注意力/MoE/MLA/门控DeltaNet等算子分类索引
- `queries/by-language.md`：CuTe-DSL/CUDA-C++/PTX/Triton→开发指南+配套内核源码
- `queries/by-repo.md`：CUTLASS/SGLang/vLLM/FlashInfer/PyTorch/DeepGEMM全量2179条PR归档

### 方式5：入门导读、规范定义、示例文档（`references/`目录）
- `references/primer.md`：知识总览（硬件特性、优化技术、性能问题、标准文档ID），宽泛类问题优先查阅
- `references/schema.md`：文档头部元数据规范、可信度分级、可复现标准、统一术语、别名对照表
- `references/examples.md`：10组查询示例：用户问题→查询指令→知识库输出样例

## 知识库输出规范（基于本库作答需遵守）
1. **标注文档来源**：附带文档路径（如`wiki/kernels/flash-attention-4.md`）与页面ID（`kernel-flash-attention-4`）
2. **溯源参考资料**：顺着文档`sources:`字段追溯至原始PR、技术博客、官方文档
3. **严格区分可信度等级**：优先级 `verified(实测验证) > source-reported(源码佐证) > inferred(合理推导) > experimental(试验性)`；试验/推导结论必须明确标注
4. **附带可运行代码**：文档包含可用代码片段时必须贴出；优化技术/内核/编程语言类文档全部经过校验，代码可编译复现
5. **性能数据完整标注六要素**：`GPU型号、数据类型、张量尺寸、性能指标、实测数值、数据源ID`

## 知识库存量（知识截止：2026-04-27）
- **Markdown文档总计：2265篇**：2179条PR归档 + 48篇优化综述 + 20篇技术博客 + 11份官方文档 + 7场竞赛方案
- `candidates/`目录6份待归类清单：收录2025.01–2026.04合计4222条合并PR（分类：收录/暂缓/剔除）
- `artifacts/`目录89份源码资源包：PR变更片段、内核源码、博客配套代码；通过`PROVENANCE.yaml`绑定上游代码Git哈希值
- `queries/`6套自动生成交叉索引
- 受控术语库：`data/tags.yaml`80+技术标签、`data/aliases.yaml`别名映射表
- 版本适配管理：单文档`version_sensitive:<id>`+全局`data/version-claims.yaml`双校验版本适配关系，双向一致性自动校验
- 校验脚本：`scripts/validate.py`全量校验（2265文档+89资源包+6清单，零错误）
- **Blackwell优先原则**：Hopper专属内容仅在标注`blackwell_relevance`字段时入库

> 截止日期为上游PR、博客快照最后一次同步更新时间；更新知识库时效：运行`scripts/refresh_candidate_ledger.py`→重新生成PR文档→修改`data/refresh-cutoff.yaml`内`cutoff_date`字段。

## 内容质量保障
1. `verified（实测验证）`等级内容：全部附带官方文档+开源落地源码佐证
2. 优化技术/内核/编程语言类文档：每篇均附带可编译运行代码片段
3. 全部PR归档：标注收录原因、状态统一为`merged(已合并)`
4. 兼容Hopper的文档：必须显式填写`blackwell_relevance`适配标识

### 专业名词简注
- SM：流式多处理器，GPU最小算力单元
- TMEM：Blackwell新型片上专用存储
- NVFP4：英伟达4bit浮点量化格式
- TCgen05：Blackwell新一代张量计算指令集
- MoE：混合专家模型
- GEMM：通用矩阵乘法
````



KernelWiki 是 KernelPilot 中负责提供外部工程知识的本地知识库。它不是一个简单的 Markdown 文档，也不是 Claude 在运行时临时上网搜索的结果，而是作为 `external/KernelWiki` 子模块接入 KernelPilot 的一套结构化知识系统。它的作用是让 Agent 在进行 GPU kernel 优化时，不只依赖模型自身的记忆，而是能够查询已有项目中的 PR、patch、源码、文档、博客、竞赛资料和工程经验。

在 GPU kernel 优化中，许多真正有价值的信息并不只存在于论文或官方教程里，而是分散在上游项目的 Pull Request、commit diff、代码注释、benchmark 结果、issue 讨论和工程文档中。例如某个 FlashAttention PR 为什么引入新的调度方式，某个 CUTLASS/CuTe patch 如何使用新的硬件特性，某个 SGLang 或 vLLM PR 为什么针对特定 shape 做专门优化，这些信息对于自动生成和优化 kernel 非常重要。KernelWiki 的目标就是把这些分散的工程知识整理成一个本地可检索、可追溯、可被 Agent 使用的知识库。

因此，KernelWiki 在 KernelPilot 里的角色可以理解为“Agent 的外部工程记忆”。Claude 在优化 kernel 时，可以通过 KernelWiki 查询已有经验，把查询结果转化成下一版 candidate kernel 的设计假设，然后再通过 correctness test、benchmark 和 profiling 验证这个假设是否成立。KernelWiki 本身不直接证明某个实现正确，也不直接证明某个实现更快，它只是提供 prior art 和 evidence。最终是否采用某个技巧，仍然要以目标硬件上的真实测试结果为准。

### 目录组成

在 KernelPilot 仓库中，KernelWiki 位于 `external/KernelWiki`。这个目录是一个 git submodule

KernelWiki 的核心组成可以抽象为几个部分：`sources/`、`wiki/`、`artifacts/`、`data/` 和 `scripts/`。其中 `sources/` 保存外部来源页面，`wiki/` 保存综合知识页面，`artifacts/` 保存与来源页面相关的源码、patch、diff 或其他产物，`data/` 保存别名和索引辅助数据，`scripts/` 提供查询、打开页面、grep 和验证知识库的工具。

```text
external/KernelWiki/
├── sources/        # 外部来源页面，例如 PR、博客、文档、竞赛资料
├── wiki/           # 综合整理后的主题知识页面
├── artifacts/      # 与 PR、博客、竞赛等来源对应的源码、patch、diff、脚本
├── data/           # 别名映射、术语映射、索引辅助数据
├── scripts/        # query.py、grep_wiki.py、get_page.py、validate.py 等查询工具
└── 其他说明和配置文件
```

这个结构的关键思想是将“原始资料”“综合知识”“代码产物”和“查询工具”分开管理。这样 Claude 不需要一次性读取整个知识库，而是可以先用 `query.py` 召回相关页面，再用 `get_page.py` 打开具体页面，再用 `grep_wiki.py` 定位某个术语或代码符号，最后根据需要读取 `artifacts/` 里的 patch 或源码片段。

### sources ：外部来源页面

`sources/` 是 KernelWiki 中最接近原始资料的一层。它保存的是外部来源的结构化 Markdown 页面。外部来源可以是 GitHub PR、上游项目文档、技术博客、竞赛题解、代码说明或者工程经验记录。

一个 source 页面通常不是简单复制网页内容，而是把外部资料整理成 KernelWiki 能识别的格式。它一般包含 YAML frontmatter 和正文两部分。frontmatter 里会记录页面的结构化元信息，例如 id、type、title、repo、tags、architectures、kernel_types、languages、sources、artifact_dir 等。正文部分则会描述这个来源做了什么、解决了什么问题、涉及什么 kernel、有什么性能变化、相关代码路径是什么，以及这个来源为什么值得关注。

例如，一个 SGLang PR source 页面可能表示：这个 PR 对某个 CUDA kernel 做了优化，涉及 TMA、Blackwell、attention 或 GEMM，关联某个 artifact 目录，里面保存了 patch 和关键源码。Claude 后续查询时，可以根据 repo、tag、architecture、kernel type 等字段快速定位到这个页面。

`sources/` 的价值在于保留知识的出处。Claude 不能只看到一个抽象结论，还应该能追溯到这个结论来自哪个 PR、哪个 patch、哪个上游文件或哪个文档。这对工程可信性非常重要，尤其当 Claude 准备借鉴某个实现细节时，必须记录来源和适配内容。

### wiki ：综合知识页面

`wiki/` 是 KernelWiki 中更高层次的综合知识页面。如果说 `sources/` 更像原始资料库，那么 `wiki/` 更像主题化的知识总结库。它会把多个 source 页面围绕某个主题组织起来，形成对某类 kernel、某种硬件特性或某类优化技术的系统说明。

例如，`wiki/` 中可能会有关于 FlashAttention、SM100、TMA、tcgen05、persistent scheduling、memory-bound kernel、tensor core path、GEMM epilogue fusion 等主题的页面。这些页面通常不只是描述某一个 PR，而是综合多个来源，回答更高层次的问题：这个优化技术适用于什么场景，解决什么性能瓶颈，在哪些上游项目中出现过，相关的 PR 和代码路径有哪些，使用时有什么限制。

对于 Claude 来说，`wiki/` 页面很适合作为“快速理解某个主题”的入口。比如 Claude 正在优化 B200 上的 attention kernel，它可以先查询 SM100 或 FlashAttention 相关 wiki 页面，了解已有的高层设计思路；如果需要更细节的代码或 patch，再通过页面中的 sources 字段追到具体 source 页面或 artifact。

这就是 `wiki/` 和 `sources/` 的关系：`wiki/` 负责总结和组织主题知识，`sources/` 负责保留可追溯的外部来源。

### artifacts ：代码、patch 与工程产物

`artifacts/` 是 KernelWiki 中最接近代码的一层。它保存与 source 页面关联的实际工程产物，例如 PR 的 `diff.patch`、关键源码文件、脚本、配置文件、metadata、竞赛解法或 benchmark 片段。

这层非常重要，因为 kernel 优化往往不能只看文字描述。很多时候，真正有价值的细节在代码里。例如某个 PR 是如何组织 shared memory 的，某个 CUTLASS/CuTe 实现如何写 epilogue，某个 FlashAttention 变体如何做 block scheduling，某个 Triton kernel 如何处理边界条件，这些信息需要通过源码或 patch 才能看清楚。

KernelWiki 的查询脚本支持检查页面是否有关联代码产物。例如 `query.py --has-code` 会筛选出 artifact 目录中包含源码、patch 或脚本的页面。`get_page.py --include-code` 则可以在打开具体页面时进一步打印关联 artifact 中的代码或 patch。这样 Claude 不只是看到“有人做过这个优化”，还可以看到“代码大概怎么做”。

不过，这并不意味着 Claude 可以直接照抄 artifact 中的代码。KernelPilot 的原则是：如果某个外部来源直接影响实现代码，必须记录来源、版本、路径、许可证或通知，以及具体适配内容。并且无论借鉴了什么代码或技巧，最终都必须在当前 workload 上重新通过 correctness 和 benchmark。

### data ：术语别名与查询辅助信息

`data/` 目录保存一些查询辅助数据，其中最典型的是别名映射，例如 `aliases.yaml`。这个文件用于解决 kernel 优化领域术语复杂、同义词多的问题。

例如，同一个硬件或技术可能有多种叫法。B200 可能和 Blackwell、SM100 相关；UMMA 可能和 tcgen05 相关；tensor memory 可能写作 tmem；FlashAttention-4 可能简称 FA4。Claude 查询时不一定总能输入和知识库页面完全一致的术语，如果没有别名映射，很多相关页面就召回不到。

`query.py` 会读取别名映射，对用户输入的关键词进行扩展和归一化。这样当 Claude 查询 `B200` 时，系统可以同时考虑 `sm100` 或 `blackwell` 相关页面；当 Claude 查询 `UMMA` 时，也可能匹配到 `tcgen05` 相关资料。

这说明 KernelWiki 不是纯粹的字符串搜索，而是引入了轻量的术语系统。对于一个面向 Agent 的知识库来说，这非常重要。因为 Agent 查询时会使用自然语言和工程术语混合表达，如果没有别名扩展，召回效果会很不稳定。

### scripts ：查询、搜索、打开页面和验证工具

`scripts/` 是 Claude 实际使用 KernelWiki 的主要入口。它不是让 Claude 手工遍历目录，而是提供几个脚本来完成不同层次的检索。

`query.py` 是主查询工具。它会加载 `sources/` 和 `wiki/` 下的 Markdown 页面，解析 frontmatter 和正文，然后根据关键词、repo、tag、language、architecture、symptom、confidence、has-code 等条件过滤和排序。它的查询方式更像轻量级的关键词检索和元数据检索，而不是大模型语义搜索。它会优先考虑标题命中，其次是 tag、technique、hardware feature、kernel type、language 等字段命中，再其次是正文命中。

例如 Claude 可以运行：

```bash
cd {{KERNELWIKI_ROOT}}
python3 scripts/query.py "B200 int8 GEMM tensor core" --limit 10 --compact
python3 scripts/query.py --repo sglang --tag tma --compact
python3 scripts/query.py --architecture sm100 --compact
python3 scripts/query.py "SM100 attention" --has-code --limit 10 --compact
```

`grep_wiki.py` 更适合精确搜索。如果 Claude 已经知道某个术语、API、硬件指令或代码符号，比如 `tcgen05`、`tmem`、`cp.async`、`block_scale`，就可以用 `grep_wiki.py` 在 wiki、sources 或 artifacts 中搜索，并输出匹配行和上下文。例如：

```bash
python3 scripts/grep_wiki.py "tcgen05|tmem" --only all --context 2
python3 scripts/grep_wiki.py "block_scale" --only artifacts --context 3
```

`get_page.py` 用于打开具体页面。当 `query.py` 返回某个页面 id 后，Claude 可以用 `get_page.py` 查看完整内容。它还支持 `--follow-sources` 和 `--include-code`。前者用于追踪一个综合 wiki 页面引用了哪些 source，后者用于查看关联 artifact 中的源码、patch 或脚本。例如：

```bash
python3 scripts/get_page.py kernel-flash-attention-sm100-mla-topk --follow-sources
python3 scripts/get_page.py pr-cutlass-2472 --include-code
```

`validate.py` 则主要用于维护 KernelWiki 本身，检查页面结构、索引、frontmatter、引用关系等是否正常。它不是每次 kernel 优化都必须运行的脚本，但对于知识库维护很重要。

### 页面格式：frontmatter 与正文

KernelWiki 的页面通常采用 Markdown 加 YAML frontmatter 的格式。frontmatter 是结构化元数据，正文是解释性内容。这个设计使得同一个页面既能被脚本检索，又能被 Claude 阅读理解。

一个典型页面可能类似：

```markdown
---
id: kernel-flash-attention-sm100-mla-topk
type: wiki-kernel
title: FlashAttention SM100 MLA TopK
repo: flash-attention
tags:
  - flashattention
  - sm100
  - tma
  - attention
architectures:
  - sm100
kernel_types:
  - attention
languages:
  - cuda
  - cute
sources:
  - pr-flashattention-xxxx
artifact_dir: artifacts/prs/flash-attention/PR-xxxx
confidence: high
---

# FlashAttention SM100 MLA TopK

正文部分描述这个 kernel 的优化动机、相关硬件特性、上游来源、实现注意点和性能结论。
```

frontmatter 让脚本可以做结构化过滤。例如 Claude 可以按 `repo=sglang` 查询，也可以按 `architecture=sm100` 查询，还可以按 `tag=tma` 查询。正文则让 Claude 了解页面的语义内容。只有 frontmatter 没有正文，Agent 很难理解；只有正文没有 frontmatter，脚本又很难精准检索。因此这两部分缺一不可。

## 2. KernelWiki 的查询流程

Claude 在 KernelPilot 中查询 KernelWiki 通常不是一次命令完成，而是一个逐步缩小范围的过程。它会先用 `query.py` 做主题召回，再用 `get_page.py` 打开相关页面，再用 `grep_wiki.py` 定位具体术语或代码符号，必要时再用 `--follow-sources` 或 `--include-code` 追溯来源和查看 artifact。

以优化 B200 上的 `int8_scaled_mm` 为例，Claude 可能首先运行：

```bash
cd {{KERNELWIKI_ROOT}}
python3 scripts/query.py "B200 int8 GEMM tensor core" --limit 10 --compact
```

如果结果太宽泛，它会进一步限定：

```bash
python3 scripts/query.py "SM100 int8 GEMM tcgen05" --limit 10 --compact
python3 scripts/query.py --repo sglang --tag int8 --compact
python3 scripts/query.py --repo sglang --tag tma --compact
```

如果 Claude 想查某个具体术语，例如 `tmem` 或 `tcgen05`，它会运行：

```bash
python3 scripts/grep_wiki.py "tmem|tcgen05" --only all --context 2
```

当它找到相关页面 id 后，再用：

```bash
python3 scripts/get_page.py <page-id> --follow-sources
```

如果这个页面有关联代码产物，则进一步使用：

```bash
python3 scripts/get_page.py <page-id> --include-code
```

查询结束后，Claude 不会直接把结果当作最终结论，而是把有用信息写入 workspace 的 `ledgers/research-digest.md` 或 `ledgers/tuning-decisions.md`。例如它可能记录：查询了什么、查到什么、为什么和当前任务相关、决定尝试哪个候选优化方向，以及如何验证这个方向。

KernelWiki 的查询结果必须转化为可验证的优化假设，才能进入 KernelPilot 的算子优化流程。

假设 Claude 当前有一个 correctness pass 但性能不达标的 candidate。它查询 KernelWiki 后发现某个上游实现通过 fused epilogue 减少了输出侧内存访问。正确的使用方式不是直接宣称“fused epilogue 一定有效”，而是形成一个假设：对于当前 `M=64,N=2048,K=2048,bias=true` 的 workload，把 bias 加法融合进 epilogue 可能减少一次额外访存，从而降低延迟。

这个假设随后要进入实际实现。Claude 修改 `kernel.cu`，生成 candidate_v3，然后重新编译、跑 correctness test、跑 benchmark。如果结果证明 correctness 通过且 latency 降低，才可以把这个方向记入 `optimization-ledger.md`。如果结果失败，也要写入 `attempt-ledger.md`，说明这个 KernelWiki 启发在当前任务中没有带来收益。

这个流程体现了 KernelPilot 的核心原则：外部知识只提供方向，当前任务的真实结果必须由测试决定。

## 3.  SDAA Wiki

如果要把 KernelPilot 的方法迁移到 SDAA/太初芯片，不能只替换 CUDA 语法或 benchmark 命令。更关键的是，需要建立一个类似 KernelWiki 的 SDAA Wiki。原因是 Agent 要写出高质量 SDAA kernel，必须知道目标平台的编程模型、API、编译器行为、内存层级、调度机制、性能计数器、已有算子实现和常见错误。

如果没有 SDAA Wiki，Claude 只能依赖通用模型记忆，而模型对国产芯片的具体语法、性能特性和工程经验通常非常有限。这样生成的代码很容易停留在“看起来像代码”的层面，却无法真正编译、运行和优化。

SDAA Wiki 的作用应该类似 KernelWiki：为 Agent 提供本地可查询、来源可追踪、面向 SDAA kernel 优化的工程知识库。它应该服务于几个问题：SDAA kernel 该怎么写，Torch-SDAA 中已有算子如何实现，TecoDNN/TecoBLAS/CustomDNN 有哪些参考，常见编译错误怎么修，profiler 指标怎么看，某些 shape 的历史最佳实现是什么，什么优化技巧在太初芯片上有效。

### 目录结构

如果迁移到 SDAA，可以参考 KernelWiki 的思想，但需要根据 SDAA 生态重新设计目录。一个合理的结构可以是：

```text
external/SDAAWiki/
├── sources/
│   ├── docs/              # 官方文档、编程手册、runtime API、编译器说明
│   ├── prs/               # Torch-SDAA、TecoDNN、TecoBLAS 等项目 PR 或 commit 页面
│   ├── examples/          # 官方示例、内部样例、教学样例
│   ├── issues/            # 常见 bug、编译错误、运行时错误、性能异常记录
│   └── benchmarks/        # 历史 benchmark 记录和性能对照
├── wiki/
│   ├── kernels/           # GEMM、softmax、layernorm、attention、reduce 等算子主题
│   ├── hardware/          # 太初芯片架构、核函数执行模型、内存层级
│   ├── techniques/        # 向量化、tiling、shared/local memory、pipeline、fusion 等技巧
│   ├── runtime/           # SDAA runtime、Torch-SDAA binding、stream/event、memory API
│   ├── compiler/          # 编译器选项、常见报错、优化开关、代码生成限制
│   └── profiling/         # profiler 指标、瓶颈分析、性能计数器解释
├── artifacts/
│   ├── docs/              # 文档快照或示例代码
│   ├── prs/               # PR patch、关键源码文件
│   ├── examples/          # 可编译示例工程
│   └── benchmarks/        # 原始 benchmark 日志、profile 报告
├── data/
│   ├── aliases.yaml       # 术语别名，例如 SDAA/太初、TecoDNN/tecodnn 等
│   ├── ops.yaml           # 算子分类、输入输出、reference、测试模板
│   ├── errors.yaml        # 常见错误模式和修复建议
│   └── metrics.yaml       # profiler 指标解释
└── scripts/
    ├── query.py
    ├── grep_wiki.py
    ├── get_page.py
    ├── validate.py
    └── ingest_*.py
```

这个结构保留 KernelWiki 的核心思路，但把知识源换成 SDAA 生态。它不应该只是 CUDA Wiki 的翻译，而应该围绕 SDAA 的真实编程模型、工具链和性能分析体系重新组织。

### 内容

SDAA Wiki 的 `sources/` 应该收集所有能帮助 Agent 写和优化 SDAA kernel 的外部来源。第一类是官方文档，例如 SDAA 编程手册、runtime API、编译器说明、内存模型、线程/核函数执行模型和 profiler 使用说明。第二类是源码来源，例如 Torch-SDAA 的算子实现、TecoDNN/TecoBLAS/CustomDNN 的公开或内部示例、已有 kernel benchmark 工程。第三类是工程经验来源，例如常见编译错误、运行时错误、精度错误、性能异常和对应修复方式。第四类是 benchmark 来源，例如某些 shape 上不同实现的延迟、带宽、吞吐或 profiler 指标。

每一个 source 页面都应该记录清楚来源路径、版本、适用范围和可信度。比如一个 Torch-SDAA softmax 实现页面，应该说明它来自哪个仓库、哪个 commit、对应哪个文件、支持什么 dtype、适合什么 shape、有什么已知限制。如果只是内部经验，也应该说明是谁记录的、在哪个环境下验证过、是否有 benchmark 或 correctness 结果。

这样设计的目的，是让 Claude 查到资料后能判断它是否适合当前任务，而不是盲目套用。

### 页面组织

SDAA Wiki 的 `wiki/` 应该按照 Agent 做任务时真正会问的问题来组织，而不是简单复制文档目录。

例如，在 `wiki/kernels/` 中，可以为每类算子建立页面：

```text
wiki/kernels/gemm.md
wiki/kernels/softmax.md
wiki/kernels/layernorm.md
wiki/kernels/reduce.md
wiki/kernels/attention.md
wiki/kernels/elementwise.md
```

这些页面不应该只写算子定义，而应该写清楚在 SDAA 上实现这个算子时的关键问题：输入输出布局、推荐 tiling、精度注意事项、reference 实现、常见错误、benchmark 方法、已有实现路径和可参考 source 页面。

在 `wiki/hardware/` 中，可以组织太初芯片相关硬件知识，例如内存层级、计算单元、数据搬运机制、并行执行模型、支持的数据类型、对齐要求等。这些信息对 kernel 生成非常关键。

在 `wiki/compiler/` 中，可以组织编译器相关知识，例如编译命令、常见报错、可用优化参数、某些语法限制、错误信息和修复建议。

在 `wiki/profiling/` 中，可以组织 profiler 指标说明。例如某个指标表示内存带宽利用率，某个指标表示计算单元利用率，某个 stall 原因对应什么瓶颈。没有这些解释，Agent 即使拿到 profile 报告，也很难转化成下一步优化。

### SDAA Wiki artifacts 

SDAA Wiki 的 `artifacts/` 应该保存能够直接帮助 Agent 理解和复现实验的产物。对于官方文档，可以保存相关示例代码或文档快照。对于 PR 或 commit，可以保存 patch、关键源文件和改动摘要。对于 benchmark，可以保存原始日志、输入 shape、环境信息和 profile 报告。对于错误案例，可以保存最小复现代码、错误日志和修复后的版本。

例如，一个 GEMM 优化案例可以有这样的 artifact：

```text
artifacts/benchmarks/gemm/m64_n2048_k2048/
├── baseline.log
├── candidate_v1.log
├── candidate_v2.log
├── profile_candidate_v2.txt
├── kernel_v1.sdaa
├── kernel_v2.sdaa
└── metadata.json
```

这样 Claude 查询到这个案例时，不只是看到一段文字总结，还可以看到原始日志、代码版本和 profile 信息。这会极大提高 Agent 的可用性和可信性。

### SDAA Wiki  data 

SDAA Wiki 的 `data/` 目录应该比 KernelWiki 更重视术语标准化和错误模式归纳，因为国产芯片生态中的术语、API 和工具链可能不像 CUDA 那样被模型充分学习。

`aliases.yaml` 应该记录各种别名和同义词。例如 SDAA、太初、TecoAI、Torch-SDAA、tecodnn、TecoDNN、tecoBLAS 等可能需要统一。某些算子也可能有不同叫法，例如 scaled_mm、int8_gemm、quant_matmul 等。

`ops.yaml` 可以记录算子定义、输入输出、reference、测试模板和 benchmark 模板。例如 GEMM 需要记录 M/N/K、dtype、layout、bias、scale；softmax 需要记录 axis、mask、数值稳定性；layernorm 需要记录 epsilon、归约维度、gamma/beta。

`errors.yaml` 很有价值。它可以把常见编译错误、链接错误、runtime 错误、精度错误和性能异常归纳成模式。例如某个错误信息对应 include path 缺失，某个 runtime 错误对应 tensor device 不一致，某个精度错误通常来自 layout 误解，某个性能异常通常来自未同步或 benchmark 方法错误。

`metrics.yaml` 则用于解释 profiler 指标。它应该记录每个指标的含义、单位、正常范围、异常表现和可能优化方向。这样 Agent 才能把 profile 结果变成可执行的下一步优化。

### SDAA Wiki query

SDAA Wiki 可以复用 KernelWiki 的三类查询入口：主题查询、关键词 grep 和页面读取。

`query.py` 应该支持自然语言关键词和结构化过滤。它应该能按算子类型、dtype、芯片型号、库名、错误类型、性能瓶颈和是否有代码 artifact 过滤。例如：

```bash
python3 scripts/query.py "SDAA int8 GEMM layout" --limit 10 --compact
python3 scripts/query.py --op softmax --dtype fp16 --compact
python3 scripts/query.py --error "undefined symbol" --compact
python3 scripts/query.py --metric memory_bandwidth --compact
```

`grep_wiki.py` 应该支持在 wiki、sources 和 artifacts 中搜索具体 API、错误信息、函数名和 profiler 指标。例如：

```bash
python3 scripts/grep_wiki.py "sdaart" --only all --context 2
python3 scripts/grep_wiki.py "TecoDNN" --only artifacts --context 3
python3 scripts/grep_wiki.py "invalid device" --only sources --context 2
```

`get_page.py` 应该支持按 id 或路径打开页面，并支持 `--follow-sources` 和 `--include-code`。Agent 查到某个 softmax 优化页面后，应该能够继续追到相关官方示例、Torch-SDAA 源码片段和 benchmark artifact。

如果后续知识库规模变大，也可以引入 embedding 检索，但初始版本不一定需要。对工程知识库来说，结构化 frontmatter、关键词查询和 artifact 追踪已经能解决大量问题。

### 页面格式

SDAA Wiki 的页面应该保持统一格式，这样 Agent 才容易读取和写入。一个 source 页面可以采用类似格式：

```markdown
---
id: source-torch-sdaa-softmax-001
type: source-code
title: Torch-SDAA Softmax Kernel Implementation
repo: torch-sdaa
path: torch_sdaa/ops/softmax/...
commit: <commit-sha>
op_type: softmax
dtype:
  - fp16
  - fp32
hardware:
  - sdaa
tags:
  - softmax
  - reduction
  - numerical-stability
artifact_dir: artifacts/prs/torch-sdaa/softmax-001
confidence: medium
---

# Torch-SDAA Softmax Kernel Implementation

本页面记录 Torch-SDAA 中 softmax 算子的实现路径、输入输出语义、关键 kernel 调用、数值稳定性处理和可参考的 benchmark 结果。
```

一个 wiki 页面可以采用类似格式：

```markdown
---
id: kernel-sdaa-softmax
type: wiki-kernel
title: SDAA Softmax Kernel Optimization
op_type: softmax
tags:
  - softmax
  - reduction
  - fp16
  - numerical-stability
sources:
  - source-torch-sdaa-softmax-001
  - source-doc-sdaa-reduction-001
---

# SDAA Softmax Kernel Optimization

本页面总结在 SDAA 上实现 softmax 的常见策略，包括最大值归约、指数计算、sum 归约、数值稳定性、axis 处理、benchmark 方法和常见错误。
```

统一页面格式的好处是 Claude 可以稳定解析，query 脚本可以稳定过滤，review 时也能检查来源是否完整。

## 4. SDAA Wiki 与算子生成 workflow 的结合

SDAA Wiki 需要和算子生成 workflow 紧密结合，而不是单独存在。一个完整流程应该是：

```text
用户提出 SDAA 算子优化任务
  ↓
Claude 抽象 K/R/W
  ↓
Claude 查询 SDAA Wiki 中该算子的语义、API、已有实现和测试模板
  ↓
Claude 创建 standalone workspace
  ↓
Claude 生成 SDAA kernel、binding、correctness test、benchmark
  ↓
如果编译失败，Claude 查询 SDAA Wiki 的 errors.yaml 或相关错误页面
  ↓
如果 correctness 失败，Claude 查询该算子的 layout、dtype、reference 说明
  ↓
如果 benchmark 不达标，Claude 查询 profiling 和历史优化案例
  ↓
Claude 形成下一版 candidate
  ↓
服务器运行 correctness 和 benchmark
  ↓
结果写入 ledger 和 performance-map
  ↓
Codex 或 reviewer 审查证据
```

这说明 SDAA Wiki 不是一个“资料库摆设”，而是 Agent 在每个关键失败点都可以调用的知识工具。编译失败查错误库，正确性失败查语义和 layout，性能失败查 profiling 和历史优化案例，这样 Agent 才能持续迭代。

## 5. SDAA Wiki 的最小可行版本

最小版本至少应该包含：

```text
一套统一页面格式
一个 aliases.yaml
一个 query.py
一个 grep_wiki.py
一个 get_page.py
若干官方文档 source 页面
若干 Torch-SDAA 源码 source 页面
若干常见错误页面
若干 benchmark 示例
每个核心算子的 wiki-kernel 页面
```

对你的场景来说，第一批最值得建设的内容可能是：

```text
GEMM / matmul
reduce / sum / max
softmax
layernorm
elementwise fusion
Torch-SDAA extension 示例
SDAA 编译器常见错误
benchmark 正确写法
profiler 指标解释
```

这样即使知识库还不完整，也能在最关键的算子生成任务中发挥作用。

