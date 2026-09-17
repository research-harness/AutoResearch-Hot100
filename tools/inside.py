"""Inside Agentic Science: workflow chapters mapped onto published analyses."""
from __future__ import annotations

import html
from pathlib import Path

CHAPTERS = (
    {
        "slug": "birds-eye",
        "code": "I.1",
        "part": "I. 总览",
        "nav": "鸟瞰架构",
        "title": "鸟瞰：科研 Agent 在干什么",
        "insight": "编码 Agent 交付能跑的改动；科研 Agent 交付能被检查的研究记录。循环同类，产物不同。",
        "body": """
## 这一章回答什么

- 科研 Agent 和编码 Agent 共用什么循环。
- 产物为什么必须能被别人检查。
- 后面各章按哪六层拆。

## 先把名字说清楚

> 📘 **大语言模型（LLM）**：根据提示词生成文本或工具调用的模型。本文把它当成循环里的决策器，不讲训练。

> 📘 **工具调用（tool call）**：模型输出一个结构化请求，运行时去执行对应函数，再把结果写回上下文。

> 📘 **Agent 循环**：重复「读上下文 → 决定下一步 → 调工具或停」直到停机条件成立。

> 📘 **停机条件**：循环退出的判定。编码 Agent 常见条件是测试通过或用户接管。科研 Agent 还要看假设有没有被实验碰到、引用能不能指回文献、稿件有没有过检查点。

> 📘 **检查点**：阶段边界上必须留下的产物，用来续跑或给人审。例如检索到的论文列表、一次实验的指标文件、一版带图稿件。

## 运行逻辑

```mermaid
flowchart TD
  ctx[读上下文] --> decide[LLM 决定下一步]
  decide -->|调工具| tool[执行工具]
  tool --> write[结果写回上下文]
  write --> ctx
  decide -->|满足停机条件| stop[停止并交出产物]
```

*图 1：共用循环。科研 Agent 改的是停机条件和产物，不是循环形状。*

循环本身不区分领域。差别在三类对象：

- **上下文里有什么**：论文段落、实验日志、图文件路径，而不只是源代码。
- **工具是什么**：文献检索、代码执行、实验室仪器、写稿接口。
- **停下来交出什么**：可引用的证据、可复跑的实验记录、可检查的稿件。

## 六层怎么叠

从上到下记这六层。后面每章只讲一层或一段。

1. **宿主 / 技能 / CLI**：谁提供会话、权限和可安装步骤。见 II.2。
2. **循环 · 状态机 · 多角色**：谁记住「现在该检索还是该跑实验」。见 II.1。
3. **文献 → 假设 → 实验 → 写稿 → 审稿**：主工作链。见 III–V。
4. **领域执行器**：生物医学、化学、实验室把通用工具换成领域工具。见 VI。
5. **评测与基准**：把动作收成可打分任务。见 VII。
6. **证据 · commit · 产物**：分析绑定冻结 commit，不是默认分支。

```mermaid
flowchart TB
  host[宿主与技能]
  loop[循环与状态]
  chain[文献 假设 实验 写稿 审稿]
  domain[领域执行器]
  eval[评测]
  evid[证据与产物]
  host --> loop --> chain
  chain --> domain
  chain --> eval
  domain --> evid
  eval --> evid
```

*图 2：六层依赖。评测和领域执行器都要写回证据层。*

## 读开源时先看什么

- 入口：CLI、Web、工作流配置，谁启动第一轮循环。
- 状态写在哪：内存、文件、数据库。重启后能否续跑。
- 产物目录：论文、日志、图、PDF 是否分阶段落盘。

> 🔶 **推断**：仓库 README 写「端到端科研」时，仍可能只覆盖文献或只覆盖写稿。要以阶段对象和产物目录为准，不要以品牌名为准。
""",
        "projects": (
            "ai-scientist",
            "ai-scientist-v2",
            "paperclaw",
            "ulab-uiuc-tiny-scientist",
            "internagent",
            "zju-real-polaris",
            "aiming-lab-autoresearchclaw",
        ),
    },
    {
        "slug": "end-to-end",
        "code": "I.2",
        "part": "I. 总览",
        "nav": "端到端工作流",
        "title": "一次任务怎么从想法走到稿件",
        "insight": "把一次查询换成一次研究：文献、实验、图和 PDF 都要在阶段边界留下可续跑的产物。",
        "body": """
## 这一章回答什么

- 端到端系统把哪些阶段串起来。
- 阶段边界上必须留下什么，才能续跑。
- 人和自动分别挡在哪。

## 先把名字说清楚

> 📘 **阶段**：工作流里职责单一的一段，例如检索、实验、写稿。阶段有入口数据和出口产物。

> 📘 **阶段对象**：源码里表示「当前跑到哪一段」的数据结构。可能是枚举、图节点或目录名。

> 📘 **续跑**：中断后从最近检查点接着做，而不是从头再来。前提是该阶段产物已写盘。

> 📘 **人工检查点**：循环暂停、等人确认再继续。和自动停机不同：自动停机是条件满足就结束；人工检查点是条件满足也要等人。

## 运行逻辑

一次研究任务的常见阶段：

1. 入口：想法、数据文件或一篇种子论文。
2. 文献：检索、入库、选出要引用的段落。
3. 假设与实验：改代码或跑分析，写下指标。
4. 写稿与图：把主张和图对上。
5. 出口：PDF、实验日志，或两者都有。

```mermaid
flowchart LR
  idea[入口] --> lit[文献]
  lit --> exp[实验]
  exp --> write[写稿与图]
  write --> out[稿件与日志]
  lit -.->|检查点| human[人]
  exp -.->|检查点| human
  write -.->|检查点| human
  human -->|放行| lit
  human -->|放行| exp
  human -->|放行| write
```

*图 1：阶段串行。虚线是可选的人工检查点。*

## 三种边界

读仓库时用边界分类，不要用项目名分类。

- **每阶段写盘**：目录里能看到 `literature/`、`runs/`、`drafts/` 这类产物。失败可从该阶段重来。
- **人挡在检查点**：状态机有 `waiting_for_human` 一类取值。
- **一跑到底**：中间产物只在内存。失败通常从头再跑。

> 🔶 **推断**：如果只有最终 PDF、没有阶段目录，续跑成本会接近重跑。这不是价值判断，是恢复成本判断。

## 读开源时先看什么

- 阶段对象叫什么、有哪些取值。
- 每个阶段的入口文件和出口文件。
- 失败时重试的是工具调用，还是整个阶段。
""",
        "projects": (
            "idea2paper",
            "agentlaboratory",
            "technion-kishony-lab-data-to-paper",
            "astropilot-ai-denario",
            "researai-deepscientist",
            "evoscientist",
            "tsinghua-fib-lab-omniscientist",
        ),
    },
    {
        "slug": "agent-loop",
        "code": "II.1",
        "part": "II. 循环与编排",
        "nav": "循环与状态机",
        "title": "循环、状态机和多角色",
        "insight": "科研循环很少是单次 tool call。状态、记忆和角色把一次实验变成可恢复的长任务。",
        "body": """
## 这一章回答什么

- 一次 tool call 为什么不够跑完科研任务。
- 状态机、记忆、角色各管什么。
- 失败之后状态写在哪。

## 先把名字说清楚

> 📘 **状态机**：用有限个状态和转移规则描述「现在该做什么」。当前状态是一个离散值，例如 `retrieve`、`experiment`、`wait`、`stop`。

> 📘 **记忆**：跨轮保留的信息。短记忆在当前上下文窗口；长记忆写在文件、数据库或向量库。

> 📘 **角色**：同一循环里不同的提示词、工具集和停机条件。例如检索员、实验员、写作者、审稿人。角色不是把同一段提示词复制三份。

> 📘 **调度**：决定下一个角色或下一个状态。调度可以是固定顺序、模型选择，或图里的边。

> 📘 **LangGraph 节点**：把一步计算收成图上的一个节点，边表示下一步。这里只需要知道：节点 = 一步，边 = 转移。

## 运行逻辑

```mermaid
stateDiagram-v2
  [*] --> Retrieve
  Retrieve --> Experiment: 证据足够
  Retrieve --> Retrieve: 还要检索
  Experiment --> Write: 指标已记录
  Experiment --> Retrieve: 需要补文献
  Write --> Review
  Review --> Write: 未过检查点
  Review --> [*]: 停机
  Retrieve --> Wait: 等人
  Experiment --> Wait: 等人
  Wait --> Retrieve: 人放行
```

*图 1：科研任务的状态，不是单次函数调用。*

多角色时，每个角色看到的工具不同：

- 检索角色：搜索、阅读、入库。
- 实验角色：代码执行、指标读写。
- 写作角色：章节草稿、图文件。
- 审稿角色：对照检查点，通常少写、多判。

```mermaid
sequenceDiagram
  participant S as 调度
  participant R as 检索角色
  participant E as 实验角色
  participant W as 写作角色
  S->>R: 当前状态 retrieve
  R-->>S: 证据对象
  S->>E: 当前状态 experiment
  E-->>S: 指标与日志路径
  S->>W: 当前状态 write
  W-->>S: 章节与图
```

*图 2：调度按状态把工作交给不同角色。*

## 失败时看哪里

- 状态有没有写盘。只在内存里的状态，进程一停就丢。
- 记忆是追加还是覆盖。覆盖会丢掉失败原因。
- 角色切换有没有把上一个角色的产物当作下一个角色的输入。

> 🔶 **推断**：源码里出现 `Packet`、`TaskLog`、图节点或会话目录，通常是在给长任务留恢复点。没有这些名字，也可能用普通文件做同一件事。看的是「状态能否在重启后读回来」。
""",
        "projects": (
            "internagent",
            "camel-ai-camel",
            "bytedance-deer-flow",
            "skyworkai-deepresearchagent",
            "dualverse-ai-station",
            "airas-org-airas",
            "lamm-mit-sciagentsdiscovery",
        ),
    },
    {
        "slug": "skills-host",
        "code": "II.2",
        "part": "II. 循环与编排",
        "nav": "技能与宿主",
        "title": "技能、宿主和可安装科研步骤",
        "insight": "不少系统不自研循环，而是把科研步骤写成技能，挂到编码 Agent 宿主上。",
        "body": """
## 这一章回答什么

- 宿主和技能怎么分工。
- 技能包里通常有什么。
- 产物怎样交回工作区。

## 先把名字说清楚

> 📘 **宿主**：提供会话、权限、工具执行和文件系统的运行环境。例如命令行编码 Agent。它不知道「这篇论文该怎么引用」，只知道如何跑一条指令、读一个文件。

> 📘 **技能（skill）**：可发现、可安装的步骤说明，通常带一份指令文件和可选脚本。技能告诉宿主：遇到这类科研任务时按什么顺序调用哪些工具。

> 📘 **技能清单**：宿主启动时能枚举到的技能名和触发条件。没有清单，技能就不可发现。

> 📘 **工作区**：宿主读写的目录。技能的产物应写进工作区，而不是只留在模型上下文里。

> 📘 **权限**：宿主允许技能做的事，例如读网、跑命令、改文件。科研技能常需要检索和写盘。

## 运行逻辑

```mermaid
flowchart TD
  user[用户任务] --> host[宿主]
  host --> discover[发现技能]
  discover --> skill[选中的技能]
  skill --> steps[按指令逐步调工具]
  steps --> ws[写入工作区]
  ws --> host
```

*图 1：宿主负责运行，技能负责科研步骤顺序。*

技能包常见内容：

- 一段说明：何时启用、先做什么后做什么。
- 脚本或模板：检索、改 LaTeX、跑实验的固定动作。
- 产物约定：输出文件名、目录、是否需要人确认。

## 和自研循环的差别

- 自研循环：项目自己实现状态机和角色。
- 技能挂宿主：循环复用宿主，领域知识放在技能里。

> 🔶 **推断**：只含 Markdown 指令、不含脚本的技能，执行质量更依赖宿主当时的工具集。有脚本的技能把关键步骤从提示词里拿出来了。

## 读开源时先看什么

- 技能如何被发现：文件名约定、清单、注册表。
- 产物写到哪个相对路径。
- 有没有扫描或权限说明，避免技能任意跑命令。
""",
        "projects": (
            "academic-research-skills",
            "scientific-agent-skills",
            "wanshuiyin-auto-claude-code-research-in-sleep",
            "brycewang-stanford-auto-research-skills",
            "brycewang-stanford-auto-empirical-research-skills",
            "jmiao24-paper2agent",
            "ar9av-paperorchestra",
        ),
    },
    {
        "slug": "literature",
        "code": "III.1",
        "part": "III. 文献与证据",
        "nav": "检索、入库、引用",
        "title": "文献怎么来、证据怎么卡住引用",
        "insight": "没有入库和引用约束，长报告只是流畅的句子。科研 Agent 必须能指回论文段落。",
        "body": """
## 这一章回答什么

- 查询怎样变成可引用的证据。
- 入库、重排、生成各卡哪一步。
- 综述生成和问答共用哪条链。

## 先把名字说清楚

> 📘 **查询**：用户或上游阶段提出的问题。科研场景里常常太宽，需要拆成子问题。

> 📘 **子问题**：从原查询拆出的、可单独检索的更小问题。拆完才能并行搜。

> 📘 **摄取（ingest）**：把 PDF、HTML 或条目变成系统内部可检索的对象。通常包括切分、元数据和可选向量。

> 📘 **证据对象**：一段带定位信息的文本，至少能指回论文、章节或页码。不是「模型记得的一句话」。

> 📘 **重排（rerank）**：对初检结果再打分，把更可能回答子问题的段落提前。

> 📘 **引用约束**：生成阶段只能使用已检索到的证据对象；没有对象时应拒绝或标明缺失。

> 📘 **语料范围**：全网、开放学术索引，或私有 PDF 库。范围决定漏检和噪声。

## 运行逻辑

```mermaid
flowchart TD
  q[查询] --> split[拆子问题]
  split --> search[检索]
  search --> ingest[摄取为证据对象]
  ingest --> rerank[重排]
  rerank --> gen[带引用生成]
  gen -->|无来源| refuse[拒绝或标缺失]
  gen -->|有来源| ans[回答或综述]
```

*图 1：引用约束发生在生成之前。没有证据对象就不能当事实写。*

三个接口决定这条链是否可检查：

1. **查询如何拆**：有没有子问题列表落盘。
2. **证据如何定位**：字段里是否有 paper id、段落、页码。
3. **生成能否拒绝**：无来源句子是被挡下，还是照样写出来。

综述生成是同一条链的长文模式：提纲 → 各节检索 → 各节带引用写 → 全篇合并。

```mermaid
sequenceDiagram
  participant Q as 查询
  participant I as 入库
  participant G as 生成
  Q->>I: 子问题
  I-->>G: 证据对象列表
  G->>G: 逐句对齐来源
  alt 某句无来源
    G-->>Q: 拒绝或标缺失
  else 均有来源
    G-->>Q: 带引用文本
  end
```

*图 2：生成阶段对无来源句子的处理，是文献链和普通聊天的分界。*

> 🔶 **推断**：只在提示词里写「请引用」，没有证据对象字段，引用约束通常不可检查。要以数据结构为准。
""",
        "projects": (
            "paper-qa",
            "openscholar",
            "gpt-researcher",
            "open-deep-research",
            "storm",
            "bytedance-pasa",
            "zilliztech-deep-searcher",
            "autosurveys-autosurvey",
            "jinheonbaek-researchagent",
        ),
    },
    {
        "slug": "experiment",
        "code": "IV.1",
        "part": "IV. 方法与实验",
        "nav": "假设与实验循环",
        "title": "假设、代码执行和下一次改什么",
        "insight": "方法发现把实验当成可迭代对象：指标、日志、补丁，下一次循环吃上一次的失败。",
        "body": """
## 这一章回答什么

- 内环和外环各改什么。
- 沙箱、预算、轨迹为什么必须留下。
- 下一次修改的输入从哪来。

## 先把名字说清楚

> 📘 **假设**：本轮想验证的命题，例如「换这个模块会提高某指标」。假设要能被一次实验碰到。

> 📘 **内环**：固定假设下的「改代码 → 跑 → 看指标」。对象是补丁和一次 run。

> 📘 **外环**：根据内环结果换假设、换搜索方向。对象是假设集合或搜索树。

> 📘 **执行沙箱**：跑代码的隔离环境。限制文件系统、网络和时长，避免一次失败实验毁掉工作区。

> 📘 **预算**：允许消耗的步数、时间和调用次数。预算用尽是停机条件之一。

> 📘 **轨迹**：按时间记下的动作和结果，包括补丁、命令、指标、报错。没有轨迹，搜索不可复盘。

> 📘 **指标文件**：一次 run 写出的数值结果，供外环比较。应和代码版本一起保存。

## 运行逻辑

```mermaid
flowchart TD
  h[当前假设] --> patch[生成补丁]
  patch --> run[沙箱执行]
  run --> log[写轨迹与指标]
  log --> budget{预算还够?}
  budget -->|够且未达标| patch
  budget -->|够且要换假设| h
  budget -->|用尽或达标| stop[停止]
```

*图 1：内环改代码，外环换假设。两者都读轨迹。*

常见形态：

- 绑在单一训练或分析脚本上，搜索超参或代码片段。
- 把机器学习工程拆成竞赛式任务，每次提交一份解答。
- 树搜索或演化：每个节点是一版代码，边是一次修改。

## 读开源时先看什么

- 沙箱边界：能读哪些目录、能不能上网。
- 预算字段：步数、墙钟、模型调用。
- 轨迹目录：失败 run 是否保留。
- 指标和下一次补丁是否同源，避免只留下最后一次成功。

> 🔶 **推断**：只有最终分数、没有中间轨迹的仓库，外环搜索无法被第三方复盘。分数本身不能代替轨迹。
""",
        "projects": (
            "rd-agent",
            "aideml",
            "autoresearch",
            "algorithmicsuperintelligence-openevolve",
            "gair-nlp-asi-arch",
            "mshumer-autonomous-researcher",
            "facebookresearch-mlgym",
            "internagent",
        ),
    },
    {
        "slug": "writing",
        "code": "V.1",
        "part": "V. 写稿与审稿",
        "nav": "写稿、图、审稿",
        "title": "稿件、图和审稿角色",
        "insight": "写稿要把主张、图和实验记录对齐。审稿角色检查稿件有没有漏掉检查点。",
        "body": """
## 这一章回答什么

- 写稿层吃哪些上游产物。
- 图和主张如何对齐。
- 审稿角色判什么，不负责写什么。

## 先把名字说清楚

> 📘 **主张**：稿件中可被检查的命题，例如「方法 A 在数据集 B 上指标 C 更高」。主张必须能指回实验记录或文献证据。

> 📘 **图文件**：由数据或结构说明生成的图像。科研稿里图要承担主张，而不是装饰。

> 📘 **同源**：图中的数字、方法描述和日志来自同一次实验记录。不同源就会出现图和正文对不上。

> 📘 **审稿角色**：读取稿件和检查点，输出问题列表。它应少改句子、多指出缺口。

> 📘 **检查点覆盖**：主张、图、引用、实验设置是否都在稿里出现，并且能指回产物。

## 运行逻辑

```mermaid
flowchart LR
  rec[实验记录] --> claim[主张列表]
  rec --> fig[图]
  lit[文献证据] --> claim
  claim --> draft[章节草稿]
  fig --> draft
  draft --> review[审稿角色]
  review -->|未覆盖| draft
  review -->|通过| ms[可检查稿件]
```

*图 1：写稿吃记录和证据；审稿只检查覆盖，不另起主张。*

这一层常见实现：

- 写作技能：按章节模板填主张和引用。
- 编辑器旁路助手：在已有稿上提修改。
- 架构示意图生成：方法图，不负责数值图。
- 多角色审稿：方法、实验、引用分开判。
- 审稿数据集：把「问题是否被指出」收成评测，而不是在线改稿。

## 图这一层单独记

- **数值图**：必须来自指标文件。
- **方法图**：来自模块关系，不冒充实验结果。
- **审稿**应能问：这张图支持哪条主张。

> 🔶 **推断**：生成图的提示词如果只写「画一张架构图」，没有绑定模块名单或指标文件，图和正文很容易分叉。要对齐，先有主张列表和数据源字段。
""",
        "projects": (
            "paperdebugger-paperdebugger",
            "paperbanana",
            "academic-research-skills",
            "ahren09-agentreview",
            "maxidl-openreviewer",
            "allenai-aries",
            "tu2021-paperaudit",
        ),
    },
    {
        "slug": "bio-med",
        "code": "VI.1",
        "part": "VI. 领域执行器",
        "nav": "生物医学",
        "title": "生物医学里的工具换成了什么",
        "insight": "循环还在，工具变成 assay、影像、知识库和实验室会议。领域约束写进工具，而不是写进形容词。",
        "body": """
## 这一章回答什么

- 通用循环接到生物医学时，工具清单换成什么。
- 任务怎样翻译成工具序列。
- 评测集卡住的是发现还是文风。

## 先把名字说清楚

> 📘 **领域执行器**：把通用「调工具」换成该领域可执行动作的一层。循环和状态机可以复用；工具不能复用。

> 📘 **assay**：一次可记录的实验测定，例如筛选、测序分析。在系统里它应是可调用的工具或工作流步骤，而不是一段描述。

> 📘 **知识库工具**：查询结构化生物医学条目（靶点、药物、通路），返回带标识符的记录，而不是自由文本。

> 📘 **虚拟实验室会议**：多角色按议程讨论实验设计，会议记录就是状态。人可以是其中一个角色。

> 📘 **任务翻译**：把自然语言目标变成工具序列，例如「找与表型相关的基因」→ 检索数据集 → 跑筛选 → 写候选列表。

## 运行逻辑

通用科研 Agent 的工具常常是搜索和代码解释器。生物医学系统常见工具是：

- 基因或单细胞筛选。
- 医学影像读取。
- 治疗或文献知识库。
- 实验室会议与实验设计记录。

```mermaid
flowchart TD
  goal[自然语言目标] --> trans[任务翻译]
  trans --> tools[领域工具序列]
  tools --> rec[测定或查询记录]
  rec --> state[会议记录或状态]
  state --> out[候选与证据]
```

*图 1：领域约束在工具和记录里，不在形容词里。*

人还在环里时：

- 会议记录保存「为什么选这个实验」。
- 下一步工具调用应引用该记录，而不是只引用最新聊天句。

## 评测卡住什么

单细胞发现一类基准问的是：系统有没有给出可检查的发现对象。不问句子像不像论文。

> 🔶 **推断**：工具清单短、提示词很长的仓库，领域约束多半还在文本里，执行时容易绕过。先数可调用工具，再读提示词。
""",
        "projects": (
            "snap-stanford-biomni",
            "snap-stanford-biodiscoveryagent",
            "zou-group-virtual-lab",
            "future-house-robin",
            "mims-harvard-txagent",
            "bowang-lab-medrax",
            "mlbio-epfl-heurekabench",
        ),
    },
    {
        "slug": "chem-lab",
        "code": "VI.2",
        "part": "VI. 领域执行器",
        "nav": "化学与实验室",
        "title": "化学、材料与实验室编排",
        "insight": "湿实验和计算化学把调度、设备和安全检查变成一等对象。实验室步骤有设备状态，不能只靠对话历史。",
        "body": """
## 这一章回答什么

- 计算化学工具和湿实验设备各是什么对象。
- 自然语言任务怎样落到仪器或计算后端。
- 失败之后数据目录是否还在。

## 先把名字说清楚

> 📘 **计算化学后端**：分子性质、反应或材料结构的计算程序。Agent 调用它时，输入是结构或参数，输出是数值或结构文件。

> 📘 **湿实验**：在真实仪器上处理样品。步骤受设备状态、试剂和安全检查约束。

> 📘 **设备对象**：源码里表示一台仪器的数据结构，含状态（空闲、运行、故障）和可执行动作。

> 📘 **实验目录**：一次实验的输入、输出、日志存放处。失败后仍应能打开。

> 📘 **安全检查**：执行前对动作合法性的判定，例如体积、温度、不相容试剂。通过才发给设备。

> 📘 **编排**：按依赖顺序调度计算步骤或仪器动作。它是状态机，不是聊天轮次。

## 运行逻辑

这一段覆盖三类实现：

- 分子或材料工具箱：把化学软件收成可调用工具。
- 原子或晶体模拟：计算后端为主，设备对象可缺省。
- 实验室编排：设备、实验目录、安全检查都是一等对象。后一类可以几乎不依赖 LLM。

```mermaid
flowchart TD
  task[自然语言或工作流任务] --> plan[编排]
  plan --> safety{安全检查}
  safety -->|拒绝| stop[记录原因并停]
  safety -->|通过| exec[计算后端或设备]
  exec --> catalog[写入实验目录]
  catalog --> plan
```

*图 1：发给设备之前先过安全检查；结果写入实验目录。*

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Running: 动作被接受
  Running --> Idle: 成功写目录
  Running --> Fault: 失败
  Fault --> Idle: 人工或自动复位
```

*图 2：设备状态。对话历史不能代替这个状态。*

## 读开源时先看什么

- 任务如何映射到具体仪器或后端名称。
- 安全检查是独立步骤，还是写在提示词里。
- 失败 run 的目录是否保留原始输入。

> 🔶 **推断**：没有设备状态字段的「实验室 Agent」，更可能是文档生成器，而不是编排器。要以状态和目录为准。
""",
        "projects": (
            "ur-whitelab-chemcrow-public",
            "argonne-lcf-chemgraph",
            "ad-sdl-madsci",
            "pylabrobot-pylabrobot",
            "malcolmsimgithub-chemos2-0",
            "lamm-mit-atomagents",
            "fung-lab-llmatdesign",
        ),
    },
    {
        "slug": "evaluation",
        "code": "VII.1",
        "part": "VII. 评测",
        "nav": "基准与审计",
        "title": "把科研动作变成可打分任务",
        "insight": "评测层不问品牌故事，只问任务、环境和分数是否可重放。",
        "body": """
## 这一章回答什么

- 科研动作怎样收成任务。
- 环境、提交、分数各是什么。
- 没有评测层时工作流停在哪。

## 先把名字说清楚

> 📘 **任务**：有准备步骤、提交物和评分规则的一道题。例如复现某论文的一个实验、完成一道科学编程题。

> 📘 **环境**：跑任务的隔离运行时，常见为容器或虚拟机。环境要能被别人用同一镜像再起一次。

> 📘 **提交**：系统交出来打分的对象，例如代码、答案文件、轨迹。

> 📘 **分数**：由评分器按规则算出的数或等级。规则必须能在相同提交上重放。

> 📘 **已知答案**：评分器持有、对受试系统隐藏的正确答案或检查脚本。

> 📘 **可重放**：同一提交、同一环境、同一评分器，得到同一分数。不可重放的分数不能当基准。

## 运行逻辑

```mermaid
sequenceDiagram
  participant T as 任务
  participant E as 环境
  participant A as 受试系统
  participant S as 评分器
  T->>E: 准备数据与限制
  E->>A: 可见输入
  A->>E: 提交
  E->>S: 提交 + 已知答案
  S-->>T: 分数
```

*图 1：分数来自评分器，不来自受试系统的自述。*

基准常见切法：

- 论文复现：提交能否再现报告指标。
- 科学编程：代码是否通过测试。
- 假设发现：输出的对象能否被检查脚本认出。
- 端到端研究：多阶段产物是否齐全。
- 审稿可靠性：问题列表是否打中标注。

## 读开源时先看什么

- 任务如何安装到环境。
- 提交格式和评分入口。
- 分数是否绑定任务版本，避免题面改了分数还在。

> 📌 **事实边界**：本章只说明评测对象怎么切。各仓库在冻结 commit 上的具体分数，以对应 13 节分析为准，不在这里汇总。

> 🔶 **推断**：只有演示脚本、没有评分器的项目，不能当成基准。演示证明能跑，基准证明能打分。
""",
        "projects": (
            "openai-frontier-evals",
            "openai-mle-bench",
            "osu-nlp-group-scienceagentbench",
            "internscience-researchclawbench",
            "facebookresearch-airs-bench",
            "anikethh-researchgym",
            "tu2021-paperaudit",
        ),
    },
    {
        "slug": "tool-layer",
        "code": "VIII.1",
        "part": "VIII. 工具层",
        "nav": "可发现的科学工具",
        "title": "工具层、检索和领域底座",
        "insight": "有的项目不扮演科学家，只把数据库、模型和软件收成可发现、可调用的工具。",
        "body": """
## 这一章回答什么

- 工具层给前面各章提供什么。
- 注册、检索、调用三个协议各管什么。
- 为什么工具层自己不必跑完整条科研链。

## 先把名字说清楚

> 📘 **工具注册**：把一个可调用对象写进目录，至少包括名字、参数说明、返回说明。没有注册，循环找不到它。

> 📘 **工具检索**：按当前任务从目录里选出若干工具。可以用关键词、向量或图结构。

> 📘 **调用协议**：一次调用的请求和响应格式。循环只依赖协议，不依赖工具内部实现。

> 📘 **领域底座**：某一领域里稳定的数据或模型服务，例如量化研究数据、材料数据库。底座可以被很多 Agent 共用。

> 📘 **系统提示**：写给模型的固定说明。把全部领域知识塞进系统提示，工具就不可发现、也不可单独更新。

## 运行逻辑

```mermaid
flowchart LR
  task[当前任务] --> search[工具检索]
  reg[注册目录] --> search
  search --> call[按协议调用]
  call --> result[结构化结果]
  result --> loop[交回 Agent 循环]
```

*图 1：循环通过检索找到工具，通过协议调用，不把领域知识写进系统提示。*

工具层常见形态：

- 科学工具图谱：节点是工具，边是可组合关系。
- 数据库问答：自然语言到查询，返回带标识符的记录。
- 领域底座：量化、材料、数据清洗等，供上游 Agent 当手用。

它通常不负责：

- 文献引用约束。
- 实验预算和轨迹。
- 稿件主张对齐。

那些仍由 III–V 的循环处理。工具层只保证「手找得到、调得动」。

## 读开源时先看什么

- 新工具如何注册，要不要改循环代码。
- 检索失败时循环是否得到空列表，而不是一段散文。
- 返回值有没有稳定字段，供下游当证据或指标用。

> 🔶 **推断**：只有包装脚本、没有检索接口的工具集，规模一大就会变成「把名字写进提示词」。先看有没有目录和检索。
""",
        "projects": (
            "mims-harvard-tooluniverse",
            "hicai-zju-scitoolagent",
            "osu-nlp-group-chemtoolagent",
            "microsoft-qlib",
            "sjtu-sai-agents-datamaster",
            "k-dense-ai-agentic-data-scientist",
        ),
    },
)


