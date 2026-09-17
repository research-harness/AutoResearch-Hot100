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
        "insight": "编码 Agent 交付能跑的改动；科研 Agent 交付能被检查的研究记录。共用循环，产物不同。",
        "body": """
<p>把自动化科研看成一个 Agent，不要先看成一百个仓库。循环仍是：读上下文、调工具、把结果写回去，直到停。停的条件换成了假设有没有被实验碰到、稿件有没有过检查点、引用能不能回到文献。</p>
<p>开源实现通常叠成六层：宿主与技能、循环与多角色、文献→假设→实验→写稿→审稿这条链、领域执行器、评测、以及冻结的证据与产物。后面每一章只讲其中一段，并指出这段在哪些仓库里能看见。</p>
<p>Hot 100 按赛道打分。这里按工作流读同一批源码。</p>
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
<p>端到端系统把科研链收成一条流水线或一张阶段图。入口常常是想法、数据文件或一篇种子论文；出口是带图的稿件、实验日志，或两者都有。</p>
<p>差别在边界。有的实现每阶段写盘、可续跑；有的把人挡在检查点上；有的一跑到底，失败就从头来。读这些仓库时先找阶段对象和产物目录，再看模型提示词。</p>
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
<p>查询进来之后，系统要决定现在该检索、该跑代码，还是该停下来等人。显式状态机、Packet、LangGraph 节点或 TaskLog，都是在给这个决定留位置。</p>
<p>多角色并不是把同一个提示词复制三份。综述、实验员、写作者、审稿人各看不同的工具和记忆。读源码时看角色是怎么被调度的，以及失败时状态写在哪。</p>
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
<p>技能包把「检索这篇」「跑这个实验」「改这段 LaTeX」收成可发现的指令和脚本。宿主负责权限、会话和工具；技能负责科研领域里的步骤顺序。</p>
<p>读这类仓库，重点不是又一个 Scientist 品牌，而是技能清单、安全扫描，以及它怎样把产物交回宿主工作区。</p>
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
<p>这一段覆盖搜索、浏览、论文摄取、重排和带引用回答。有的系统面向全网；有的只在私有 PDF 或开放学术索引里走。</p>
<p>看三个接口：查询如何被拆成子问题、证据如何变成可引用对象、生成阶段能不能拒绝无来源的句子。综述生成是同一条链的长文模式。</p>
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
<p>自动实验系统通常有一条内环（改代码、跑、看指标）和一条外环（换假设、换搜索）。有的绑在单一训练脚本上，有的把机器学习工程拆成竞赛式任务。</p>
<p>读这些实现时盯执行沙箱、预算和轨迹。没有轨迹，演化搜索和树搜索都无法复盘。</p>
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
        "insight": "写稿不是把日志粘进 LaTeX。图要承担主张，审稿角色要能指出稿件没覆盖的检查点。",
        "body": """
