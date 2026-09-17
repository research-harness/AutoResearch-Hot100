# PaperOrchestra：把研究材料编排为论文的宿主技能包

> 固定快照：[Ar9av/PaperOrchestra](https://github.com/Ar9av/PaperOrchestra/tree/798f03a14ce582607ba2742d025691f226470641)；commit `798f03a14ce582607ba2742d025691f226470641`；snapshot `2026-09-17`；候选许可证元数据 `NOASSERTION`；审阅状态 `draft`。

## 1. 它到底是什么

📘 `Ar9av/PaperOrchestra` 是将 PaperOrchestra 论文方法转成宿主可执行技能的项目。用户提供研究想法、实验日志、LaTeX 模板、会议规则和可选图，宿主编码代理依次做提纲、绘图、文献综述、正文和内容修订，最后编译论文。它的输入假定研究材料已经存在，不是自动完成全部原始研究的执行系统。

README 引用论文中的相对优势数字，但这是作者论文结果在该仓库中的转述，不是此技能包被本次重新跑出的评估。项目还提供日志聚合器和论文 autorater 方向；它们可能帮助准备或评价写作材料，但不会把缺失实验变成真实数据。候选 API 许可为 NOASSERTION；已读 LICENSE 主体是 MIT，并另注明复刻提示的论文来源，复用时应保留该说明。

## 2. 运行时堆叠

核心是 SKILL.md 操作指令、references 中的提示与 schema，以及 Python 辅助脚本。模型推理与大部分检索由现有编码代理宿主提供；论文编译依赖用户的 TeX 环境。README 所称“不需要嵌入模型 API key”是说核心技能复用宿主能力，并不是整个工作流没有模型成本或外部网络。

固定 README 的另一段列出 Semantic Scholar、Exa 搜索 helper 和可选 PaperBanana，因此“所有脚本都不联网”的概括过强。更准确的说法是结构、覆盖和一致性检查主要可本地执行，某些可选检索与出图集成仍访问外部服务。本次只读取已列脚本和技能合同，没有安装这些集成。

## 3. 阶段机或 DAG

主流程先检查输入完整性与密度、探测 TeX 包，再生成 outline.json；绘图与文献阶段在宿主支持时并行；文献回来后可调和提纲，再以一次多模态正文调用整合，之后执行本地检查和有界修订，最后编译和记录哈希。

```mermaid
flowchart LR
    I[想法 日志 模板和规则] --> O[结构化提纲]
    O --> F[绘图与图注]
    O --> L[文献检索 核验和综述]
    L --> R[提纲调和]
    F --> W[正文整合]
    R --> W
    W --> G[确定性检查]
    G --> C[审阅 修订和回退]
    C --> P[LaTeX PDF 与来源快照]
```

`paper-orchestra/SKILL.md` 区分阻塞与警告：输入和提纲 schema 错误会停机，某些一致性及 claim-evidence 问题只报告警告。修订分数下降会回退，达到轮数或没有新问题会停止。这是“接受当前最好快照”的规则，不是独立证明论文已可投稿。

## 4. Tool / Skill / Agent 怎么切

Skill 是完整角色说明，宿主 Agent 阅读并执行；工具包括 JSON 校验、引用覆盖、孤立引用、LaTeX 检查和哈希快照。Outline、Plotting、Literature Review、Section Writing、Content Refinement 是五种写作职责，顶层 orchestrator 组织它们，benchmark 与 autorater 是评价用途的旁路。

该仓库并不自带常驻多代理服务器；“五代理”由宿主是否真的启动并行任务决定。指令中的调用次数是方法与成本预算约定，不是代码能机械保证每种宿主完全一致的网络调用量。输入聚合器也是准备资料的附加角色，不应在无授权时广泛扫描个人缓存或其他研究目录。

## 5. 文献怎么来、是否入库、引用约束

Outline 技能分别规划 Introduction 的背景文献和 Related Work 的技术簇，并给数据、指标、模型和优化器等条目加引用线索。文献代理利用宿主搜索发现候选，再通过 Semantic Scholar 等路径核对标题、时间截止与重复记录，保存 citation_pool.json 和 refs.bib。它是工作区论文池，不是已确认的跨项目文献治理服务。

已读 `citation_coverage.py` 提取 LaTeX 引用键，计算其与池的交集；其阈值实际用 `int(threshold * n_pool)` 下取整，池外引用只打印 warning。这意味着脚本注释“至少 90%”与所有小样本输入上的严格比例并不完全等价，而且单独运行该脚本不会因外来键自动阻塞。顶层还安排另一孤立引用检查，必须按整条组合流程评价。

## 6. 实验 / 代码执行

本项目主要消费 experimental_log.md，写作阶段从日志形成表和结果叙述；绘图脚本可能真实执行，但这与重做科学实验不同。日志聚合器把编码代理历史提取成结构化输入，并提示不确定数字，这属于证据整理，不是独立重测。

🔶 `claim_evidence_gate.py` 是启发式数字核对且被明确设为 WARN。它用正则抽取部分结果表达，在日志中找到相同数值片段就归入 supported；小于 0.5 的数被跳过，相同数值被去重，未抽到主张也能返回成功。它不验证指标名、单位、实验条件或数据版本是否对应，不能作为“所有数字已被独立证据支持”的保证。本文没有运行实验或这些辅助检查器。

## 7. 写稿怎么做

Outline 输出绘图计划、引言/相关工作计划和 section_plan；正文整合阶段保留已写好的 intro_relwork，结合真实图像、实验日志、引用表和会议规则生成完整 LaTeX。顶层指令强调正文阶段保持论文方法中的一次多模态调用，而不是擅自拆成若干不一致章节任务。

修订循环保存 worklog 与每轮快照，评分下降或部分维度负向变化会回退，避免为了多改几轮持续破坏原稿。最终将最佳版本复制到 final，编译后记录输入、提纲、引用、图和 TeX/PDF 哈希。哈希能说明这一版用了哪些文件，但不能证明输入日志内容真实，模拟审稿分数也不代表真实编辑决定。

## 8. 图怎么做

Plotting Agent 接收 outline.plotting_plan，其中必须区分 plot 和 diagram，声明数据来自 idea.md、experimental_log.md 或两者，设置图标识、比例和预期内容。README 将 PaperBanana 描述为可选示意图后端，未配置时走 matplotlib 方向；定量图仍应从已有日志数据生成。

图与文献并行后交给多模态正文阶段，能够让图注和叙述围绕实际图像组织。局限是图是否真的读取原始结果、数值抄录是否准确、VLM 是否看到输出像素需要执行记录证明；一张可编译的图不会自动成为观测证据。本文 Mermaid 只是技能工作流，不是调用 PaperBanana 生成的科研图片。

## 9. 和 RH 的相似点

两者都强调先有结构化计划和证据材料，再组织正文；引用、图、日志和稿件应保留关联；写作后需要确定性检查与审阅，而不是只看模型说“完成”。版本快照、回退规则和哈希能提高修订可追踪性，与 RH 的稿件版本和质量报告接口存在相似目标。

另一个相似点是技能与工具分工：长流程说明负责指导宿主，机械校验负责结构约束。两者都必须避免将检查通过解释成科学正确，尤其在输入数据和引用支持尚未验证时。

## 10. 和 RH 的不同点

PaperOrchestra 从已有实验日志与模板出发，主轴是写作生产；RH 的公开研究流程还覆盖主题、文献获取、声明证据链接、方法设计和研究阶段推进。它可以为 RH 的表达层提供参考，但不是完整实验治理系统的替代。

该项目重视对原论文提示与流程的忠实实现，文献 cutoff、调用布局和 autorater 都与复现某种写作方法有关；RH 还需要依据具体研究任务决定证据门槛与交付合同。方法复刻和用户任务最佳实现是不同目标，尤其不能用赢过某个 autorater 的文字代替更强证据。

## 11. 优点 / 缺点

优点是输入合同具体，提纲同时协调图、引用与章节；并行阶段有明确汇合点；本地检查、修订快照、回退和来源哈希较完整；宿主型技能易适配多种编码代理；许可证文本明确说明 MIT 主体及论文提示来源。

局限是高度依赖宿主执行指令的忠实度；输入日志缺证据时无法自行补实验；数字检查和引用覆盖存在启发式边界；WARN 不等于硬闸；单次长正文可能遇到上下文或输出长度限制；论文所报胜率无法直接外推至该仓库、所有宿主或任意学科。

## 12. RH 可学的 1–3 条

1. 💬 **提纲统一协调图、文献和正文。** 三者共用一份可验证计划，减少画完图才发现叙事或证据不匹配。
2. **修订必须可回退。** 留下每轮快照和接受原因，评价下降时保留更好的旧稿，而不是默认新版总更好。
3. **明确每个检查的强度。** 正则告警、引用集合校验、语义支持和独立实验验证应分别报告，不能统一叫“证据闸已过”。

## 13. 名字速查表

| 名称 | 角色 |
|---|---|
| paper-orchestra | 总体写作技能与交付协调 |
| outline-agent | 统一图、文献与章节计划 |
| plotting-agent | 图形制作和图注整理 |
| literature-review-agent | 候选检索、核验与相关工作 |
| section-writing-agent | 多模态正文整合 |
| content-refinement-agent | 有界审阅修订和回退 |
| agent-research-aggregator | 从已有日志整理写作输入 |
| citation_coverage.py | 引用池整合比例检查 |
| claim_evidence_gate.py | 基于数值匹配的非阻塞告警 |
| paper-autoraters | 论文提出的自动评价角色与材料 |

**固定提交证据入口**

- [README.md](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/README.md)
- [LICENSE](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/LICENSE)
- [skills/paper-orchestra/SKILL.md](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/skills/paper-orchestra/SKILL.md)
- [skills/outline-agent/SKILL.md](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/skills/outline-agent/SKILL.md)
- [skills/paper-orchestra/scripts/claim_evidence_gate.py](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/skills/paper-orchestra/scripts/claim_evidence_gate.py)
- [skills/literature-review-agent/scripts/citation_coverage.py](https://github.com/Ar9av/PaperOrchestra/blob/798f03a14ce582607ba2742d025691f226470641/skills/literature-review-agent/scripts/citation_coverage.py)

📌事实边界：本报告基于上述固定提交的 README、文档及关键源码实际查看，源码为所列文件的关键路径抽样；缓存字节经 Git blob 哈希核验，README 与公开固定 URL 对照一致。未安装项目依赖、启动服务或宿主代理、调用模型、执行实验或 GPU 任务、运行基准、编译论文、生成图像或发布内容。README、论文链接及示例中的性能数字均属作者报告，未做独立复现；RH 对比仅为公开职责与机制分析，不是性能或科学质量排名。