def part_anchor(part: str) -> str:
    return "part-" + part.split(".", 1)[0].strip().lower()


def series_tables() -> str:
    blocks: list[str] = []
    current_part = None
    rows: list[str] = []
    header = "<thead><tr><th>Part</th><th>Title</th><th>Core Insight</th></tr></thead>"
    for chapter in CHAPTERS:
        if chapter["part"] != current_part:
            if rows:
                blocks.append(
                    f'<div class="book" id="{html.escape(part_anchor(current_part))}">'
                    f"<h2>{html.escape(current_part)}</h2>"
                    f"<table>{header}<tbody>{''.join(rows)}</tbody></table></div>"
                )
                rows = []
            current_part = chapter["part"]
        rows.append(
            f'<tr><td class="num">{html.escape(chapter["code"])}</td>'
            f'<td><a href="{html.escape(chapter["slug"])}/">{html.escape(chapter["title"])}</a></td>'
            f"<td>{html.escape(chapter['insight'])}</td></tr>"
        )
    if rows:
        blocks.append(
            f'<div class="book" id="{html.escape(part_anchor(current_part))}">'
            f"<h2>{html.escape(current_part)}</h2>"
            f"<table>{header}<tbody>{''.join(rows)}</tbody></table></div>"
        )
    return "\n".join(blocks)