<p>写作技能、Overleaf 旁路助手、架构示意图生成、多角色审稿，都是在稿件这一层工作。有的系统把审稿做成数据集和基准，有的做成在线建议。</p>
<p>和实验层的接头是图表数据与方法描述是否同源。分析页里的「图怎么做」「写稿怎么做」两节就是为这个接头准备的。</p>
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
<p>通用科研 Agent 调的是搜索和解释器。生物医学系统调的是基因筛选、胸部影像、治疗知识库或虚拟实验室会议。人还在环里时，会议记录就是状态。</p>
<p>读这些仓库先列工具清单，再看任务如何被翻译成工具序列。评测集（如单细胞发现基准）用来卡住「发现了什么」而不是「说得像不像」。</p>
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
        "insight": "湿实验和计算化学把调度、设备和安全检查变成一等对象。实验室不是又一个聊天窗口。",
        "body": """
<p>这一段从分子工具、晶体设计、原子模拟，走到液体处理硬件和自驱实验室编排。有的实现是 LangChain 工具箱；有的根本不是 LLM Agent，而是设备与实验目录。</p>
<p>看它如何把自然语言任务落到具体仪器或计算后端，以及失败时数据目录是否还在。</p>
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
<p>基准把论文复现、科学编程、假设发现、端到端研究和审稿可靠性收成可准备、可提交、可打分的任务。容器、虚拟机和已知答案，是为了让轨迹能被别人再跑一遍。</p>
<p>科研 Agent 若没有这一层，工作流只停在演示。分析页里的评测项目说明任务怎么切、分数怎么来。</p>
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
<p>循环要能找到工具，而不是把全部领域知识写进系统提示。工具图谱、材料数据库问答、量化研究底座、数据侧改进，都属于这一层。</p>
<p>读这些实现时看注册、检索和调用协议。它们给前面各章的 Agent 提供手，自己不一定跑完整条科研链。</p>
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


def series_tables() -> str:
    blocks: list[str] = []
    current_part = None
    rows: list[str] = []
    for chapter in CHAPTERS:
        if chapter["part"] != current_part:
            if rows:
                blocks.append(f'<div class="book"><h3>{html.escape(current_part)}</h3><table>{"".join(rows)}</table></div>')
                rows = []
            current_part = chapter["part"]
        rows.append(
            f'<tr><td class="num">{html.escape(chapter["code"])}</td>'
            f'<td class="title"><a href="{html.escape(chapter["slug"])}/">{html.escape(chapter["title"])}</a></td>'
            f'<td class="insight">{html.escape(chapter["insight"])}</td></tr>'
        )
    if rows:
        blocks.append(f'<div class="book"><h3>{html.escape(current_part)}</h3><table>{"".join(rows)}</table></div>')
    return "\n".join(blocks)


def series_nav(active: str) -> str:
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
            f'<li><a{cls} href="../{html.escape(chapter["slug"])}/">{html.escape(chapter["code"])} {html.escape(chapter["nav"])}</a></li>'
        )
    if items:
        blocks.append(f"<h3>{html.escape(current_part)}</h3><ul>{''.join(items)}</ul>")
    return "\n".join(blocks)


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


def render_inside(dist: Path, template_index: Path, template_chapter: Path, base_url: str, projects: list[dict]) -> None:
    by_slug = {project["slug"]: project for project in projects}
    missing = sorted({slug for chapter in CHAPTERS for slug in chapter["projects"] if slug not in by_slug})
    if missing:
        raise SystemExit(f"inside chapters reference unknown slugs: {missing}")
    dest = dist / "inside"
    dest.mkdir(parents=True)
    snapshot = max(project["snapshot_date"] for project in projects)
    index = template_index.read_text(encoding="utf-8").replace("{{SNAPSHOT}}", snapshot).replace("{{SERIES}}", series_tables())
    (dest / "index.html").write_text(index, encoding="utf-8")
    chapter_template = template_chapter.read_text(encoding="utf-8")
    for number, chapter in enumerate(CHAPTERS):
        page = chapter_template
        for key, value in {
            "{{TITLE}}": html.escape(f'{chapter["code"]} {chapter["title"]}｜Inside Agentic Science'),
            "{{DESCRIPTION}}": html.escape(chapter["insight"], quote=True),
            "{{CANONICAL}}": f'{base_url}/inside/{chapter["slug"]}/',
            "{{SERIES_NAV}}": series_nav(chapter["slug"]),
            "{{CODE}}": html.escape(f'{chapter["part"]} · {chapter["code"]}'),
            "{{HEADING}}": html.escape(chapter["title"]),
            "{{INSIGHT}}": html.escape(chapter["insight"]),
            "{{BODY}}": chapter["body"],
            "{{PROJECTS}}": project_table(chapter, by_slug),
            "{{PAGER}}": pager(number),
        }.items():
            page = page.replace(key, value)
        folder = dest / chapter["slug"]
        folder.mkdir()
        (folder / "index.html").write_text(page, encoding="utf-8")
