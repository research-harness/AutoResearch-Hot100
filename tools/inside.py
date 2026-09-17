"""Inside Agentic Science: mechanism chapters mapped onto published analyses."""
from __future__ import annotations

import html
from pathlib import Path

CHAPTERS = (
    {
        "slug": "birds-eye",
        "code": "I.1",
        "part": "I. 总览",
        "nav": "鸟瞰架构",
        "title": "鸟瞰：共用循环，不同产物",
        "insight": "编码 Agent 和科研 Agent 共用「读上下文 → 调工具 → 写回」循环。差别在停机条件和必须留下的记录。",
        "body": """
## 这一章只讲一个判断

- 循环形状相同。
- 停机条件和产物不同。
- 后面各章按运行对象切开，不按仓库品类切开。

## 先把名字说清楚

> 📘 **大语言模型（LLM）**：根据提示词生成文本或工具调用的模型。这里只当循环里的决策器。

> 📘 **工具调用**：模型输出结构化请求，运行时执行对应函数，把结果写回上下文。

> 📘 **Agent 循环**：重复「读上下文 → 决定下一步 → 调工具或停」直到停机条件成立。

> 📘 **停机条件**：循环退出的判定。编码侧常见是测试通过或用户接管。科研侧还要看假设有没有被实验碰到、引用能不能指回文献、稿件有没有过检查点。

> 📘 **检查点**：阶段边界上必须留下的产物，用来续跑或给人审。

## 运行逻辑

```mermaid
flowchart TD
  ctx[读上下文] --> decide[LLM 决定下一步]
  decide -->|调工具| tool[执行工具]
  tool --> write[结果写回上下文]
  write --> ctx
  decide -->|满足停机条件| stop[停止并交出产物]
```

*图 1：共用循环。科研 Agent 改的是停机条件和产物。*

差别落在三类对象：

- **上下文**：论文段落、实验日志、图路径，而不只是源代码。
- **工具**：文献检索、代码执行、仪器、写稿接口。
- **产物**：可引用证据、可复跑记录、可检查稿件。

## 后面按什么切

不是「生物一组、化学一组」。一章一个对象：

- 状态机、角色、内环 / 外环
- 子问题、证据对象、引用约束
- 沙箱、轨迹、搜索树
- 主张对齐、审稿角色
- 技能、工具注册
- 领域工具、设备状态
- 任务 / 环境 / 分数

> 🔶 **推断**：README 写「端到端科研」时，仍可能只覆盖文献或只覆盖写稿。要以阶段对象和产物目录为准。
""",
        "projects": (
            ("ai-scientist", "idea→experiment→LaTeX 脚本链"),
            ("internagent", "WorkflowState"),
            ("paperclaw", "domain / idea / research CLI"),
        ),
    },
    {
        "slug": "stage-object",
        "code": "I.2",
        "part": "I. 总览",
        "nav": "阶段对象",
        "title": "阶段对象：一次研究停在哪、留下什么",
        "insight": "端到端不是品牌。先找到表示「当前跑到哪一段」的对象，再看该段有没有写盘。",
        "body": """
## 这一章只讲一个对象

阶段对象：源码里表示当前职责段的数据结构。没有它，所谓流水线只是一次长提示。

## 先把名字说清楚

> 📘 **阶段**：职责单一的一段，有入口数据和出口产物。例如检索、实验、写稿。

> 📘 **阶段对象**：枚举、图节点、目录名或 CLI 子命令，用来记住「现在在哪一段」。

> 📘 **续跑**：从最近检查点接着做。前提是该阶段产物已写盘。

> 📘 **人工检查点**：条件满足也要等人。和自动停机不同。

## 运行逻辑

```mermaid
flowchart LR
  idea[入口] --> lit[文献]
  lit --> exp[实验]
  exp --> write[写稿]
  write --> out[稿件与日志]
  lit -.-> ck[检查点写盘]
  exp -.-> ck
  write -.-> ck
```

*图 1：箭头是阶段转移。虚线是必须留下的产物。*

三种边界：

- **每阶段写盘**：能看到分阶段目录或固定文件名。
- **人挡在检查点**：状态机有等待人的取值。
- **一跑到底**：中间产物只在内存。失败接近重跑。

## 读源码时先找什么

- 阶段对象叫什么、有哪些取值。
- 每个取值的入口文件和出口文件。
- 失败时重试的是工具调用，还是整个阶段。

> 🔶 **推断**：只有最终 PDF、没有阶段目录，续跑成本接近重跑。这是恢复成本，不是价值判断。
""",
        "projects": (
            ("idea2paper", "Story"),
            ("paperclaw", "DOMAIN.md / IDEA.md"),
            ("academic-research-skills", "academic-pipeline 阶段派发"),
            ("agentlaboratory", "lit→plan→exp→paper 角色阶段"),
        ),
    },
    {
        "slug": "state-machine",
        "code": "II.1",
        "part": "II. 循环与状态",
        "nav": "状态机",
        "title": "状态机：当前该检索、该跑，还是该停",
        "insight": "长任务靠离散状态，不靠「再生成一次」。重启后状态读不回来，就不是可续跑。",
        "body": """
## 这一章只讲一个对象

状态机：有限个状态和转移规则。当前状态是一个离散值。

## 先把名字说清楚

> 📘 **状态**：当前允许做的那一类动作，例如 `retrieve`、`experiment`、`wait`、`stop`。

> 📘 **转移**：满足条件后改写当前状态。条件可以是「证据够了」或「人放行」。

> 📘 **写盘**：把当前状态写到文件、checkpoint 或数据库。只在内存里的状态，进程一停就丢。

> 📘 **LangGraph checkpoint**：把图执行位置和通道值存下来，用来恢复。这里只需知道：它是状态的持久化，不是聊天记录。

## 运行逻辑

```mermaid
stateDiagram-v2
  [*] --> Retrieve
  Retrieve --> Experiment: 证据足够
  Retrieve --> Retrieve: 还要检索
  Experiment --> Write: 指标已记录
  Write --> Review
  Review --> Write: 未过检查点
  Review --> [*]: 停机
  Retrieve --> Wait: 等人
  Wait --> Retrieve: 人放行
```

*图 1：科研任务的状态。单次 tool call 覆盖不了这些转移。*

## 失败时看哪里

- 状态有没有写盘。
- 非法转移是被拒绝，还是靠提示词「请不要跳阶段」。
- `wait` 一类状态有没有对应的人接口。

> 🔶 **推断**：出现 `WorkflowState`、`Packet`、`TaskLog` 或 checkpoint 目录，通常是在给长任务留恢复点。没有这些名字，普通文件也能做同一件事。看的是重启后能否读回来。
""",
        "projects": (
            ("internagent", "WorkflowState"),
            ("bytedance-deer-flow", "LangGraph checkpoint"),
            ("open-deep-research", "deep_researcher 图节点"),
        ),
    },
    {
        "slug": "roles",
        "code": "II.2",
        "part": "II. 循环与状态",
        "nav": "角色与调度",
        "title": "角色：不同工具集，不是同一段提示词复制三份",
        "insight": "角色是提示词、工具和停机条件的捆绑。调度决定下一个角色看到什么输入。",
        "body": """
## 这一章只讲一个对象

角色：循环里一组绑定在一起的提示词、工具集和停机条件。

## 先把名字说清楚

> 📘 **角色**：检索员、实验员、写作者、审稿人可以是四个角色。各自能调的工具不同。

> 📘 **调度**：决定下一个角色或下一个状态。可以是固定顺序、模型选择，或图上的边。

> 📘 **输入交接**：上一个角色的产物，必须成为下一个角色的输入对象，而不是再讲一遍故事。

## 运行逻辑

```mermaid
sequenceDiagram
  participant S as 调度
  participant R as 检索角色
  participant E as 实验角色
  participant W as 写作角色
  S->>R: 状态 retrieve
  R-->>S: 证据对象
  S->>E: 状态 experiment
  E-->>S: 指标与日志路径
  S->>W: 状态 write
  W-->>S: 章节与图
```

*图 1：调度按状态把工作交给不同角色。*

不是角色的做法：

- 同一段系统提示里写「你既是科学家又是审稿人」。
- 三个名字，工具清单却完全一样。

## 读源码时先找什么

- 角色是类、配置还是提示词文件。
- 每个角色的工具列表是否真的不同。
- 调度失败时，状态停在谁身上。

> 🔶 **推断**：实验室头衔当角色名（PhD、教授）只说明人设。要看工具列表和可见消息，才能判断是不是真切分。
""",
        "projects": (
            ("agentlaboratory", "PhDStudentAgent / ReviewersAgent"),
            ("camel-ai-camel", "Workforce + TaskChannel"),
            ("ahren09-agentreview", "Reviewer / Author / Area Chair"),
        ),
    },
    {
        "slug": "inner-outer",
        "code": "II.3",
        "part": "II. 循环与状态",
        "nav": "内环与外环",
        "title": "内环改代码，外环换假设",
        "insight": "方法发现有两层循环。混成一层，就分不清「这次该修 bug」还是「该换命题」。",
        "body": """
## 这一章只讲一对对象

内环和外环。内环固定假设；外环根据内环结果换假设。

## 先把名字说清楚

> 📘 **假设**：本轮想验证的命题，要能被一次实验碰到。

> 📘 **内环**：固定假设下「改代码 → 跑 → 看指标」。对象是补丁和一次 run。

> 📘 **外环**：换假设、换搜索方向。对象是假设集合或搜索树。

> 📘 **反馈**：内环写给外环的指标、报错、轨迹路径。没有反馈，外环只能随机换。

## 运行逻辑

```mermaid
flowchart TD
  h[当前假设] --> patch[生成补丁]
  patch --> run[执行]
  run --> fb[写反馈]
  fb --> inner{内环还继续?}
  inner -->|修代码| patch
  inner -->|换假设| h
  inner -->|停| stop[停止]
```

*图 1：内环吃报错，外环吃假设级结果。*

常见切法：

- Research 角色提假设，Development 角色落地代码。
- 想法生成 → 实验后端；实验后端可替换。
- 树节点动作分成 draft / debug / improve。

> 🔶 **推断**：只有一条「再试一次」循环、没有假设对象，外环通常不存在。那是在调参，不是在换科学命题。
""",
        "projects": (
            ("rd-agent", "Research / Development"),
            ("internagent", "IdeaGenerator → ExperimentRunner"),
            ("aideml", "draft / debug / improve"),
        ),
    },
    {
        "slug": "query-split",
        "code": "III.1",
        "part": "III. 文献与证据",
        "nav": "子问题",
        "title": "查询怎么拆成可检索的子问题",
        "insight": "科研问题通常太宽。不拆子问题，检索只能碰运气，后面也无法并行。",
        "body": """
## 这一章只讲一个对象

子问题：从原查询拆出的、可单独检索的更小问题。

## 先把名字说清楚

> 📘 **查询**：用户或上游阶段提出的问题。

> 📘 **子问题**：可单独交给检索器的更小问题。拆完才能并行搜。

> 📘 **研究 brief**：给下游检索角色的完整、独立任务说明。它是子问题的一种落盘形式。

> 📘 **监督者**：只负责拆题和收束，自己可以不抓网页。

## 运行逻辑

```mermaid
flowchart TD
  q[原查询] --> split[拆子问题]
  split --> a[子问题 A]
  split --> b[子问题 B]
  a --> searchA[检索]
  b --> searchB[检索]
  searchA --> merge[合并]
  searchB --> merge
```

*图 1：拆开是为了可检索、可并行，不是为了把句子写长。*

## 读源码时先找什么

- 子问题列表有没有写成对象或文件。
- 谁有权结束检索（例如 `ResearchComplete`）。
- 拆题角色能不能直接写最终报告。若能，拆题和写作已经混在一起。

> 🔶 **推断**：提示词里写「请分点检索」，但没有任何子问题字段，拆题通常不可检查。
""",
        "projects": (
            ("open-deep-research", "ConductResearch / research brief"),
            ("gpt-researcher", "规划查询"),
            ("storm", "多视角提问"),
        ),
    },
    {
        "slug": "evidence-object",
        "code": "III.2",
        "part": "III. 文献与证据",
        "nav": "证据对象",
        "title": "证据对象：能指回论文段落的那一块",
        "insight": "入库之后必须得到带定位信息的对象。模型「记得的一句话」不是证据。",
        "body": """
## 这一章只讲一个对象

证据对象：一段带定位信息的文本，至少能指回论文、章节或页码。

## 先把名字说清楚

> 📘 **摄取（ingest）**：把 PDF 或 HTML 变成内部可检索对象。通常包括切分和元数据。

> 📘 **chunk**：切出来的小段。问答时的证据通常来自若干 chunk，不是整篇论文。

> 📘 **证据对象**：chunk 加上定位字段（论文、段落、页码）。

> 📘 **重排（rerank）**：对初检结果再打分，把更可能回答子问题的段落提前。

> 📘 **Docs / InformationTable**：保存已摄取材料的状态容器。名字因仓库而异，职责相同：已入库集合。

## 运行逻辑

```mermaid
flowchart LR
  pdf[PDF 或网页] --> ingest[切分并入库]
  ingest --> obj[证据对象]
  obj --> retrieve[检索]
  retrieve --> rerank[重排]
  rerank --> gen[交给生成]
```

*图 1：生成只能看见证据对象，不能直接看见「全网」。*

## 读源码时先找什么

- 定位字段有没有 paper id、段落、页码。
- 未摄取的搜索命中能不能混进生成。
- 重排打分是否落盘。

> 🔶 **推断**：只有 URL 列表、没有 chunk 对象，引用只能指到网页，不能指到段落。
""",
        "projects": (
            ("paper-qa", "chunk / Docs / gather_evidence"),
            ("storm", "StormInformationTable"),
            ("zilliztech-deep-searcher", "子查询与重排"),
        ),
    },
    {
        "slug": "citation-gate",
        "code": "III.3",
        "part": "III. 文献与证据",
        "nav": "引用约束",
        "title": "引用约束：无来源的句子能不能写出去",
        "insight": "约束发生在生成之前。提示词里写「请引用」不算约束。",
        "body": """
## 这一章只讲一个闸

引用约束：生成阶段只能使用已检索到的证据对象；没有对象时应拒绝或标明缺失。

## 先把名字说清楚

> 📘 **来源字段**：句子或段落绑定的证据对象标识。

> 📘 **拒绝**：无来源时不写该句，或整段停住。

> 📘 **标缺失**：仍输出文本，但显式标出没有来源。和假装有引用不同。

> 📘 **综述模式**：同一条闸的长文用法：各节先检索，再带引用写，最后合并。

## 运行逻辑

```mermaid
sequenceDiagram
  participant I as 已入库证据
  participant G as 生成
  I-->>G: 证据对象列表
  G->>G: 逐句对齐来源
  alt 某句无来源
    G-->>G: 拒绝或标缺失
  else 均有来源
    G-->>G: 带引用文本
  end
```

*图 1：有没有闸，看无来源句子的分支，不看文风。*

## 读源码时先找什么

- 生成函数的输入是否必须带证据列表。
- 空列表时是报错、标缺失，还是照样写。
- 数字上标是后贴的，还是和证据对象一一对应。

> 🔶 **推断**：只在提示词里写「请引用」，没有证据对象字段，引用通常不可检查。
""",
        "projects": (
            ("paper-qa", "generate_answer"),
            ("storm", "来源去重后再编号"),
            ("autosurveys-autosurvey", "按节检索再写"),
        ),
    },
    {
        "slug": "sandbox-budget",
        "code": "IV.1",
        "part": "IV. 实验执行",
        "nav": "沙箱与预算",
        "title": "沙箱和预算：一次实验允许破坏什么、跑多久",
        "insight": "没有隔离和上限，失败实验会毁掉工作区，循环也没有停机条件。",
        "body": """
## 这一章只讲两个对象

执行沙箱和预算。它们是实验内环的硬边界。

## 先把名字说清楚

> 📘 **执行沙箱**：跑代码的隔离环境。限制文件系统、网络和时长。

> 📘 **预算**：允许消耗的步数、时间和模型调用次数。用尽是停机条件之一。

> 📘 **容器**：沙箱的一种实现。镜像相同，别人才能重放这次执行。

> 📘 **工作区**：允许读写的目录。沙箱不应默认等于宿主机全部磁盘。

## 运行逻辑

```mermaid
flowchart TD
  patch[待跑代码] --> box[沙箱]
  box --> ok{预算还够?}
  ok -->|够| run[执行]
  run --> out[指标或报错]
  ok -->|用尽| stop[停]
  run -->|超时或越权| stop
```

*图 1：沙箱限制空间，预算限制时间与次数。*

## 读源码时先找什么

- 能读哪些目录、能不能上网。
- 预算字段：步数、墙钟、调用次数。
- 超时后进程是否被杀掉，还是只在日志里写一句。

> 🔶 **推断**：文档写「安全执行」、代码里却是本机 `subprocess` 无超时，沙箱边界不成立。
""",
        "projects": (
            ("openai-mle-bench", "竞赛容器 + 只读 private 答案"),
            ("facebookresearch-mlgym", "任务环境"),
            ("bytedance-deer-flow", "Sandbox"),
        ),
    },
    {
        "slug": "trajectory",
        "code": "IV.2",
        "part": "IV. 实验执行",
        "nav": "轨迹",
        "title": "轨迹：下一次修改吃哪一次失败",
        "insight": "没有轨迹，搜索树和演化都无法复盘。最终分数不能代替中间记录。",
        "body": """
## 这一章只讲一个对象

轨迹：按时间记下的动作和结果，包括补丁、命令、指标、报错。

## 先把名字说清楚

> 📘 **轨迹**：一次或一轮实验的时间序列记录。

> 📘 **指标文件**：一次 run 写出的数值，供外环比较。应和代码版本一起保存。

> 📘 **workspace / Trace**：存放轨迹的目录或对象。名字因仓库而异。

> 📘 **失败 run**：没达标的那一次。若被覆盖，外环会丢掉失败原因。

## 运行逻辑

```mermaid
flowchart LR
  act[动作] --> rec[追加到轨迹]
  rec --> metric[指标文件]
  metric --> next[下一次补丁]
  rec --> next
```

*图 1：下一次修改的输入是轨迹，不是「再试一次」四个字。*

## 读源码时先找什么

- 失败 run 是否保留。
- 指标和下一次补丁是否同源。
- 轨迹是追加还是覆盖。

> 🔶 **推断**：只有最终分数、没有中间轨迹，外环搜索无法被第三方复盘。
""",
        "projects": (
            ("rd-agent", "Trace / workspace"),
            ("aideml", "树节点日志"),
            ("algorithmicsuperintelligence-openevolve", "Program artifacts"),
        ),
    },
    {
        "slug": "search-tree",
        "code": "IV.3",
        "part": "IV. 实验执行",
        "nav": "搜索树",
        "title": "搜索树：候选是节点，动作是边",
        "insight": "方法发现常常不是单链。节点保存一版代码，边是 draft、debug 或 improve。",
        "body": """
## 这一章只讲一个对象

搜索树（或网格）：每个节点是一版候选，边是一次修改。

## 先把名字说清楚

> 📘 **节点**：一版代码或程序，带父节点、指标、是否可运行。

> 📘 **边**：从父节点生成子节点的动作。常见三类：草案、修 bug、改进。

> 📘 **树搜索**：保存多个分支，按当前价值选下一个扩展。不是只沿一条路走。

> 📘 **MAP-Elites**：按特征网格占位的演化方法。格子里只留该特征下最好的程序。这里只需知道：候选按格子保存，不是单条链。

## 运行逻辑

```mermaid
flowchart TD
  root[初始草案] --> d1[draft]
  root --> d2[draft]
  d1 --> bug[debug]
  d1 --> imp[improve]
  d2 --> imp2[improve]
```

*图 1：动作类型决定子节点种类。策略决定先扩展谁。*

常见策略顺序：

1. 草案数量不够就继续 draft。
2. 坏叶节点按概率 debug。
3. 好节点 improve。

> 🔶 **推断**：配置里只有 `max_iters`、没有节点类型，更可能是单链重试，不是树搜索。
""",
        "projects": (
            ("aideml", "draft / debug / improve 树"),
            ("ai-scientist-v2", "BFTS 实验树"),
            ("algorithmicsuperintelligence-openevolve", "MAP-Elites 网格"),
        ),
    },
    {
        "slug": "claim-align",
        "code": "V.1",
        "part": "V. 写稿与审稿",
        "nav": "主张对齐",
        "title": "主张、图、实验记录必须同源",
        "insight": "写稿层吃上游产物。图中的数字和方法描述要来自同一次记录。",
        "body": """
## 这一章只讲一个关系

同源：主张、图、实验记录指向同一次产物。

## 先把名字说清楚

> 📘 **主张**：稿件中可被检查的命题，必须能指回实验记录或文献证据。

> 📘 **图文件**：由数据或结构说明生成的图像。数值图和示意方法图不是同一类。

> 📘 **同源**：图中的数字、方法描述和日志来自同一次实验记录。

> 📘 **Story / 稿件对象**：把标题、主张、证据指针收在一起的中间对象。

## 运行逻辑

```mermaid
flowchart LR
  rec[实验记录] --> claim[主张列表]
  rec --> fig[数值图]
  lit[文献证据] --> claim
  claim --> draft[章节]
  fig --> draft
```

*图 1：写稿不另起数字。数字从图和记录来。*

两类图：

- **数值图**：必须来自指标文件。
- **方法图**：来自模块关系，不冒充实验结果。

> 🔶 **推断**：生成图的提示只写「画一张架构图」，没有绑定模块名单或指标文件，图和正文很容易分叉。
""",
        "projects": (
            ("idea2paper", "Story"),
            ("paperclaw", "venue LaTeX + 实验 map"),
            ("paperbanana", "Critic 对照源文本"),
        ),
    },
    {
        "slug": "review-role",
        "code": "V.2",
        "part": "V. 写稿与审稿",
        "nav": "审稿角色",
        "title": "审稿角色判覆盖，不另起主张",
        "insight": "审稿输出问题列表。它应少改句子，多指出检查点缺口。",
        "body": """
## 这一章只讲一个角色

审稿角色：读取稿件和检查点，输出问题列表。

## 先把名字说清楚

> 📘 **检查点覆盖**：主张、图、引用、实验设置是否都在稿里出现，并且能指回产物。

> 📘 **问题列表**：审稿的提交物。每条应能指向稿件位置和缺失的检查点。

> 📘 **完整性清单**：固定条目的检查，例如引用、数据声明、图表编号。和自由评语不同。

> 📘 **模拟审稿**：用角色互动研究偏差。它是实验装置，不一定是投稿服务。

## 运行逻辑

```mermaid
flowchart TD
  ms[稿件] --> rev[审稿角色]
  ck[检查点] --> rev
  rev --> issues[问题列表]
  issues -->|未覆盖| ms
  issues -->|通过| done[可检查稿]
```

*图 1：审稿不发明新主张。它对照检查点。*

## 读源码时先找什么

- 审稿输入是否包括检查点或证据，而不只是正文。
- 输出是问题列表还是直接改稿。
- 角色之间看见哪些消息（独立审还是先看别人）。

> 🔶 **推断**：审稿提示只说「请严格一点」，没有对照表，覆盖检查通常不可复现。
""",
        "projects": (
            ("ahren09-agentreview", "Reviewer / AC 决策"),
            ("academic-research-skills", "integrity checklist"),
            ("tu2021-paperaudit", "planner / specialist findings"),
        ),
    },
    {
        "slug": "host-skill",
        "code": "VI.1",
        "part": "VI. 宿主与工具",
        "nav": "技能与宿主",
        "title": "技能挂在宿主上，不自研循环",
        "insight": "宿主提供会话和权限。技能提供科研步骤顺序。产物必须写回工作区。",
        "body": """
## 这一章只讲一对对象

宿主和技能。循环复用宿主，领域步骤放在技能里。

## 先把名字说清楚

> 📘 **宿主**：提供会话、权限、工具执行和文件系统的运行环境。

> 📘 **技能**：可发现、可安装的步骤说明，通常带指令文件和可选脚本。

> 📘 **技能清单**：宿主能枚举到的技能名和触发条件。没有清单，技能不可发现。

> 📘 **工作区**：宿主读写的目录。技能产物应写进这里。

## 运行逻辑

```mermaid
flowchart TD
  user[用户任务] --> host[宿主]
  host --> discover[发现技能]
  discover --> skill[选中的技能]
  skill --> steps[按指令调工具]
  steps --> ws[写入工作区]
```

*图 1：宿主负责运行，技能负责步骤顺序。*

和自研循环的差别：

- 自研循环：项目自己实现状态机。
- 技能挂宿主：状态机在宿主里，技能只描述科研步骤。

> 🔶 **推断**：只含 Markdown、不含脚本的技能，执行质量更依赖宿主当时的工具集。
""",
        "projects": (
            ("academic-research-skills", "Skill 目录 + pipeline 派发"),
            ("scientific-agent-skills", "可装载科学技能包"),
            ("jmiao24-paper2agent", "论文到可运行技能"),
        ),
    },
    {
        "slug": "tool-registry",
        "code": "VI.2",
        "part": "VI. 宿主与工具",
        "nav": "工具注册",
        "title": "工具要能被发现，不能只写进系统提示",
        "insight": "注册、检索、调用是三个协议。循环只依赖协议，不依赖工具内部实现。",
        "body": """
## 这一章只讲一个对象

工具目录：名字、参数说明、返回说明的注册表，加上按任务选出若干工具的检索。

## 先把名字说清楚

> 📘 **工具注册**：把可调用对象写进目录。

> 📘 **工具检索**：按当前任务从目录里选出若干工具。

> 📘 **调用协议**：一次调用的请求和响应格式。

> 📘 **系统提示**：写给模型的固定说明。把全部工具名塞进提示，工具就不可单独更新。

## 运行逻辑

```mermaid
flowchart LR
  task[当前任务] --> search[工具检索]
  reg[注册目录] --> search
  search --> call[按协议调用]
  call --> result[结构化结果]
```

*图 1：找不到工具应得到空列表，不是一段散文。*

工具层通常不负责文献引用、实验预算、稿件对齐。那些仍由前面各章的循环处理。

> 🔶 **推断**：只有包装脚本、没有检索接口，规模一大就会变成「把名字写进提示词」。
""",
        "projects": (
            ("mims-harvard-tooluniverse", "registry + find/execute"),
            ("snap-stanford-biomni", "ToolRegistry"),
            ("hicai-zju-scitoolagent", "科学工具检索"),
        ),
    },
    {
        "slug": "domain-tools",
        "code": "VII.1",
        "part": "VII. 领域执行器",
        "nav": "领域工具",
        "title": "领域约束写进工具，不写进形容词",
        "insight": "循环可复用。生物医学和化学把通用搜索换成 assay、知识库、分子工具。",
        "body": """
## 这一章只讲一次替换

领域执行器：把通用「调工具」换成该领域可执行动作。

## 先把名字说清楚

> 📘 **领域执行器**：循环和状态机可以复用；工具不能复用的那一层。

> 📘 **assay**：一次可记录的实验测定。在系统里应是可调用步骤，不是一段描述。

> 📘 **知识库工具**：查询结构化条目，返回带标识符的记录。

> 📘 **任务翻译**：自然语言目标变成工具序列。

## 运行逻辑

```mermaid
flowchart TD
  goal[自然语言目标] --> trans[任务翻译]
  trans --> tools[领域工具序列]
  tools --> rec[测定或查询记录]
  rec --> out[候选与证据]
```

*图 1：领域约束在工具和记录里。*

通用 Agent 常见工具是搜索和代码解释器。领域系统常见工具是筛选、影像、知识库、分子计算。

> 🔶 **推断**：工具清单短、提示词很长，领域约束多半还在文本里，执行时容易绕过。先数可调用工具。
""",
        "projects": (
            ("snap-stanford-biomni", "ToolRegistry + 代码 runner"),
            ("ur-whitelab-chemcrow-public", "RDKit / 反应 / 安全工具"),
            ("mims-harvard-txagent", "治疗知识库工具"),
        ),
    },
    {
        "slug": "device-safety",
        "code": "VII.2",
        "part": "VII. 领域执行器",
        "nav": "设备与安全",
        "title": "设备状态和安全检查是一等对象",
        "insight": "湿实验有仪器状态。对话历史不能代替 Idle / Running / Fault。",
        "body": """
## 这一章只讲两个对象

设备对象和安全检查。实验室编排可以几乎不依赖 LLM。

## 先把名字说清楚

> 📘 **设备对象**：表示一台仪器的数据结构，含状态和可执行动作。

> 📘 **安全检查**：执行前对动作合法性的判定。通过才发给设备。

> 📘 **实验目录**：一次实验的输入、输出、日志。失败后仍应能打开。

> 📘 **编排**：按依赖顺序调度仪器动作或计算步骤。它是状态机。

## 运行逻辑

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Running: 动作被接受
  Running --> Idle: 成功写目录
  Running --> Fault: 失败
  Fault --> Idle: 复位
```

*图 1：设备状态。发给设备前还要过安全检查。*

```mermaid
flowchart TD
  task[任务] --> plan[编排]
  plan --> safety{安全检查}
  safety -->|拒绝| stop[记录原因]
  safety -->|通过| exec[设备或计算后端]
  exec --> catalog[实验目录]
```

*图 2：拒绝也要写入目录，否则无法复盘。*

> 🔶 **推断**：没有设备状态字段的「实验室 Agent」，更可能是文档生成器。要以状态和目录为准。
""",
        "projects": (
            ("ad-sdl-madsci", "Node / Workflow / ActionResult"),
            ("pylabrobot-pylabrobot", "液体处理设备对象"),
            ("ur-whitelab-chemcrow-public", "safety 工具"),
        ),
    },
    {
        "slug": "evaluation",
        "code": "VIII.1",
        "part": "VIII. 评测",
        "nav": "任务与分数",
        "title": "任务、环境、分数必须能重放",
        "insight": "评测不问品牌故事。同一提交、同一环境、同一评分器，要得到同一分数。",
        "body": """
## 这一章只讲三个对象

任务、环境、分数。少一个都不能叫基准。

## 先把名字说清楚

> 📘 **任务**：有准备步骤、提交物和评分规则的一道题。

> 📘 **环境**：跑任务的隔离运行时。常用容器。要能用同一镜像再起一次。

> 📘 **提交**：交出来打分的对象，例如代码、答案文件、轨迹。

> 📘 **已知答案**：评分器持有、对受试系统隐藏的正确答案或检查脚本。

> 📘 **可重放**：同一提交、同一环境、同一评分器，得到同一分数。

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

基准常见切法：论文复现、科学编程、假设发现、端到端产物是否齐全、审稿是否打中标注。

> 📌 **事实边界**：各仓库在冻结 commit 上的具体分数，以对应 13 节分析为准，不在这里汇总。

> 🔶 **推断**：只有演示脚本、没有评分器，不能当成基准。演示证明能跑，基准证明能打分。
""",
        "projects": (
            ("openai-mle-bench", "submission.csv + grader"),
            ("osu-nlp-group-scienceagentbench", "程序 / 轨迹 / 成本"),
            ("tu2021-paperaudit", "findings 与标注"),
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


def chapter_slugs(chapter: dict) -> list[str]:
    out: list[str] = []
    for item in chapter["projects"]:
        out.append(item if isinstance(item, str) else item[0])
    return out


def project_table(chapter: dict, by_slug: dict[str, dict]) -> str:
    rows = ["<table><thead><tr><th>这个对象在仓库里</th><th>项目</th><th>分析</th><th>源码快照</th></tr></thead><tbody>"]
    for item in chapter["projects"]:
        slug, obj = (item, "") if isinstance(item, str) else item
        project = by_slug[slug]
        commit = project["analyzed_commit"]
        tree = f"https://github.com/{project['repo']}/tree/{commit}"
        short = commit[:7]
        rows.append(
            "<tr>"
            f"<td>{html.escape(obj)}</td>"
            f"<td>{html.escape(project['name'])}</td>"
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
    missing = sorted({slug for chapter in CHAPTERS for slug in chapter_slugs(chapter) if slug not in by_slug})
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
        toc.append((2, "impl", "例证：这个对象在开源里叫什么"))
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