def series_nav(active: str, *, root: bool = False) -> str:
    prefix = "" if root else "../"
    blocks: list[str] = []
    current_part = None
    items: list[str] = []
    for chapter in CHAPTERS:
        if chapter["part"] != current_part:
            if items:
                blocks.append(f"<h3>{html.escape(current_part)}</h3><ul>{''.join(items)}</ul>")
                items = []
            current_part = chapter["part"]
        cls = ' class="active"' if chapter["slug"] == active else ""
        items.append(
            f'<li><a{cls} href="{prefix}{html.escape(chapter["slug"])}/">{html.escape(chapter["code"])} {html.escape(chapter["nav"])}</a></li>'
        )
    if items:
        blocks.append(f"<h3>{html.escape(current_part)}</h3><ul>{''.join(items)}</ul>")
    return "\n".join(blocks)


def index_page_toc() -> str:
    items = ['<li><a href="#how">怎么读</a></li>']
    seen: list[str] = []
    for chapter in CHAPTERS:
        if chapter["part"] in seen:
            continue
        seen.append(chapter["part"])
        items.append(
            f'<li><a href="#{html.escape(part_anchor(chapter["part"]))}">{html.escape(chapter["part"])}</a></li>'
        )
    return "<ul>" + "".join(items) + "</ul>"


