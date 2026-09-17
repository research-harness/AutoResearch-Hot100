# OS-Copilot/ScienceBoard：ScienceBoard 的公开源码合同

| 字段 | 值 |
|---|---|
| GitHub | https://github.com/OS-Copilot/ScienceBoard |
| License | MIT（根 `LICENSE` 已查阅，与 GitHub API 一致） |
| 分析 commit | `c8d5010bdba32afc5dfb16472873bed148c39a45` |
| 产品类型 | 科研/机器学习 Agent benchmark 与执行评测 |
| 直接证据 | `README.md`, `LICENSE`, `requirements.txt`, `main.py`, `sci/Presets.py`, `sci/Prompts.py` |

本文用 📘 标注文档或源码中可直接定位的事实，🔶 标注由控制流推导的边界，💬 标注评价与借鉴建议。仓库动态元数据沿用候选清单，源码判断只绑定页面中的固定提交。

## 1. 它到底是什么

ScienceBoard 是评估多模态自主 Agent 在现实科学工作流中表现的代码、环境和数据仓库。README 说明其基于 OSWorld 与 VMware，提供虚拟机、科学应用和任务配置，让 Agent 在 GUI/文本环境中完成科学操作。它关注工具使用、环境状态和任务成功，不是文献管理或论文生产平台。

## 2. 运行时堆叠

main.py 负责选择模型、Agent/Community、Tester 与任务路径；sci/base/task.py 组织初始化、观察、community 生成代码、执行 primitives、记录日志和最终 eval；sci/base/community.py 定义一个或多个模型如何协作；sci/vm/vmanager.py 获取截图、可访问性树、文件和应用状态。Presets 列出 Lean、Qt、KAlgebra、Celestia、Grass GIS 等科学软件路径。

## 3. 阶段机或 DAG

ScienceBoard 的阶段是加载任务 JSON→初始化 VM/应用→获取 screenshot/a11y/textual observation→Community 生成代码→VM 执行→记录 observation/code→按 states/info/file/early-stop 评价。
```mermaid
flowchart LR
 A[任务JSON与VM快照] --> B[Manager初始化应用]
 B --> C[截图/a11y/状态观察]
 C --> D[Community多Agent协作]
 D --> E[GUI或科学工具动作]
 E --> F[日志与状态] 
 F --> G[states/info/file评价]
```
Task.predict 会在连续错误达到 penalty 阈值时减少剩余步数，直到 planned termination 或 timeout。

## 4. Tool / Skill / Agent 怎么切

Agent 是模型调用，Community 是多 Agent 协作方式，Manager 是 Raw/VM 应用控制，Task 是步骤、观察、动作和评价合同，Tester 管理任务集合与 logs。任务可以通过继承 Community 自定义协作。源码有 RawTask/VMTask 和应用专用 TaskMixin，说明 skill 更接近应用插件/primitive，而非独立技能目录。

## 5. 文献怎么来、是否入库、引用约束

README 链接 ScienceBoard 论文、OSWorld 和各科学应用修改仓库；任务 JSON 可包含应用状态和文件条件，但运行时没有通用论文、claim、citation 或 evidence span。科学软件状态是操作证据，不是科学文献证据。

## 6. 实验 / 代码执行

执行依赖 VMware Workstation、预制 VM snapshot、应用插件和本地模型 API。Task 在 init 后循环观察和执行，Manager 返回状态码，eval 检查状态、info 或文件内容；日志装饰器记录输入和结果。README 给出硬件建议和常见 VM/a11y 错误；本次没有启动 VMware、下载镜像或运行任务。

## 7. 写稿怎么做

不负责写论文。logs 记录模型动作、观察、社区和结果；ScienceBoard 的论文/README 图是 benchmark 说明，不能把任务日志自动变成方法和结果章节。

## 8. 图怎么做

仓库自带 overview/workflow 图和徽章，GUI screenshot/a11y 是环境观察，不是论文定量作图。没有 figure plan、数据图表合同或出版 QA。

## 9. 和 RH 的相似点

与 RH 都将长任务拆成阶段、保存日志、管理失败并依赖可复核执行。ScienceBoard 的 observation/action/result 三分法可启发 RH 记录实验前状态、执行动作和后验结果。

## 10. 和 RH 的不同点

ScienceBoard 的成功标准通常是 VM 状态、文件内容或任务终止条件；RH 还要求科学问题、文献证据、统计和稿件。GUI 操作成功不能证明分析结论正确，VM 隔离也不替代 provenance/citation。

## 11. 优点 / 缺点

优点：把多模态观察、GUI/科学应用和可配置协作纳入真实 VM；Task 的初始化—预测—评价链明确；状态/文件检查比只看文本更可验证。缺点：VM/软件依赖重，a11y 和应用启动易失败，模型行为和坐标脆弱，任务配置与插件维护成本高，未形成统一科学证据层。

## 12. RH 可学的 1–3 条

1. 将实验前观察、动作和后验状态分别记录。
2. 把应用状态检查作为执行 gate，但继续用独立数据/统计检查科学结果。
3. 为科学软件操作保存版本、VM 镜像和插件来源。

## 13. 名字速查表

`Task`：任务生命周期；`Community`：多 Agent 协作；`Manager`：Raw/VM 应用控制；`VManager`：虚拟机观察；`TaskMixin`：应用状态/文件评价；`Tester`：批量任务与日志。

补充核验：Task 的状态检查支持 info、states、file 和 early-stop，VM 管理器还依赖截图和可访问性树；这些都是操作层信号。若要把操作结果写入科研结论，仍需要保存应用版本、输入文件、脚本、数值输出和独立统计检查。

> 📌事实边界：本页依据 `c8d5010bdba32afc5dfb16472873bed148c39a45` 固定公开源码快照、2026-09-17 `data/candidates-staging.jsonl` 元数据和下列实际查看文件静态撰写（`README.md`、`LICENSE`、`requirements.txt`、`main.py`、`sci/Presets.py`、`sci/Prompts.py`、`sci/Tester.py`、`sci/base/task.py`、`sci/base/community.py`、`sci/vm/vmanager.py`、`vm_config/server.py`）。没有把 README 的榜单、论文结果或运行说明当作本次实测；未调用未配置的模型/API，未运行完整 benchmark（除非明确另有说明），未据此声称运行效果。
