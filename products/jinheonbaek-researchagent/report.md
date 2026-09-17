# ResearchAgent：从核心论文迭代生成问题、方法和实验设计

> 固定快照：[JinheonBaek/ResearchAgent](https://github.com/JinheonBaek/ResearchAgent/tree/babb49b51ebfcebedc39ccde12c9785be7bef46c)；commit `babb49b51ebfcebedc39ccde12c9785be7bef46c`；snapshot `2026-09-17`；候选许可证元数据 `NOASSERTION`；审阅状态 `draft`。

## 1. 它到底是什么

📘 `JinheonBaek/ResearchAgent` 是论文《ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models》的研究实现。输入核心论文标识和知识库，检索相关论文及实体，然后提出研究问题、方法和实验设计，用多维模型审阅反复改进。实际主流程会分别优化三个对象，而非只输出一个想法标题。

它的交付边界是结构化研究提案与迭代历史。虽然存在 ExperimentDesigner 和 ExperimentValidator，这些名称指实验方案撰写和评估，不是实验执行器。将它放进自动科研图谱，应定位在文献驱动构思与设计层，避免把“提出实验”误报为“已开展实验”。固定候选许可证是 NOASSERTION，公开树未见 LICENSE，本文不推定默认授予 MIT 等许可。

## 2. 运行时堆叠

README 给出 Python 入口和 OpenAI Chat Completions 使用方式；实际读到的代码依赖 requests、torch、sentence-transformers 的余弦相似度工具、tqdm 和线程池。知识库从 JSONL 加载到内存，论文信息通过 Semantic Scholar Graph API 获取；这是一套较轻的研究脚本，不是带 Web 前后端和数据库服务的产品平台。

核心边界是 KnowledgeStore、Semantic Scholar 辅助函数、ResearchPipeline 与角色类。网络请求包装器有超时与异常回退，运行稳定性还取决于服务返回格式和模型输出。README 显示可运行命令，但本次没有配置 key、安装依赖或启动入口，不能从命令存在得出当前环境已经兼容。

## 3. 阶段机或 DAG

`ResearchPipeline.run` 依次做问题生成与验证、方法开发与验证、实验设计与验证。每一段重复固定轮数，默认三轮且至少一轮，把候选及反馈加入 history，然后按平均评分选择该段最佳候选作为下一段上下文。没有分数的候选在选择时被赋予较低排序值。

```mermaid
flowchart LR
    P[核心论文] --> R[相关参考文献与实体]
    R --> Q[问题生成]
    Q --> V1[多维问题审阅]
    V1 -->|迭代| Q
    V1 --> B1[选择最佳问题]
    B1 --> M[方法开发和审阅]
    M --> B2[选择最佳方法]
    B2 --> E[实验设计和审阅]
    E --> O[提案与完整候选历史]
```

这是一条带局部循环的顺序工作流，而不是实验结果反馈驱动的自主科学发现回路。最佳问题确定后才进入方法，最佳方法确定后才进入实验设计；已读实现未显示实验设计反过来推翻问题阶段的全局搜索或人工冻结闸门。

## 4. Tool / Skill / Agent 怎么切

Agent 主要是共享 BaseAgent 上的提示角色：ProblemIdentifier、ProblemValidator、MethodDeveloper、MethodValidator、ExperimentDesigner、ExperimentValidator。ResearchPipeline 控制调用顺序；工具性的文献请求与实体计算独立于角色提示。固定树没有独立的 SKILL.md 安装体系或 MCP 工具注册表。

`ProblemValidator` 以线程池并行调用五个评价维度：Clarity、Relevance、Originality、Feasibility、Significance。每个维度各有提示、评论与评分输出，减少单一总评覆盖所有问题的含糊。但并行提示不意味着五位真实独立专家，它们仍可能共享模型偏差和相同文献盲区。

## 5. 文献怎么来、是否入库、引用约束

`s2.py` 批量请求 Semantic Scholar 的标题、摘要、年份、出版时间、引用量及 SPECTER v2 嵌入；相关文献来自核心论文的 references，再根据与核心论文嵌入的余弦相似度选取。它是沿参考文献关系找相近材料，不是全网搜索加系统综述，也不能保证覆盖最新竞争方法。

`KnowledgeStore` 从论文—实体计数构建实体频率和共现，结合条件对数概率与实体先验选相关实体。它返回启发构思的词或概念，不是带逐句原文证据的知识图谱。数据以 JSONL 和内存映射使用，已读代码没有长期文献库的版本迁移、DOI 去重和全文页码绑定。

引用约束主要体现为给各角色提供目标论文、相关论文和实体，而不是生成文稿后的 BibTeX 白名单检查。模型看过某篇论文摘要，不能证明它生成的每个创新性或方法主张都得到该文献支持；新颖性仍需更宽范围外部检索。

## 6. 实验 / 代码执行

ResearchPipeline 的 experiment 字段保存的是实验描述、理由和模型反馈，代码没有在这个主流程里启动训练、读取真实实验指标、生成数据或调用测量设备。ExperimentValidator 评的是计划质量，不能解释为对实验数据独立复算。

🔶 评分最大化也不是科学有效性保证：三轮中选平均分最高者，可能只是更善于符合审阅提示，而非真正更可行。尤其 Originality 与 Significance 是依赖背景覆盖和价值判断的维度，不能用高分替代先前工作核查、预算测试和数据可用性检查。本次没有运行模型评分，也没有报告改进幅度。

## 7. 写稿怎么做

系统写的是研究问题、方法和实验方案的结构化提案。`run` 返回最终 context，并保留 problems、methods、experiments 三组 history，供使用者检查如何从前一个候选走到被选版本。这比只给“最佳方案”更有研究透明度，因为可以查看哪些反馈改变了设计。

公开主路径没有完整论文写作器、LaTeX 模板、图表装配和最终 PDF 验收。它可以成为论文前期规划材料，但从提案到论文还缺实际研究执行、结果分析、正文证据约束与发表流程。README 的论文引用是如何引用 ResearchAgent 这项研究，不是系统生成稿件的引用管理实现。

## 8. 图怎么做

已读源码围绕文本与结构化提案，未显示自动科研制图。torch 在这里用于相关性计算，不能因为依赖里出现数值库就推断存在可视化能力。固定 README 也没有提供可据本次确认的图生成合同。

因此，本文 Mermaid 是对 ResearchPipeline 的阅读解释，不是该项目输出的实验图。若把提案交给后续执行系统，需要重新建立图表计划：每张图回答什么问题、依赖哪个实验、统计口径是什么。这个计划尚不能从一个高分的实验方案直接变成有数据支撑的图。

## 9. 和 RH 的相似点

两者都以已有论文为起点，先检索和理解研究背景，再组织问题与方法，且尝试通过审阅减少一次生成的盲点。ResearchAgent 保留候选历史，与 RH 保存研究分析、提案和评价产物的思路相近；明确阶段职责也便于定位某个提案的问题出在检索、构思还是设计。

实体共现提供一个可计算的构思启发来源，比只让模型凭记忆发散更容易解释。它仍只是线索生成，后续要通过证据和可行性检查才能成为可靠研究计划，这一点与 RH 的阶段推进目标一致。

## 10. 和 RH 的不同点

ResearchAgent 的实际范围更窄：单个核心论文上下文、内存实体库和固定轮数的提案优化。RH 的公开接口覆盖受管理论文池、声明和证据链接、主题状态、实验结果和稿件版本；不能因为两者都叫 research agent 就视为同类完整产品。

该项目的过关逻辑主要是模型评分排序，而非一组确定性研究闸门。局部最优候选也没有表示“证据充分”的资格，缺少评分时选取行为仍只是排序回退。它适合做想法辅助与研究基线，但用于重要资源投入前，应额外落实数据、代码、计算和评价协议。

## 11. 优点 / 缺点

优点是实现结构紧凑，问题—方法—实验设计的边界清楚；文献来自明确 API 和引用关系；实体计算可解释；多维审阅并行、历史完整保留；研究定位与代码产物相对一致，适合作为构思阶段基线。

局限是外部 API 可用性和嵌入缺失影响输入，异常回退可能掩盖检索失败；参考文献邻域有覆盖偏差；模型自评易受共同偏差影响；没有实际实验、写稿和图表闭环；知识实体缺原文定位；许可证未明确，复用和分发应先核实权利。

## 12. RH 可学的 1–3 条

1. 💬 **把提案拆成三个可审对象。** 问题、方法和实验设计分别保存候选与反馈，便于人工诊断而不把所有分歧混成一个总分。
2. **实体关系只作为启发。** 共现与相似度可以提出连接，但要在推进前补做新颖性与证据核验，不能自动升格为事实关系。
3. **公开最优候选的选择依据。** 连同各轮反馈和评分缺失情况交付，而不是只展示最高分的一段文字。

## 13. 名字速查表

| 名称 | 角色 |
|---|---|
| ResearchPipeline | 三段生成与验证的顺序编排 |
| KnowledgeStore | 从 JSONL 建立实体和共现统计 |
| SPECTER v2 | Semantic Scholar 提供的论文嵌入字段 |
| ProblemIdentifier | 生成或改进研究问题 |
| ProblemValidator | 五维并行问题评价 |
| MethodDeveloper | 在选定问题上形成方法 |
| MethodValidator | 对方法方案给反馈 |
| ExperimentDesigner | 形成实验计划，而非运行实验 |
| ExperimentValidator | 审阅实验计划 |
| history | 问题、方法和实验方案的迭代记录 |

**固定提交证据入口**

- [README.md](https://github.com/JinheonBaek/ResearchAgent/blob/babb49b51ebfcebedc39ccde12c9785be7bef46c/README.md)
- [code/pipelines/research_pipeline.py](https://github.com/JinheonBaek/ResearchAgent/blob/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/pipelines/research_pipeline.py)
- [code/knowledge/store.py](https://github.com/JinheonBaek/ResearchAgent/blob/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/knowledge/store.py)
- [code/utils/s2.py](https://github.com/JinheonBaek/ResearchAgent/blob/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/utils/s2.py)
- [code/pipelines/agents/problem_validator.py](https://github.com/JinheonBaek/ResearchAgent/blob/babb49b51ebfcebedc39ccde12c9785be7bef46c/code/pipelines/agents/problem_validator.py)

📌事实边界：本报告基于上述固定提交的 README、文档及关键源码实际查看，源码为所列文件的关键路径抽样；缓存字节经 Git blob 哈希核验，README 与公开固定 URL 对照一致。未安装项目依赖、启动服务或宿主代理、调用模型、执行实验或 GPU 任务、运行基准、编译论文、生成图像或发布内容。README、论文链接及示例中的性能数字均属作者报告，未做独立复现；RH 对比仅为公开职责与机制分析，不是性能或科学质量排名。
