# AutoResearch Hot 100

面向自动化科研开源项目的中文技术架构分析与可复核快照。

- 站点：<https://atlas.zhice.io>
- GitHub：<https://github.com/research-harness/AutoResearch-Hot100>
- 当前快照：2026-09-17
- 当前完整分析：20 个项目（持续扩展至 100 个）
- 每篇分析：固定 13 节、至少一张架构图、固定 commit、公开证据文件清单与事实边界

## 内容范围

图谱覆盖端到端科研系统、方法发现与自动实验、论文检索与证据、学术写作与技能、科研绘图等类别。它不是 stars 榜单，也不把上游 README 的能力宣称当作独立效果验证。

每个项目包含：

1. 它到底是什么
2. 运行时堆叠
3. 阶段机或 DAG
4. Tool / Skill / Agent 怎么切
5. 文献怎么来、是否入库、引用约束
6. 实验 / 代码执行
7. 写稿怎么做
8. 图怎么做
9. 和 Research Harness 的相似点
10. 和 Research Harness 的不同点
11. 优点 / 缺点
12. Research Harness 可学的 1–3 条
13. 名字速查表

## 仓库结构

```text
data/projects.jsonl        项目目录与固定快照
products/<slug>/report.md  中文架构分析
products/<slug>/evidence.json
                            分析 commit 与上游证据文件
site/                       无框架静态页面模板和本地 Mermaid
tools/build.py              生成 dist/
tools/check.py              内容、结构、链接和公开卫生门禁
```

## 本地构建

需要 Python 3、Pandoc 和 BeautifulSoup 4。

```bash
python3 -m pip install -r requirements.txt
python3 tools/check.py
python3 tools/build.py
python3 tools/check.py
python3 -m http.server 8000 --directory dist
```

打开 <http://localhost:8000>。

## 收录和更新规则

- 项目必须有公开 GitHub 仓库，并与自动化科研链的至少一个环节直接相关。
- 正文事实绑定 `analyzed_commit`；动态 GitHub 元数据绑定 `snapshot_date`。
- 只有完成 13 节分析、证据清单和审核的项目才标为 `published`。
- 未运行的软件能力按源码或公开文档描述，不写成“已验证”。
- 上游源码不复制进本仓库；证据清单只保存相对路径和固定 commit 链接。
- 更正事实或推荐候选项目，请提交 Issue；完整分析需同时更新项目记录、报告和证据清单。

## 关于 Research Harness

本图谱由执策团队维护。我们也在建设 [Research Harness（执策·研枢）](https://zhice.io/tools/research-harness/?utm_source=atlas&utm_medium=referral)：面向文献、证据、实验规划、论文写作与质量门禁的 Agent-first 科研工作流平台。图谱中的竞品分析不构成对 Research Harness 效果的证明。

## 许可

- `tools/` 与站点模板：MIT，见 [LICENSE](LICENSE)
- 原创中文分析与项目目录：CC BY 4.0，见 [CONTENT-LICENSE.md](CONTENT-LICENSE.md)
- 被分析项目的名称、代码、文档和商标遵循各自上游许可
