# AIRAS：以预注册、运行输出和版本历史约束科研产物

> 固定快照：[airas-org/airas](https://github.com/airas-org/airas/tree/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f)；commit `72c4b5c83eb33a5b5709fa6fc9069f9b6425664f`；snapshot `2026-09-17`；候选许可证元数据 `MIT`；审阅状态 `draft`。

## 1. 它到底是什么

📘 `airas-org/airas` 是一个面向科研自动化的工具与工作流项目，固定 README 以机器学习研究为当前主要应用。它通过 PyPI 包提供 MCP 服务、宿主插件和验证 CLI，把检索、假设、设计、实验、图表与论文连起来。特色不是只让模型按步骤写文，而是把声明和实验条件放进 Git 中的研究记录，并要求报告值来自运行输出。

这里有三种不同的交付层：宿主技能管理研究步骤，MCP 工具操作研究资产，verify-record/verify-paper 供实验仓库 CI 执行。模板、论文数据库和评估逻辑还有三个独立兄弟仓库。本文没有读取这些兄弟仓库的固定提交，因此不会把它们所有功能纳入本次源码核验范围。

## 2. 运行时堆叠

安装表面是 uvx 启动 Python MCP 服务；生成工作可以由已有编码代理完成，`get_generation_prompt` 提供提示与 schema，不强制每一步再调用后端模型。也保留通过 LiteLLM 和多个供应商生成的工具路线。实验以 GitHub Actions 或 Seyval 执行并保存结果，Git 仓库承担后续恢复所需状态。

源码还包含 LangGraph 的实验迭代图，用于代码生成、sanity、pilot、分析和决策等组织。这个后端图与 README 当前主推的宿主技能流程应分开读，不能把它们强行拼成一个唯一调用序列。共同底座是 GitHub 配置、结构化设计、run_id、结果目录和可验证记录。

## 3. 阶段机或 DAG

README 的 auto-research 八步依次为准备仓库、检索论文、假设设计、预注册论文、写实验代码、运行实验、分析结果和发布论文。预注册将声明、判据与预测区间先写入记录，再用执行输出实现论文里的数值；这与边写实验边任意调整结论不同。

```mermaid
flowchart LR
    L[来源和研究设计] --> F[声明预注册与冻结提交]
    F --> C[实验代码和环境合同]
    C --> R[后端运行]
    R --> O[导入输出与 provenance]
    O --> D[派生结果和判决]
    D --> P[数值及图表映射]
    P --> V[记录与论文验证]
    V --> B[CI 生成正式 PDF]
```

实验迭代图另有 scale_up、redesign、complete 和 abort 路由；这些只是代码中的控制选择，不是本文启动过的研究活动。源码和技能若允许探索性追加，新声明、旧声明、旧结果的关系必须清晰保留，不能通过删除历史来制造预先声明的假象。

## 4. Tool / Skill / Agent 怎么切

宿主 Agent 负责提出研究内容、读文献和写分析，Skill 负责跨步骤约定；MCP 工具负责 prepare_repository、register_sources、preregister_record、dispatch_experiment、import_run_outputs、render_chart 等具体动作。CLI 的验证器则承担不能仅靠提示执行的检查。

`record.py` 把 hypothesis、claim、design、run 组成树，并保留 assumptions 与 rationale。verifier 可以是实验、Lean 或 LLM judge，但同一文件明确：LLM judge 执行工具，以及 Lean/LLM judge 的闸门重执行尚未实现。存在 schema 和解析代码不能写成所有验证器都已经端到端可运行。

## 5. 文献怎么来、是否入库、引用约束

README 描述论文搜索整合内部论文库、OpenAlex、Semantic Scholar 和 arXiv。`register_sources` 固定全文快照，为论文或代码来源建立身份；代码源还记录 URL、commit 与所选文件。passages 引用快照中的原文，并可被 hypothesis.grounded_on 或 claim.cites_passages 等字段关联。

`verify.py` 实际检查来源有 verified_by、全文路径符合合同、文件存在且 SHA-256 相符、引文片段能在全文中找到；还检查声明引用的 passage 在该历史版本已经存在。其 TODO 同时说明作者、年份、venue 仍来自提交元数据，存在性和 PDF 标题检查不代表这些字段全被认证；全文中出现某句也不等于它支持研究者赋予的推理关系。

## 6. 实验 / 代码执行

`dispatch_experiment` 接收 GitHub 仓库、分支、run_id、sanity/pilot/full 和 backend，返回 execution_id 与 URL。`get_experiment_run_status` 区分后端：GitHub Actions 路线在已读代码中不直接返回日志尾部，Seyval 才在结束后尝试取 stdout/stderr。输出由 import 路线带 provenance 拉回，再与后端存储或导入时哈希对照。

🔶 `derive_results.py` 让写入与检查复用派生逻辑，判断 supported、refuted 或 inconclusive，避免模型自行改判决；不过 ClaimStatus 的注释明确“声明是否发生在这些运行之前”尚未在该状态计算中建模。已读工具文档的预注册保证比这个局部实现更强，必须联合历史和来源闸核验，不能仅凭 verified=True 判断完整预注册时序成立。README 也承认数据泄漏、基准投机和设计偏离仍是待解决问题。

## 7. 写稿怎么做

预注册阶段先组织论文声明及判据，实际数字通过 `\airasval{run.metric}` 或参数引用进入正文；未认证内容另行标记。`claims.tex`、参考文献和结果表从记录派生，验证时重新生成与比对。这里的价值是让数字有机器可解析来源，而不是仅在最后对正文做相同数字搜索。

`verify_append_only` 检查每个 commit 与父节点之间的包含关系，并检查 HEAD 到工作树；修改已有值、移除记录、缩短列表等会被发现，允许明确的 verified 单向变化。它需要完整 Git 历史，浅克隆会导致所需历史核验失败。分支保护和发布 CI 属部署与模板边界，本次没有创建仓库或实际证明保护规则不可绕过。

## 8. 图怎么做

`render_chart` 接受 Vega-Lite spec，要求定量数据以 metric 引用而非自由字面数字进入；解析后本地渲染，图声明与输出共同记录，供后续重新渲染核验。该工具拒绝 PDF 图输出，因为其字节跨进程不稳定，使用 PNG 或 SVG。这是把数据来源约束直接放进绘图接口的具体实现。

`render_diagram` 则走 Kroki 的文本示意图通道，默认是公共服务，可配置自托管；它与定量结果图不同，不能套用同样的数值验证。图形字节一致不证明坐标、统计方法和叙述合理，概念图的内容也需人工检查。本文未调用任何渲染器，也未向外部图服务发送材料。

## 9. 和 RH 的相似点

两者在显式科研资产方面最接近：论文来源、声明、研究设计、实验运行、结果、图和稿件形成可追溯链，工具成功不应直接等同于研究通过。宿主技能与 MCP 原语分离，也支持已有代理完成推理、确定性代码承担约束。

双方还都面对同一个难点：字节和结构检查可以阻止一类篡改，却不能独自证明实验设计合理、模型评价无偏和科学结论新颖。因此过程完整性与科学有效性需要分别记录，不能混用“verified”一词。

## 10. 和 RH 的不同点

AIRAS 将实验 Git 仓库作为状态中心，依靠预注册记录、分支历史、外部运行存储和 CI 建立约束；RH 的公开接口则以主题、受管理文献池、证据关系、阶段状态和版本化研究产物为中心。两者可借鉴同一验证原则，但状态模型和运维依赖不同。

AIRAS 的预注册论文与数值引用方式更强地约束实验前后的叙述一致性；其适用性也依赖稳定的运行合同与评价后端。研究中需要更换设计或追加探索时，必须保留版本关系和说明，而不能把探索结果悄悄写回原有假设。

## 11. 优点 / 缺点

优点是声明、判据、run_id 与结果结构明确，写入和复核共用派生代码；文献全文和片段可核验；定量图有来源替换与重绘规则；结果判决和负结果可以由预定判据派生；MIT 许可和 MCP 接口便于集成。

局限是模板、评价器、平台存储与分支保护跨多个仓库，单仓库静态阅读不能验证整体强保证；部分 verifier 尚不完整；实验代码完整性和数据泄漏仍是作者承认的缺口；导入哈希与文件历史说明来源一致性，不直接证明测量或科学解释正确。

## 12. RH 可学的 1–3 条

1. 💬 **正文数值使用结构化引用。** 比对字符串存在更强的是 run、metric、参数和来源字段绑定，并共享派生与复核逻辑。
2. **定量图的数据入口强约束。** 先声明指标引用，再解析和渲染，将手填结果值排除出正常图表路径。
3. **历史核验按父边而非线性排序。** 分支和合并需要比较真实父子关系，才能可靠识别声明和结果是否被改写。

## 13. 名字速查表

| 名称 | 角色 |
|---|---|
| AIRAS | MCP 工具、宿主技能及验证 CLI |
| record.json | 研究声明、来源和结果的规范记录 |
| preregister_record | 创建记录与冻结提交 |
| register_sources | 固定论文或代码来源和原文片段 |
| dispatch_experiment | 选择后端并启动指定运行 |
| import_run_outputs | 导入运行结果与来源记录 |
| derive_results | 从结果文件派生记录与判决 |
| verify-record | 检查记录、历史及运行来源 |
| airasval | 论文中引用测量值或参数的命令 |
| render_chart | 以 metric 引用驱动的定量图工具 |

**固定提交证据入口**

- [README.md](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/README.md)
- [LICENSE](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/LICENSE)
- [backend/src/airas/mcp/tools/execution.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/mcp/tools/execution.py)
- [backend/src/airas/mcp/tools/record.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/mcp/tools/record.py)
- [backend/src/airas/mcp/tools/figures.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/mcp/tools/figures.py)
- [backend/src/airas/research_record/derive_results.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/research_record/derive_results.py)
- [backend/src/airas/research_record/verify.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/research_record/verify.py)
- [backend/src/airas/usecases/autonomous_research/workflows/experiment_cycle_graph.py](https://github.com/airas-org/airas/blob/72c4b5c83eb33a5b5709fa6fc9069f9b6425664f/backend/src/airas/usecases/autonomous_research/workflows/experiment_cycle_graph.py)

📌事实边界：本报告基于上述固定提交的 README、文档及关键源码实际查看，源码为所列文件的关键路径抽样；缓存字节经 Git blob 哈希核验，README 与公开固定 URL 对照一致。未安装项目依赖、启动服务或宿主代理、调用模型、执行实验或 GPU 任务、运行基准、编译论文、生成图像或发布内容。README、论文链接及示例中的性能数字均属作者报告，未做独立复现；RH 对比仅为公开职责与机制分析，不是性能或科学质量排名。
