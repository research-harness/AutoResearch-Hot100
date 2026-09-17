#!/usr/bin/env python3
"""Build the static Automated Science Atlas into dist/."""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PROJECTS = ROOT / "data" / "projects.jsonl"
PAGE_TEMPLATE = ROOT / "site" / "template.html"
DASHBOARD_TEMPLATE = ROOT / "site" / "dashboard-template.html"
BASE_URL = "https://atlas.zhice.io"


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
        "{{BRAND}}": "AutoResearch Hot 100",
        "{{SUB}}": f'{project["repo"]} · {project["snapshot_date"]}',
        "{{HOME}}": '<a class="home" href="../../">← 返回项目总览</a>',
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


def render_dashboard(projects: list[dict]) -> None:
    categories = sorted({project["category"] for project in projects})
    layers = sorted({layer for project in projects for layer in project["layers"]})
    cards: list[str] = []
    for project in sorted(projects, key=lambda item: item["featured_order"]):
        tags = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in [project["category"], *project["layers"]])
        report_text = (ROOT / "products" / project["slug"] / "report.md").read_text(encoding="utf-8")
        searchable = " ".join([project["name"], project["repo"], project["tagline"], project["category"], *project["layers"], report_text]).lower()
        cards.append(
            f'<article class="card" data-order="{project["featured_order"]}" data-name="{html.escape(project["name"], quote=True)}" '
            f'data-category="{html.escape(project["category"], quote=True)}" data-layers="{html.escape("|".join(project["layers"]), quote=True)}" '
            f'data-stars="{project["stars"] if project["stars"] is not None else -1}" data-updated="{project["pushed_at"]}" '
            f'data-search="{html.escape(searchable, quote=True)}">'
            f'<span class="rank">#{project["featured_order"]} · {html.escape(project["repo"])}</span>'
            f'<h2><a href="products/{project["slug"]}/">{html.escape(project["name"])}</a></h2>'
            f'<p>{html.escape(project["tagline"])}</p><div class="tags">{tags}</div>'
            f'<div class="meta">Stars：{format_stars(project)} · 最近 push：{project["pushed_at"]}<br>'
            f'分析 commit：<a href="{project["url"]}/tree/{project["analyzed_commit"]}">{project["analyzed_commit"][:7]}</a> · '
            f'<a href="{project["url"]}">上游仓库</a></div></article>'
        )
    template = DASHBOARD_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{COUNT}}": str(len(projects)),
        "{{CATEGORIES}}": str(len(categories)),
        "{{SNAPSHOT}}": max(project["snapshot_date"] for project in projects),
        "{{CATEGORY_OPTIONS}}": "".join(f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>' for value in categories),
        "{{LAYER_OPTIONS}}": "".join(f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>' for value in layers),
        "{{CARDS}}": "\n".join(cards),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    (DIST / "index.html").write_text(template, encoding="utf-8")


def write_support_files(projects: list[dict]) -> None:
    shutil.copy2(ROOT / "site" / "assets" / "mermaid.min.js", DIST / "assets" / "mermaid.min.js")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    urls = [f"{BASE_URL}/", *(f'{BASE_URL}/products/{project["slug"]}/' for project in projects)]
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