def project_table(chapter: dict, by_slug: dict[str, dict]) -> str:
    rows = ["<table><thead><tr><th>项目</th><th>在这一段做什么</th><th>分析</th><th>源码快照</th></tr></thead><tbody>"]
    for slug in chapter["projects"]:
        project = by_slug[slug]
        commit = project["analyzed_commit"]
        tree = f"https://github.com/{project['repo']}/tree/{commit}"
        short = commit[:7]
        rows.append(
            "<tr>"
            f"<td>{html.escape(project['name'])}</td>"
            f"<td>{html.escape(project['tagline'])}</td>"
            f'<td><a href="../../products/{html.escape(slug)}/">13 节分析</a></td>'
            f'<td><a href="{html.escape(tree)}"><code>{html.escape(project["repo"])}@{short}</code></a></td>'
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "".join(rows)


def pager(index: int) -> str:
    prev_html = "<span></span>"
    next_html = "<span></span>"
    if index > 0:
        prev = CHAPTERS[index - 1]
        prev_html = f'<a href="../{html.escape(prev["slug"])}/">← {html.escape(prev["code"])} {html.escape(prev["nav"])}</a>'
    if index + 1 < len(CHAPTERS):
        nxt = CHAPTERS[index + 1]
        next_html = f'<a href="../{html.escape(nxt["slug"])}/">{html.escape(nxt["code"])} {html.escape(nxt["nav"])} →</a>'
    return prev_html + next_html


def render_inside(
    dist: Path,
    template_index: Path,
    template_chapter: Path,
    base_url: str,
    projects: list[dict],
    markdown_to_body,
    build_toc,
) -> None:
    by_slug = {project["slug"]: project for project in projects}
    missing = sorted({slug for chapter in CHAPTERS for slug in chapter["projects"] if slug not in by_slug})
    if missing:
        raise SystemExit(f"inside chapters reference unknown slugs: {missing}")
    dest = dist / "inside"
    dest.mkdir(parents=True)
    snapshot = max(project["snapshot_date"] for project in projects)
    index = (
        template_index.read_text(encoding="utf-8")
        .replace("{{SNAPSHOT}}", snapshot)
        .replace("{{SERIES}}", series_tables())
        .replace("{{SERIES_NAV}}", series_nav("", root=True))
        .replace("{{PAGE_TOC}}", index_page_toc())
    )
    (dest / "index.html").write_text(index, encoding="utf-8")
    chapter_template = template_chapter.read_text(encoding="utf-8")
    for number, chapter in enumerate(CHAPTERS):
        _, body, toc = markdown_to_body(chapter["body"])
        toc.append((2, "impl", "开源实现怎么接到这一段"))
        page = chapter_template
        for key, value in {
            "{{TITLE}}": html.escape(f'{chapter["code"]} {chapter["title"]}｜Inside Agentic Science'),
            "{{DESCRIPTION}}": html.escape(chapter["insight"], quote=True),
            "{{CANONICAL}}": f'{base_url}/inside/{chapter["slug"]}/',
            "{{SERIES_NAV}}": series_nav(chapter["slug"]),
            "{{PAGE_TOC}}": build_toc(toc),
            "{{CODE}}": html.escape(f'{chapter["part"]} · {chapter["code"]}'),
            "{{HEADING}}": html.escape(chapter["title"]),
            "{{INSIGHT}}": html.escape(chapter["insight"]),
            "{{BODY}}": body,
            "{{PROJECTS}}": project_table(chapter, by_slug),
            "{{PAGER}}": pager(number),
            "{{MERMAID}}": "../../assets/mermaid.min.js",
        }.items():
            page = page.replace(key, value)
        folder = dest / chapter["slug"]
        folder.mkdir()
        (folder / "index.html").write_text(page, encoding="utf-8")
