#!/usr/bin/env python3
"""Build the static Automated Science Atlas into dist/."""
from __future__ import annotations

import html
import json
import math
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECTS = ROOT / "data" / "projects.jsonl"
PAGE_TEMPLATE = ROOT / "site" / "template.html"
DASHBOARD_TEMPLATE = ROOT / "site" / "dashboard-template.html"
LIST_TEMPLATE = ROOT / "site" / "list-template.html"
BASE_URL = "https://research-harness.github.io/AutoResearch-Hot100"
GROUPS = (
    ("end-to-end", "端到端科研系统", "从想法、实验到稿件的整条科研链。", ("端到端", "AI Scientist", "自主科学", "全模态", "模块化科研", "科研自动化", "开放世界", "论文生产", "论文到科研", "数据到论文")),
    ("method-experiment", "方法发现与自动实验", "假设、实验循环和自动发现。", ("方法发现", "机器学习", "算法发现", "模型架构", "长程", "多模态自主", "科学发现", "自主机器学习")),
    ("deep-research", "深度研究与文献", "检索、证据和长报告。", ("深度研究", "文献", "检索", "综述", "论文检索")),
    ("writing-review", "写作、技能与审稿", "写作技能、审稿数据和辅助系统。", ("写作", "技能", "审稿", "评审")),
    ("benchmarks", "评测与基准", "任务、环境和执行评测。", ("基准", "评测", "复现", "审计", "质量")),
    ("bio-med", "生物医学", "生物医学 Agent 与实验设计。", ("生物", "医学", "单细胞")),
    ("chem-lab", "化学、材料与实验室", "化学工具、材料设计和实验室编排。", ("化学", "材料", "分子", "原子", "实验室", "湿实验", "晶体")),
    ("infra-tools", "基础设施与专用工具", "绘图、工具层、领域执行器和编排底座。", ()),
)
ROMANS = ("II", "III", "IV", "V", "VI", "VII", "VIII", "IX")


