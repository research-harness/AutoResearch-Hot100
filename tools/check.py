#!/usr/bin/env python3
"""Validate Atlas source records and, when present, the generated site."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST_INSIDE = ROOT / "dist-inside"
HOT100_BASE = "https://research-harness.github.io/AutoResearch-Hot100"
INSIDE_BASE = "https://research-harness.github.io/Inside-Agentic-Science"
MERMAID_SHA = "07e37dfa97b337ccc85365d57eddf99b9706f09db3b59b260d0333b23b343c4b"
REQUIRED_PROJECT_FIELDS = {
    "schema_version", "slug", "repo", "name", "tagline", "url", "category",
    "layers", "license", "stars", "stars_approximate", "pushed_at",
    "snapshot_date", "analyzed_commit", "status", "review_status", "featured_order",
}
REQUIRED_EVIDENCE_FIELDS = {
    "schema_version", "repo", "url", "analyzed_commit", "snapshot_date",
    "license", "evidence_files", "review_status",
}
ALLOWED_PROJECT_FIELDS = REQUIRED_PROJECT_FIELDS
ALLOWED_STATUS = {"published", "pending", "blocked", "remainder"}
ALLOWED_REVIEW = {"draft", "migrated-reviewed", "independently-reviewed"}
CANDIDATE_FIELDS = {
    "schema_version", "stage", "status", "review_status", "selection_order", "slug",
    "repo", "name", "url", "category", "layers", "selection_reason", "stars",
    "stars_approximate", "pushed_at", "snapshot_date", "default_branch", "analyzed_commit",
    "repository_id", "license_api", "license_text_status", "fork", "archived", "evidence_status",
}
BANNED_TEXT = (
    "/Users/", "/home/", "/private/", "private.env", ".env.local",
    "id_rsa", "id_ed25519", "pool.db", "tickets.db",
)
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".py", ".html", ".yml", ".yaml", ".txt", ""}
EXPECTED_SECTIONS = [
    "它到底是什么", "运行时堆叠", "阶段机或 DAG", "Tool / Skill / Agent 怎么切",
    "文献怎么来、是否入库、引用约束", "实验 / 代码执行", "写稿怎么做", "图怎么做",
    "和 RH 的相似点", "和 RH 的不同点", "优点 / 缺点", "RH 可学的 1–3 条", "名字速查表",
]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(errors, f"{path.relative_to(ROOT)}: expected a JSON object")
        return {}
    return value


def valid_date(value: object) -> bool:
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def load_projects(errors: list[str]) -> list[dict]:
    path = ROOT / "data" / "projects.jsonl"
    projects: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            project = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(errors, f"data/projects.jsonl:{number}: invalid JSON: {exc}")
            continue
        if not isinstance(project, dict):
            fail(errors, f"data/projects.jsonl:{number}: expected an object")
            continue
        missing = REQUIRED_PROJECT_FIELDS - project.keys()
        extra = project.keys() - ALLOWED_PROJECT_FIELDS
        if missing:
            fail(errors, f"data/projects.jsonl:{number}: missing {sorted(missing)}")
        if extra:
            fail(errors, f"data/projects.jsonl:{number}: unknown fields {sorted(extra)}")
        projects.append(project)
    return projects


def load_candidates(errors: list[str]) -> list[dict]:
    path = ROOT / "data" / "candidates-staging.jsonl"
    if not path.is_file():
        fail(errors, "data/candidates-staging.jsonl: missing candidate staging manifest")
        return []
    candidates: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(errors, f"data/candidates-staging.jsonl:{number}: invalid JSON: {exc}")
            continue
        if not isinstance(candidate, dict):
            fail(errors, f"data/candidates-staging.jsonl:{number}: expected an object")
            continue
        missing = CANDIDATE_FIELDS - candidate.keys()
        extra = candidate.keys() - CANDIDATE_FIELDS
        if missing:
            fail(errors, f"data/candidates-staging.jsonl:{number}: missing {sorted(missing)}")
        if extra:
            fail(errors, f"data/candidates-staging.jsonl:{number}: unknown fields {sorted(extra)}")
        candidates.append(candidate)
    return candidates


def check_candidate(candidate: dict, errors: list[str]) -> None:
    repo = str(candidate.get("repo", "<missing>"))
    label = f"candidate {repo}"
    if candidate.get("schema_version") != 1:
        fail(errors, f"{label}: schema_version must be 1")
    if candidate.get("stage") != "candidate-freeze":
        fail(errors, f"{label}: stage must be candidate-freeze")
    if candidate.get("status") != "pending":
        fail(errors, f"{label}: status must be pending")
    if candidate.get("review_status") != "draft":
        fail(errors, f"{label}: review_status must be draft")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(candidate.get("slug", ""))):
        fail(errors, f"{label}: invalid slug")
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
        fail(errors, f"{label}: repo must be owner/name")
    if candidate.get("url") != f"https://github.com/{repo}":
        fail(errors, f"{label}: url must match repo")
    if not isinstance(candidate.get("name"), str) or not candidate["name"].strip():
        fail(errors, f"{label}: name must be non-empty")
    if not isinstance(candidate.get("category"), str) or not candidate["category"].strip():
        fail(errors, f"{label}: category must be non-empty")
    layers = candidate.get("layers")
    if not isinstance(layers, list) or not layers or len(set(layers)) != len(layers) or any(not isinstance(item, str) or not item.strip() for item in layers):
        fail(errors, f"{label}: layers must be a non-empty unique list")
    if not isinstance(candidate.get("selection_reason"), str) or len(candidate["selection_reason"].strip()) < 10:
        fail(errors, f"{label}: selection_reason is too short")
    for field in ("pushed_at", "snapshot_date"):
        if not valid_date(candidate.get(field)):
            fail(errors, f"{label}: {field} must be YYYY-MM-DD")
    if not re.fullmatch(r"[0-9a-f]{40}", str(candidate.get("analyzed_commit", ""))):
        fail(errors, f"{label}: analyzed_commit must be a full SHA")
    if not isinstance(candidate.get("default_branch"), str) or not candidate["default_branch"].strip():
        fail(errors, f"{label}: default_branch must be non-empty")
    if not isinstance(candidate.get("repository_id"), int) or isinstance(candidate.get("repository_id"), bool) or candidate["repository_id"] < 1:
        fail(errors, f"{label}: repository_id must be a positive integer")
    if candidate.get("stars") is not None and (not isinstance(candidate["stars"], int) or isinstance(candidate["stars"], bool) or candidate["stars"] < 0):
        fail(errors, f"{label}: stars must be a non-negative integer or null")
    if not isinstance(candidate.get("stars_approximate"), bool):
        fail(errors, f"{label}: stars_approximate must be boolean")
    if not isinstance(candidate.get("license_api"), str) or not candidate["license_api"].strip():
        fail(errors, f"{label}: license_api must record an API value or NOASSERTION")
    if not isinstance(candidate.get("license_text_status"), str) or not candidate["license_text_status"].strip():
        fail(errors, f"{label}: license_text_status must be explicit")
    if candidate.get("fork") is not False or candidate.get("archived") is not False:
        fail(errors, f"{label}: frozen candidates must not be forks or archived")
    if not isinstance(candidate.get("evidence_status"), str) or not candidate["evidence_status"].strip():
        fail(errors, f"{label}: evidence_status must be explicit")
    if not isinstance(candidate.get("selection_order"), int) or isinstance(candidate.get("selection_order"), bool):
        fail(errors, f"{label}: selection_order must be an integer")


def check_candidates(candidates: list[dict], projects: list[dict], errors: list[str]) -> None:
    published_count = sum(project.get("status") == "published" for project in projects)
    if not candidates:
        if published_count != 100:
            fail(errors, f"candidate staging is empty but published count is {published_count}, expected 100")
        return
    if len(candidates) != 80:
        fail(errors, f"candidate staging: expected 80 records, found {len(candidates)}")
    orders = [candidate.get("selection_order") for candidate in candidates]
    if orders != list(range(21, 101)):
        fail(errors, "candidate staging: selection_order must be the exact 21-100 sequence")
    for field in ("slug", "repo", "url", "selection_order", "repository_id"):
        values = [candidate.get(field) for candidate in candidates]
        duplicates = sorted({str(value) for value in values if values.count(value) > 1})
        if duplicates:
            fail(errors, f"duplicate candidate {field}: {duplicates}")
    published_repos = {str(project.get("repo")) for project in projects}
    overlap = sorted(published_repos.intersection(str(candidate.get("repo")) for candidate in candidates))
    if overlap:
        fail(errors, f"candidate staging overlaps published projects: {overlap}")


def check_staged_reports(candidates: list[dict], errors: list[str]) -> None:
    for candidate in candidates:
        slug = str(candidate.get("slug", "<missing>"))
        label = f"staged candidate {slug}"
        directory = ROOT / "products" / slug
        report_path = directory / "report.md"
        evidence_path = directory / "evidence.json"
        present = [path.is_file() for path in (report_path, evidence_path)]
        if not any(present):
            continue
        if not all(present):
            fail(errors, f"{label}: report.md and evidence.json must arrive together")
            continue
        report = report_path.read_text(encoding="utf-8")
        headings = re.findall(r"^##\s+\d+\.\s+(.+?)\s*$", report, flags=re.M)
        if headings != EXPECTED_SECTIONS:
            fail(errors, f"{label}: expected the canonical 13 sections in order, got {headings}")
        if report.count("```mermaid") < 1:
            fail(errors, f"{label}: report needs at least one Mermaid diagram")
        if "📌" not in report or "事实边界" not in report:
            fail(errors, f"{label}: report needs a 📌事实边界 callout")
        for marker in ("📘", "🔶", "💬"):
            if marker not in report:
                fail(errors, f"{label}: report needs the {marker} evidence-boundary marker")
        if len(report) < 3000:
            fail(errors, f"{label}: report is too short for a full analysis ({len(report)} characters)")
        evidence = read_json(evidence_path, errors)
        missing = REQUIRED_EVIDENCE_FIELDS - evidence.keys()
        if missing:
            fail(errors, f"{label}: evidence.json missing {sorted(missing)}")
        for field in ("repo", "url", "analyzed_commit", "snapshot_date"):
            if evidence.get(field) != candidate.get(field):
                fail(errors, f"{label}: evidence {field} does not match candidates-staging.jsonl")
        if evidence.get("review_status") != "draft":
            fail(errors, f"{label}: staged evidence review_status must be draft")
        files = evidence.get("evidence_files")
        if not isinstance(files, list) or len(files) < 3 or any(not isinstance(item, str) or not item or item.startswith(("/", "../")) for item in files):
            fail(errors, f"{label}: evidence_files must contain at least three safe relative paths")
        elif len(files) != len(set(files)):
            fail(errors, f"{label}: evidence_files contains duplicates")


def check_project(project: dict, errors: list[str]) -> None:
    slug = project.get("slug", "<missing>")
    label = f"project {slug}"
    if project.get("schema_version") != 1:
        fail(errors, f"{label}: schema_version must be 1")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(slug)):
        fail(errors, f"{label}: invalid slug")
    repo = str(project.get("repo", ""))
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
        fail(errors, f"{label}: repo must be owner/name")
    if project.get("url") != f"https://github.com/{repo}":
        fail(errors, f"{label}: url must match repo")
    if not re.fullmatch(r"[0-9a-f]{40}", str(project.get("analyzed_commit", ""))):
        fail(errors, f"{label}: analyzed_commit must be a full SHA")
    for field in ("pushed_at", "snapshot_date"):
        if not valid_date(project.get(field)):
            fail(errors, f"{label}: {field} must be YYYY-MM-DD")
    if project.get("status") not in ALLOWED_STATUS:
        fail(errors, f"{label}: invalid status")
    if project.get("review_status") not in ALLOWED_REVIEW:
        fail(errors, f"{label}: invalid review_status")
    if not isinstance(project.get("layers"), list) or not project.get("layers") or len(set(project.get("layers", []))) != len(project.get("layers", [])):
        fail(errors, f"{label}: layers must be a non-empty unique list")
    if project.get("stars") is not None and (not isinstance(project.get("stars"), int) or project["stars"] < 0):
        fail(errors, f"{label}: stars must be a non-negative integer or null")
    if not isinstance(project.get("stars_approximate"), bool):
        fail(errors, f"{label}: stars_approximate must be boolean")
    if not isinstance(project.get("featured_order"), int) or project["featured_order"] < 1:
        fail(errors, f"{label}: featured_order must be a positive integer")

    directory = ROOT / "products" / str(slug)
    report_path = directory / "report.md"
    evidence_path = directory / "evidence.json"
    if project.get("status") != "published":
        return
    if not report_path.is_file():
        fail(errors, f"{label}: missing products/{slug}/report.md")
        return
    if not evidence_path.is_file():
        fail(errors, f"{label}: missing products/{slug}/evidence.json")
        return
    report = report_path.read_text(encoding="utf-8")
    headings = re.findall(r"^##\s+\d+\.\s+(.+?)\s*$", report, flags=re.M)
    if headings != EXPECTED_SECTIONS:
        fail(errors, f"{label}: expected the canonical 13 sections in order, got {headings}")
    if report.count("```mermaid") < 1:
        fail(errors, f"{label}: report needs at least one Mermaid diagram")
    if "📌" not in report or "事实边界" not in report:
        fail(errors, f"{label}: report needs a 📌事实边界 callout")
    if len(report) < 3000:
        fail(errors, f"{label}: report is too short for a full analysis ({len(report)} characters)")

    evidence = read_json(evidence_path, errors)
    missing = REQUIRED_EVIDENCE_FIELDS - evidence.keys()
    if missing:
        fail(errors, f"{label}: evidence.json missing {sorted(missing)}")
    for field in ("repo", "url", "analyzed_commit", "snapshot_date", "license", "review_status"):
        if evidence.get(field) != project.get(field):
            fail(errors, f"{label}: evidence {field} does not match projects.jsonl")
    files = evidence.get("evidence_files")
    if not isinstance(files, list) or len(files) < 3 or any(not isinstance(item, str) or not item or item.startswith(("/", "../")) for item in files):
        fail(errors, f"{label}: evidence_files must contain at least three safe relative paths")
    elif len(files) != len(set(files)):
        fail(errors, f"{label}: evidence_files contains duplicates")


def check_uniqueness(projects: list[dict], candidates: list[dict], errors: list[str]) -> None:
    for field in ("slug", "repo", "url", "featured_order"):
        values = [project.get(field) for project in projects]
        duplicates = sorted({str(value) for value in values if values.count(value) > 1})
        if duplicates:
            fail(errors, f"duplicate {field}: {duplicates}")
    directories = {
        path.name for path in (ROOT / "products").iterdir()
        if path.is_dir() and any(path.iterdir())
    }
    published = {str(project.get("slug")) for project in projects if project.get("status") == "published"}
    staged = {str(candidate.get("slug")) for candidate in candidates}
    unexpected = directories - published - staged
    if unexpected or published - directories:
        fail(errors, f"product directories and published manifest differ: only dirs={sorted(unexpected)}, only manifest={sorted(published-directories)}")


def check_active_markup(text: str, label: str, errors: list[str]) -> None:
    soup = BeautifulSoup(text, "html.parser")
    dangerous_tags = {"script", "iframe", "object", "embed", "form", "base"}
    for tag in soup.find_all(dangerous_tags):
        fail(errors, f"{label}: active HTML tag <{tag.name}> is not allowed")
    for tag in soup.find_all(True):
        for attr, value in tag.attrs.items():
            if attr.lower().startswith("on"):
                fail(errors, f"{label}: event handler attribute {attr!r} is not allowed")
            if attr.lower() in {"href", "src", "action", "formaction"}:
                raw = str(value).strip().lower()
                if raw.startswith(("javascript:", "vbscript:", "data:")):
                    fail(errors, f"{label}: unsafe URL scheme in {attr!r}")


def check_public_hygiene(errors: list[str]) -> None:
    roots = [ROOT / "data", ROOT / "products", ROOT / "site", ROOT / "tools", ROOT / ".github"]
    candidates = [ROOT / "README.md", ROOT / "CONTENT-LICENSE.md", ROOT / "LICENSE"]
    for directory in roots:
        if directory.exists():
            candidates.extend(path for path in directory.rglob("*") if path.is_file() and path.suffix in TEXT_SUFFIXES and "assets" not in path.parts)
    candidates.remove(Path(__file__))
    secret_assignment = re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{16,}")
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for banned in BANNED_TEXT:
            if banned in text:
                fail(errors, f"{path.relative_to(ROOT)}: contains banned public text {banned!r}")
        if secret_assignment.search(text):
            fail(errors, f"{path.relative_to(ROOT)}: resembles a committed credential")
        if path.suffix == ".md":
            check_active_markup(text, str(path.relative_to(ROOT)), errors)


def local_target(page: Path, raw_url: str, root: Path = DIST) -> tuple[Path, str] | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc or raw_url.startswith(("mailto:", "javascript:", "data:")):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        target = page
    elif path_text.startswith("/"):
        target = root / path_text.lstrip("/")
    else:
        target = page.parent / path_text
    if path_text.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve(), parsed.fragment


def check_mermaid_asset(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        fail(errors, f"{path.relative_to(ROOT)}: missing local Mermaid asset")
        return
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != MERMAID_SHA:
        fail(errors, f"{path.relative_to(ROOT)}: unexpected Mermaid asset SHA-256 {digest}")


def scan_pages(root: Path, pages: list[Path], canonical_prefix: str, errors: list[str]) -> None:
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for banned in BANNED_TEXT:
            if banned in text:
                fail(errors, f"{page.relative_to(ROOT)}: generated page contains banned public text {banned!r}")
        if re.search(r"{{[A-Z_]+}}", text):
            fail(errors, f"{page.relative_to(ROOT)}: unresolved template marker")
        soup = BeautifulSoup(text, "html.parser")
        ids = {tag.get("id") for tag in soup.find_all(id=True)}
        for node in soup.select("main script, main iframe, main object, main embed, main form, main base"):
            fail(errors, f"{page.relative_to(ROOT)}: active content <{node.name}> found in report body")
        for node in soup.select("main *"):
            for attribute, value in node.attrs.items():
                if attribute.lower().startswith("on"):
                    fail(errors, f"{page.relative_to(ROOT)}: report body contains event handler {attribute!r}")
                if attribute.lower() in {"href", "src", "action", "formaction"} and str(value).strip().lower().startswith(("javascript:", "vbscript:", "data:")):
                    fail(errors, f"{page.relative_to(ROOT)}: report body contains unsafe URL scheme")
        for nested in soup.select("nav.side ul ul"):
            if not nested.parent or nested.parent.name != "li":
                fail(errors, f"{page.relative_to(ROOT)}: nested TOC list is not inside its parent li")
        canonical = soup.find("link", rel="canonical")
        if not canonical or not str(canonical.get("href", "")).startswith(canonical_prefix):
            fail(errors, f"{page.relative_to(ROOT)}: missing canonical URL")
        for tag, attribute in (("a", "href"), ("script", "src"), ("link", "href"), ("img", "src")):
            for node in soup.find_all(tag):
                raw = node.get(attribute)
                if not raw:
                    continue
                resolved = local_target(page, str(raw), root)
                if not resolved:
                    continue
                target, fragment = resolved
                if not target.is_file():
                    fail(errors, f"{page.relative_to(ROOT)}: broken local link {raw}")
                    continue
                if fragment:
                    target_soup = soup if target == page.resolve() else BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser")
                    target_ids = ids if target == page.resolve() else {item.get("id") for item in target_soup.find_all(id=True)}
                    if fragment not in target_ids:
                        fail(errors, f"{page.relative_to(ROOT)}: missing anchor {raw}")


def check_dist(projects: list[dict], errors: list[str]) -> None:
    if not DIST.exists():
        return
    from inside import CHAPTERS

    pages = sorted(DIST.rglob("*.html"))
    group_pages = list((DIST / "groups").glob("*/index.html")) if (DIST / "groups").exists() else []
    inside_pages = list((DIST / "inside").rglob("index.html")) if (DIST / "inside").exists() else []
    expected = 1 + len(group_pages) + len(inside_pages) + sum(project.get("status") == "published" for project in projects)
    if len(group_pages) < 2:
        fail(errors, "dist: expected category index pages under groups/")
    if len(inside_pages) != 1 + len(CHAPTERS):
        fail(errors, f"dist: expected {1 + len(CHAPTERS)} Inside redirect pages under inside/")
    for page in inside_pages:
        text = page.read_text(encoding="utf-8")
        if INSIDE_BASE not in text:
            fail(errors, f"{page.relative_to(ROOT)}: Hot 100 /inside/ must redirect to Inside Agentic Science")
        if "开源实现：仓库里的这个模块" in text or "ais-workflow.png" in text:
            fail(errors, f"{page.relative_to(ROOT)}: Hot 100 /inside/ still hosts the series")
    if len(pages) != expected:
        fail(errors, f"dist: expected {expected} HTML pages, found {len(pages)}")
    check_mermaid_asset(DIST / "assets" / "mermaid.min.js", errors)
    hot_pages = [page for page in pages if page.relative_to(DIST).parts[0] != "inside"]
    redir_pages = [page for page in pages if page.relative_to(DIST).parts[0] == "inside"]
    scan_pages(DIST, hot_pages, f"{HOT100_BASE}/", errors)
    scan_pages(DIST, redir_pages, f"{INSIDE_BASE}/", errors)
    check_inside_site(errors)


def check_inside_site(errors: list[str]) -> None:
    if not DIST_INSIDE.exists():
        fail(errors, "dist-inside: missing Inside Agentic Science site")
        return
    from inside import CHAPTERS

    pages = sorted(DIST_INSIDE.rglob("*.html"))
    home = DIST_INSIDE / "index.html"
    if not home.is_file():
        fail(errors, "dist-inside: missing homepage")
        return
    text = home.read_text(encoding="utf-8")
    if "怎么读" in text:
        fail(errors, "dist-inside/index.html: homepage still contains 怎么读")
    if "ais-workflow.png" not in text:
        fail(errors, "dist-inside/index.html: homepage needs the workflow figure")
    if "zhice" in text.lower() or "执策" in text:
        fail(errors, "dist-inside/index.html: Inside page must not mention zhice")
    expected = 1 + len(CHAPTERS)
    if len(pages) != expected:
        fail(errors, f"dist-inside: expected {expected} HTML pages, found {len(pages)}")
    for chapter in CHAPTERS:
        page = DIST_INSIDE / chapter["slug"] / "index.html"
        if not page.is_file():
            fail(errors, f"dist-inside/{chapter['slug']}/index.html: missing chapter")
            continue
        body = page.read_text(encoding="utf-8")
        if "开源实现：仓库里的这个模块" not in body:
            fail(errors, f"{page.relative_to(ROOT)}: chapter is missing the per-chapter implementation table")
        if "https://github.com/" not in body or "/blob/" not in body:
            fail(errors, f"{page.relative_to(ROOT)}: chapter table needs in-repo blob paths")
        if "zhice" in body.lower() or "执策" in body:
            fail(errors, f"{page.relative_to(ROOT)}: Inside page must not mention zhice")
        if re.search(r"优：优点(?:<|（|（源码)|缺：缺点(?:<|是)?", body):
            fail(errors, f"{page.relative_to(ROOT)}: implementation verdict still contains section headings")
    check_mermaid_asset(DIST_INSIDE / "assets" / "mermaid.min.js", errors)
    if not (DIST_INSIDE / "assets" / "ais-workflow.png").is_file():
        fail(errors, "dist-inside: missing homepage workflow figure")
    scan_pages(DIST_INSIDE, pages, f"{INSIDE_BASE}/", errors)


def main() -> int:
    errors: list[str] = []
    projects = load_projects(errors)
    candidates = load_candidates(errors)
    for project in projects:
        check_project(project, errors)
    for candidate in candidates:
        check_candidate(candidate, errors)
    check_candidates(candidates, projects, errors)
    check_staged_reports(candidates, errors)
    check_uniqueness(projects, candidates, errors)
    check_public_hygiene(errors)
    check_dist(projects, errors)
    if errors:
        print("Atlas validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    published = sum(project.get("status") == "published" for project in projects)
    print(f"Atlas validation passed: {published} published projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
