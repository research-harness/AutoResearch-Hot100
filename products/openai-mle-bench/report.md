# openai/mle-bench：MLE-bench 的公开源码合同

| 字段 | 值 |
|---|---|
| GitHub | https://github.com/openai/mle-bench |
| License | 根 `LICENSE` 为 MIT；GitHub API 仍为 NOASSERTION |
| 分析 commit | `507f92e1138bb6e40dac5c6ee7a6758e6424bf97` |
| 产品类型 | 科研/机器学习 Agent benchmark 与执行评测 |
| 直接证据 | `README.md`, `LICENSE`, `pyproject.toml`, `mlebench/data.py`, `mlebench/grade.py`, `mlebench/metrics.py` |

本文用 📘 标注文档或源码中可直接定位的事实，🔶 标注由控制流推导的边界，💬 标注评价与借鉴建议。仓库动态元数据沿用候选清单，源码判断只绑定页面中的固定提交。

## 1. 它到底是什么

OpenAI 发布的机器学习工程 Agent 评测代码与数据构造仓库。它把 75 个 Kaggle 风格竞赛转成可准备、可执行、可提交、可评分的任务，核心问题是 Agent 能否从任务说明和数据生成有效 submission.csv，而不是能否独立完成一篇有引用的科研论文。仓库同时发布数据准备、评分逻辑和若干被评测 Agent 的启动适配。

## 2. 运行时堆叠

运行时由竞赛注册、数据准备、容器环境、Agent 启动、提交评分和汇总组成。data.py 下载 Kaggle 压缩包、建立 public/private 目录、运行 prepare 函数并生成 checksum；environment/Dockerfile 提供执行镜像和 grading server；agents/registry.py 与 agents/run.py 负责适配器和容器内 start.sh；grade.py 读取 CSV、答案和 leaderboard，生成 CompetitionReport。

## 3. 阶段机或 DAG

准备阶段下载并校验数据，Agent 在容器中训练并写 submission.csv，grading server 先检查提交能否被 grader 处理，然后按真实竞赛指标评分，最后 aggregate_grading_reports 按复杂度 split 汇总 any-medal 比例。private 答案以只读方式挂载给评分侧，public 数据供 Agent 使用。
```mermaid
flowchart TD
  kaggle[Kaggle 压缩包] --> prepare[prepare / checksum]
  prepare --> pub[public 数据]
  prepare --> priv[private 答案只读]
  pub --> container[容器内 Agent]
  container --> sub[submission.csv]
  sub --> validate[/validate]
  priv --> grade[grade_csv]
  validate --> grade
  grade --> report[CompetitionReport]
  report --> agg[按 split 汇总]
```

## 4. Tool / Skill / Agent 怎么切

Agent 负责工程决策，容器提供 shell、依赖和工作区，grading server 提供 /validate，grader 提供任务指标，实验脚本提供多次运行聚合。它没有独立科研 Skill 注册表；任务说明、submission 格式和命令构成隐式操作合同。

## 5. 文献怎么来、是否入库、引用约束

README 提供 MLE-bench 论文引用、Kaggle 数据来源和竞赛说明。运行时不维护论文、主张或来源定位，也不把代码决策链接到论文证据。leaderboard 和 SOTA 类信息是 benchmark 参照，不是自动生成的学术引文。

## 6. 实验 / 代码执行

执行是真实的模型训练和提交评分。prepare 会下载、解压、校验和准备数据；run.py 创建容器、挂载 public/private 目录、等待 /health 后以非 root 用户执行 Agent，最后抽取 submission、日志和代码。grade_csv 计算分数、奖牌和 above-median；本次没有下载数据或运行容器。

## 7. 写稿怎么做

产物是 JSON grading report、日志、代码和提交文件，不是章节化论文。聚合脚本可产出均值和 SEM，适合给上层论文表格使用，但没有引用配额、章节模板、数字一致性或审稿修订门。

## 8. 图怎么做

README 的 leaderboard、复杂度拆分表和项目图属于 benchmark 展示；仓库没有统一 figure plan、图注证据绑定或出版质量检查。外部使用者可将逐竞赛报告导入其他绘图系统，但不能称仓库自动生成论文图。

## 9. 和 RH 的相似点

和 RH 一样，它把长任务拆成可保存产物，强调真实执行、失败记录和结果审计；checksum、运行组、提交物和 grading report 对应 RH 的数据、实验和 provenance artifact。两者都允许外部 Agent 接入统一评价合同。

## 10. 和 RH 的不同点

MLE-bench 衡量竞赛工程分数和奖牌，RH 还要处理研究问题、文献证据、统计推断、稿件和发布。MLE-bench 的 private 数据用于评分而非 claim-evidence；grader 不判断科学新颖性、解释质量或引文正确性。

## 11. 优点 / 缺点

优点是任务边界、数据隔离、校验和、容器、grader 和汇总清晰；提交能否被真实指标处理而非自报。缺点是 Kaggle 依赖和准备成本高，部分竞赛存在数据泄漏或切分问题，跨 Agent 分数受资源和日期影响，容器不自动解决所有侧信道，也没有科学证据或稿件一致性审计。

## 12. RH 可学的 1–3 条

1. 在 RH 实验中分离 public input、private evaluation、submission 和 grading report。
2. 将数据版本、准备脚本 checksum、资源、seed 和 Agent 配置写入实验 artifact。
3. 在昂贵实验前做格式和健康检查，但不要把格式通过误当作科学结论。

## 13. 名字速查表

`Competition`：竞赛注册对象；`prepare`：构造 public/private 数据；`grade_csv`：评分 CSV；`validate_submission`：轻量提交校验；`CompetitionReport`：单竞赛结果；`run_in_container`：容器生命周期；`aggregate_reports`：跨运行汇总。

补充核验：本次查看了数据准备、容器运行、HTTP 校验和聚合入口，能确认的是代码如何组织评测，不是任何 Agent 在 75 项竞赛上的实际成绩。README 中的榜单包含外部提交，且仓库自己列出若干泄漏和切分已知问题；因此比较时必须同时报告版本、竞赛集合、资源、seed 和规则接受状态。

> 📌事实边界：本页依据 `507f92e1138bb6e40dac5c6ee7a6758e6424bf97` 固定公开源码快照、2026-09-17 `data/candidates-staging.jsonl` 元数据和下列实际查看文件静态撰写（`README.md`、`LICENSE`、`pyproject.toml`、`mlebench/data.py`、`mlebench/grade.py`、`mlebench/metrics.py`、`agents/run.py`、`environment/grading_server.py`、`environment/Dockerfile`、`experiments/aggregate_grading_reports.py`、`agents/registry.py`）。没有把 README 的榜单、论文结果或运行说明当作本次实测；未调用未配置的模型/API，未运行完整 benchmark（除非明确另有说明），未据此声称运行效果。