def load_projects() -> list[dict]:
    return [json.loads(line) for line in PROJECTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def short_title(level: int, text: str) -> str:
    if level == 2:
        return re.split(r"[：:]", text)[0]
    text = re.split(r"[：:—]", text)[0]
    return re.sub(r"[（(].*?[)）]", "", text).strip()


def build_toc(entries: list[tuple[int, str, str]]) -> str:
    """Render nested headings with each child list inside its parent li."""
    roots: list[list] = []
    stack: list[tuple[int, list]] = []
    for level, heading_id, text in entries:
        if level == 4:
            continue
        node = [level, heading_id, text, []]
        while stack and stack[-1][0] >= level:
            stack.pop()
        (stack[-1][1] if stack else roots).append(node)
        stack.append((level, node[3]))

    def render(nodes: list[list]) -> str:
        lines = ["<ul>"]
        for level, heading_id, text, children in nodes:
            lines.append(f'<li class="l{level}"><a href="#{heading_id}">{html.escape(text)}</a>')
            if children:
                lines.append(render(children))
            lines.append("</li>")
        lines.append("</ul>")
        return "\n".join(lines)

    return render(roots)


def markdown_to_body(markdown: str) -> tuple[str, str, list[tuple[int, str, str]]]:
    mermaids: list[str] = []

    def take_mermaid(match: re.Match[str]) -> str:
        source = "\n".join(
            line for line in match.group(1).splitlines() if not line.strip().startswith("%%{init")
        ).strip("\n")
        mermaids.append(source)
        return f"\n\n@@MERMAID_{len(mermaids) - 1}@@\n\n"

    markdown = re.sub(r"```mermaid[^\n]*\n(.*?)```", take_mermaid, markdown, flags=re.S)
    rendered = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
        input=markdown,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    soup = BeautifulSoup(rendered, "html.parser")
    title = soup.h1.get_text(" ", strip=True) if soup.h1 else "项目架构分析"
    toc: list[tuple[int, str, str]] = []
    for number, heading in enumerate(soup.find_all(["h2", "h3", "h4"]), 1):
        heading_id = f"s{number}"
        heading["id"] = heading_id
        level = int(heading.name[1])
        toc.append((level, heading_id, short_title(level, heading.get_text(" ", strip=True))))
    for quote in soup.find_all("blockquote"):
        text = quote.get_text(" ", strip=True)
        kind = next(((prefix, cls) for prefix, cls in (("📘", "term"), ("🔶", "infer"), ("💬", "opinion"), ("📌", "note")) if text.startswith(prefix)), None)
        if kind:
            quote["class"] = ["callout", kind[1]]
    for paragraph in soup.find_all("p"):
        if len(paragraph.contents) == 1 and getattr(paragraph.contents[0], "name", None) == "em":
            if paragraph.get_text(strip=True).startswith(("图", "表")):
                paragraph["class"] = ["figcap"]
    for table in soup.find_all("table"):
        table.wrap(soup.new_tag("div", attrs={"class": "tbl"}))
    for paragraph in soup.find_all("p"):
        marker = re.fullmatch(r"@@MERMAID_(\d+)@@", paragraph.get_text(strip=True))
        if marker:
            block = soup.new_tag("pre", attrs={"class": "mermaid"})
            block.string = mermaids[int(marker.group(1))]
            paragraph.replace_with(block)
    for heading in soup.find_all("h2"):
        if "名字速查" not in heading.get_text():
            continue
        table = heading.find_next_sibling()
        if table and table.name == "div" and "tbl" in (table.get("class") or []):
            details = soup.new_tag("details")
            summary = soup.new_tag("summary")
            summary.string = "展开本页标识符速查表"
            table.wrap(details)
            details.insert(0, summary)
    return title, str(soup), toc


def render_project(project: dict) -> None:
    source = ROOT / "products" / project["slug"] / "report.md"
    title, body, toc = markdown_to_body(source.read_text(encoding="utf-8"))
    canonical = f'{BASE_URL}/products/{project["slug"]}/'
    description = project["tagline"]
    replacements = {
        "{{TITLE}}": html.escape(title),
        "{{DESCRIPTION}}": html.escape(description, quote=True),
        "{{CANONICAL}}": canonical,
        "{{BRAND}}": "Inside Agentic Science",
        "{{SUB}}": f'{project["repo"]} · {project["snapshot_date"]}',
        "{{HOME}}": f'<a class="home" href="../../groups/{group_slug_for(project)}/">← 返回本章榜单</a>',
        "{{TOC}}": build_toc(toc),
        "{{BODY}}": body,
        "{{MERMAID}}": "../../assets/mermaid.min.js",
    }
    page = PAGE_TEMPLATE.read_text(encoding="utf-8")
    for key, value in replacements.items():
        page = page.replace(key, value)
    output = DIST / "products" / project["slug"] / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")


def format_stars(project: dict) -> str:
    stars = project["stars"]
    if stars is None:
        return "未记录"
    prefix = "约 " if project["stars_approximate"] else ""
    return f"{prefix}{stars:,}"


def clamp(value: float) -> int:
    return max(0, min(25, round(value)))


def score_project(project: dict) -> dict:
    stars = project["stars"] or 0
    community = clamp(math.log10(stars + 1) / math.log10(20001) * 25)
    recency_days = (date.fromisoformat(project["snapshot_date"]) - date.fromisoformat(project["pushed_at"])).days
    recency = clamp(25 * max(0, 1 - recency_days / 540))
    evidence_n = len(json.loads((ROOT / "products" / project["slug"] / "evidence.json").read_text(encoding="utf-8"))["evidence_files"])
    evidence = clamp(evidence_n / 12 * 25)
    report_n = len((ROOT / "products" / project["slug"] / "report.md").read_text(encoding="utf-8"))
    analysis = clamp((report_n - 3000) / 5000 * 25)
    total = community + recency + evidence + analysis
    return {
        "community": community,
        "recency": recency,
        "evidence": evidence,
        "analysis": analysis,
        "total": total,
    }


def group_slug_for(project: dict) -> str:
    category = project["category"]
    for slug, _title, _lead, keys in GROUPS[:-1]:
        if any(key in category for key in keys):
            return slug
    return GROUPS[-1][0]


def grouped_projects(projects: list[dict]) -> dict[str, list[dict]]:
    buckets = {slug: [] for slug, *_ in GROUPS}
    for project in projects:
        project = dict(project)
        project["scores"] = score_project(project)
        buckets[group_slug_for(project)].append(project)
    for slug, items in buckets.items():
        items.sort(key=lambda item: (-item["scores"]["total"], item["featured_order"]))
        buckets[slug] = items[:10]
        if len(buckets[slug]) < 5:
            raise SystemExit(f"group {slug} has only {len(buckets[slug])} ranked projects")
    return buckets


def project_list_items(projects: list[dict], href_prefix: str) -> str:
    items = []
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, project in enumerate(projects, 1):
        scores = project["scores"]
        medal = medals.get(rank, f"{rank:02d}")
        items.append(
            f'<a class="row" href="{href_prefix}{project["slug"]}/">'
            f'<span class="place">{medal}</span>'
            f'<span class="body"><strong>{html.escape(project["name"])}</strong>'
            f'<em>{html.escape(project["tagline"])}</em>'
            f'<small>{html.escape(project["repo"])} · 社区 {scores["community"]} · 活跃 {scores["recency"]} · 证据 {scores["evidence"]} · 分析 {scores["analysis"]}</small></span>'
            f'<span class="score">{scores["total"]}</span></a>'
        )
    return "\n".join(items)


def fill_template(path: Path, replacements: dict[str, str]) -> str:
    template = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def render_series(buckets: dict[str, list[dict]]) -> str:
    books = []
    for number, (roman, (slug, title, lead, _keys)) in enumerate(zip(ROMANS, GROUPS), 2):
        items = buckets[slug]
        top = "、".join(item["name"] for item in items[:3])
        books.append(
            f'<div class="book"><h3>{roman}. {html.escape(title)}</h3><table>'
            f'<tr><td class="num">{number:02d}</td><td class="title"><a href="groups/{slug}/">Top {len(items)}</a></td>'
            f'<td class="insight">{html.escape(lead)} 前列：{html.escape(top)}。</td></tr>'
            "</table></div>"
        )
    return "\n".join(books)


def render_dashboard(projects: list[dict]) -> None:
    buckets = grouped_projects(projects)
    (DIST / "index.html").write_text(
        fill_template(
            DASHBOARD_TEMPLATE,
            {
                "{{COUNT}}": str(len(projects)),
                "{{GROUPS}}": str(len(GROUPS)),
                "{{SNAPSHOT}}": max(project["snapshot_date"] for project in projects),
                "{{SERIES}}": render_series(buckets),
            },
        ),
        encoding="utf-8",
    )
    for roman, (slug, title, lead, _keys) in zip(ROMANS, GROUPS):
        items = buckets[slug]
        dest = DIST / "groups" / slug
        dest.mkdir(parents=True)
        (dest / "index.html").write_text(
            fill_template(
                LIST_TEMPLATE,
                {
                    "{{TITLE}}": html.escape(f"{roman} · {title} Top {len(items)}｜Inside Agentic Science"),
                    "{{DESCRIPTION}}": html.escape(lead, quote=True),
                    "{{CANONICAL}}": f"{BASE_URL}/groups/{slug}/",
                    "{{CRUMB}}": '<a href="../../">Inside Agentic Science</a> / 赛道榜',
                    "{{EYEBROW}}": f"{roman} · Top {len(items)} · 快照 {max(project['snapshot_date'] for project in items)}",
                    "{{HEADING}}": html.escape(title),
                    "{{LEAD}}": html.escape(lead) + " 分数来自社区关注、近期活跃、证据完整度和分析深度，不是运行效果实测。点项目名进入 13 节分析。",
                    "{{ITEMS}}": project_list_items(items, "../../products/"),
                    "{{HOME_HREF}}": "../../",
                },
            ),
            encoding="utf-8",
        )


def write_support_files(projects: list[dict]) -> None:
    shutil.copy2(ROOT / "site" / "assets" / "mermaid.min.js", DIST / "assets" / "mermaid.min.js")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    urls = [
        f"{BASE_URL}/",
        *(f"{BASE_URL}/groups/{slug}/" for slug, *_ in GROUPS),
        *(f'{BASE_URL}/products/{project["slug"]}/' for project in projects),
    ]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def main() -> None:
    projects = [project for project in load_projects() if project["status"] == "published"]
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    render_dashboard(projects)
    for project in projects:
        render_project(project)
    write_support_files(projects)
    print(f"built {len(projects)} project pages in {DIST}")


if __name__ == "__main__":
    main()
