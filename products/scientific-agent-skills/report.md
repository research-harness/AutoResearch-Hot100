# K-Dense-AI/scientific-agent-skills：跨宿主的 166 个科研能力包，而非科研编排器

<div class="meta">

| 字段 | 值 |
|---|---|
| GitHub | https://github.com/K-Dense-AI/scientific-agent-skills |
| License | MIT |
| Stars | 45,184（2026-09-16 快照） |
| GitHub 最后 push / 本地 HEAD | 2026-09-14 · `330c8e7` |
| 当前公开标识 | README v2.68.0；`plugin.json` 另有版本，存在可见版本漂移 |
| 产品类型 | **科研 Skill 库**（写作、检索、方法、图等广覆盖）；不是统一 e2e 运行时 |
| 分析证据 | README、`AGENTS.md`、`plugin.json`、`skills/`、`skills/scientific-writing/SKILL.md`、tests/、LICENSE |

</div>

## 1. 它到底是什么

Scientific Agent Skills（原 Claude Scientific Skills）提供 166 个可装载的科学技能，涵盖生信、化学、临床研究、数据分析、科研写作、同行评议和数据库调用。它遵循 Agent Skills / Agent Plugins 格式，支持 Claude Code、Codex、Cursor 等宿主。

它不是“生成一篇论文”的单一系统，而是给任意 Coding Agent 加一套**可分发的程序性知识**。对 RH 最有价值的是分发规范、Skill QA 与领域覆盖策略，不是复制其庞大的目录。

## 2. 运行时堆叠

- Agent runtime：无。宿主 Agent 解释并执行每个 `skills/<name>/SKILL.md`。
- 状态：由宿主会话、工作区和对应的科学工具/数据库保存。
- 分发：`plugin.json` + Agent Skills 目录；可用 `npx skills add` 等安装。
- 质量保障：安全扫描和 skill tests 在 CI 中运行；测试刻意放在 skill 内容之外。
- 边界：`AGENTS.md` 明确不把它变成总 orchestrator；每个 skill 保持一个清楚用途。

> 📘术语
> **Agent Skills 标准**：把“何时使用、先做什么、要调用哪些工具、输出应是什么”封装为可被不同 Agent host 读取的目录约定。它是 prompt/workflow 的分发格式，不是服务协议。

## 3. 阶段机或 DAG

没有产品级统一阶段机。实际结构是宿主按任务选择若干 Skill：

```mermaid
flowchart LR
  task[用户科研任务]
  host[Claude Code / Codex / Cursor]
  skill[选择一个或多个 Skill]
  api[数据库 / Python 工具 / 文件]
  out[任务产物]
  task --> host --> skill --> api --> out
```

其核心设计选择是“不给 166 个 Skill 再套一层强编排器”；这避免了一个巨大而难以维护的万能流程，但将跨 Skill 的质量责任留给宿主或使用者。

## 4. Tool / Skill / Agent 怎么切

- **Skill**：唯一的一等抽象；`scientific-writing`、`literature-review`、`hypothesis-generation`、`paperclip`、`paper-lookup` 等是独立包。
- **Tool**：技能指导 Agent 使用 Python 库、数据库 API 或命令；没有公共 MCP service。
- **Agent**：宿主 Agent，而不是库中自建 agent swarm。
- **测试**：工具脚本和测试放在仓库测试层，避免把测试指令塞入每份 Skill。

## 5. 文献怎么来、是否入库、引用约束

包含 paper lookup、全文生物医学检索、literature review 等 Skill，也覆盖 100+ 数据库。但它没有一个统一 paper pool / evidence graph；每个 skill 可按自己的指南取数据。`paperclip` 的行级全文 citation 思路值得观察，但不是一个全局知识库。

## 6. 实验 / 代码执行

可以指导生信、化学模拟、机器学习、地理科学等 Python 任务，执行由宿主环境承担。没有 RH 正式 experiment 或 Arena contract，也没有统一资源/安全策略。

## 7. 写稿怎么做

有 scientific writing、peer review、grant、poster、Mermaid 写作等 skill。`scientific-writing` 明确区分 draft、evidence 和 approval，这正是值得 RH 学习的局部纪律；但它不会把所有写作 Skill 自动连成一篇可提交论文。

## 8. 图怎么做

有 publication-quality figures、poster、schematic 等指导，但不是 PaperBanana 式图形运行时，也没有对实验记录的强制数据到图映射。

## 9. 和 RH 的相似点

- 都把 Skill 看成给 Agent 的操作说明，而不是 Tool 的实现。
- 都可依附 Claude Code/Codex，而非重造聊天 host。
- 都关心科学写作、文献、图和研究方法的可分发指南。
- 都需要目录、描述和入口与真实能力保持一致。

## 10. 和 RH 的不同点

- RH 有六阶段控制面、MCP Tool 合同、topic DB 和 artifact/provenance；本库没有。
- 该库用高覆盖面换取统一工作流深度；RH 用一条长程科研链换取可审计性。
- RH 可为共享 key 建网关；Skill 库本身不解决多席位 secret/ACL。

## 11. 优点 / 缺点

**优点**

- MIT、跨宿主，安装与分发摩擦低。
- 166 项覆盖及 100+ 数据库，使其成为领域技能地图。
- 明确的“技能不等于 orchestrator”边界值得尊重。
- CI 有安全扫描和 Skill 测试，维护节奏活跃。

**缺点**

- 166 个候选可能让宿主路由错误，用户也难以知道哪几个可组合。
- 业务质量 gate 分散在文档，跨技能的一致性不足。
- README 与 `plugin.json` 版本不一致，说明超大 Skill 集仍会发生表面漂移。

## 12. RH 可学的 1–3 条

1. **输出 RH Skill 的 portable manifest**：保持现有 Skill 为权威，再生成 Agent Skills 兼容包，不复制第二套内容。
2. **建立 Skill inventory parity CI**：目录、manifest、短描述、文档与可安装表面必须集合相等。
3. **将通用数据库 lookup 做成一个可路由的 Skill 门面**，内部仍调用 RH `paper_search`/服务网关，不能把供应商 key 重新注进用户环境。

## 13. 名字速查表

| 名字 | 先决概念 | 含义 |
|---|---|---|
| Agent Skills | 分发格式 | 跨宿主读取任务指南的目录标准 |
| Agent Plugins | manifest | 可由插件宿主加载整组 skill 的包格式 |
| `plugin.json` | manifest | 声明插件版本和可发现内容的文件 |
| `skills/` | Skill | 所有独立能力包的根目录 |
| `scientific-writing` | writing workflow | 科学写作证据/审批约束的 Skill |
| `paperclip` | full-text citation | 侧重全文和行级引用定位的能力包 |
| Skill test | CI | 验证 skill 结构、脚本或合同是否漂移的测试 |

---

> 📌事实边界
> 166 个 Skill 的数量是仓库公开清单，不等于每个 Skill 的效果都被独立测量。