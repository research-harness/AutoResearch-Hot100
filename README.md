# AutoResearch Hot 100

[Inside Agentic Science](https://research-harness.github.io/AutoResearch-Hot100/) 把 100 个自动化科研开源项目读成一套导读：首页按科研链分九部，八个赛道各有公开打分的 Top 10，点项目名进入 13 节中文架构分析。

- 站点：<https://research-harness.github.io/AutoResearch-Hot100/>
- GitHub：<https://github.com/research-harness/AutoResearch-Hot100>
- 当前快照：2026-09-17
- 分析池：100 个已完成 13 节分析的项目
- 公开榜：8 个赛道，每榜最多 10 名
- 每篇分析：固定 13 节、至少一张架构图、固定 commit、公开证据文件清单与事实边界

## 评分口径

榜单不是运行效果实测，也不只按 stars 排序。每个已发布项目用同一套公开快照打四项分，每项 0–25，加总后在赛道内取 Top 10。

| 维度 | 依据 | 计分 |
|---|---|---|
| 社区关注 | `projects.jsonl` 里的 stars 快照 | `log10(stars+1)`，约 2 万星封顶 |
| 近期活跃 | 快照日与 `pushed_at` 的间隔 | 540 天内线性衰减，更近更高 |
| 证据完整度 | `evidence.json` 中实际查看的源码/文档路径数 | 12 个文件封顶 |
| 分析深度 | 对应 `report.md` 的篇幅 | 约 3000–8000 字线性映射 |

同分时用收录顺序 `featured_order` 打破平局。分数会随快照更新重算；分析正文仍绑定 `analyzed_commit`，不会因为 stars 变化而改写。

未运行过的软件能力按源码或公开文档描述，不写成“已验证效果”。README 宣称和源码核验结果不混写。

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
- 只有完成 13 节分析、证据清单和审核的项目才标为 `published`，才进入评分池。
- 计划按快照周期更新 stars、`pushed_at` 并重算八榜；分析页只在源码复核后改。
- 上游源码不复制进本仓库；证据清单只保存相对路径和固定 commit 链接。
- 更正事实、质疑分数或推荐候选项目，请提交 Issue；完整分析需同时更新项目记录、报告和证据清单。

## 关于 Research Harness

本图谱由执策团队维护。图谱中的竞品分析不构成对 Research Harness 效果的证明。

## 许可

- `tools/` 与站点模板：MIT，见 [LICENSE](LICENSE)
- 原创中文分析与项目目录：CC BY 4.0，见 [CONTENT-LICENSE.md](CONTENT-LICENSE.md)
- 被分析项目的名称、代码、文档和商标遵循各自上游许可
