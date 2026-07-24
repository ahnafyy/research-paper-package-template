#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ORCID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default or ""


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    title = _require_text(data, "title")
    subtitle = _require_text(data, "subtitle")
    slug = _require_text(data, "slug")
    abstract = _require_text(data, "abstract")
    author = _require_text(data, "author")
    affiliation = _require_text(data, "affiliation")
    repository = _require_text(data, "repository")
    site = _require_text(data, "site")
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("slug must contain lowercase words separated by single hyphens")
    if not _valid_url(repository) or not _valid_url(site):
        raise ValueError("repository and site must be absolute https URLs")
    orcid = data.get("orcid")
    if orcid is not None and (not isinstance(orcid, str) or not ORCID_PATTERN.fullmatch(orcid)):
        raise ValueError("orcid must use the form 0000-0000-0000-000X")
    keywords = data.get("keywords", [])
    categories = data.get("arxiv_categories", ["cs.AI"])
    if (
        not isinstance(keywords, list)
        or not keywords
        or not all(isinstance(value, str) for value in keywords)
    ):
        raise ValueError("keywords must be a non-empty list of strings")
    if not isinstance(categories, list) or not categories or not all(
        isinstance(v, str) for v in categories
    ):
        raise ValueError("arxiv_categories must be a non-empty list of strings")
    seed = data.get("random_seed", 20260723)
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("random_seed must be an integer")
    return {
        "title": title,
        "subtitle": subtitle,
        "slug": slug,
        "abstract": abstract,
        "author": author,
        "orcid": orcid,
        "affiliation": affiliation,
        "repository": repository,
        "site": site,
        "keywords": keywords,
        "arxiv_categories": categories,
        "random_seed": seed,
        "code_license": str(data.get("code_license", "MIT")),
        "content_license": str(data.get("content_license", "CC-BY-4.0")),
    }


def _quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _render(data: dict[str, Any]) -> str:
    orcid = "null" if data["orcid"] is None else _quoted(data["orcid"])
    keyword_lines = "\n".join(f"    - {_quoted(value)}" for value in data["keywords"])
    category_lines = "\n".join(
        f"    - {_quoted(value)}" for value in data["arxiv_categories"]
    )
    return f"""schema_version: 1
initialized: true
project:
  title: {_quoted(data['title'])}
  subtitle: {_quoted(data['subtitle'])}
  slug: {_quoted(data['slug'])}
  abstract: {_quoted(data['abstract'])}
  keywords:
{keyword_lines}
  arxiv_categories:
{category_lines}
authors:
  - name: {_quoted(data['author'])}
    orcid: {orcid}
    affiliations:
      - {_quoted(data['affiliation'])}
links:
  repository: {_quoted(data['repository'])}
  site: {_quoted(data['site'])}
research:
  random_seed: {data['random_seed']}
licenses:
  code: {_quoted(data['code_license'])}
  content: {_quoted(data['content_license'])}
"""


def _interactive_values() -> dict[str, Any]:
    return {
        "title": _ask("Paper title"),
        "subtitle": _ask("One-sentence contribution"),
        "slug": _ask("Project slug"),
        "abstract": _ask("Initial abstract"),
        "author": _ask("Author name"),
        "orcid": _ask("ORCID (optional)") or None,
        "affiliation": _ask("Affiliation"),
        "repository": _ask("Repository URL"),
        "site": _ask("Site URL"),
        "keywords": [value.strip() for value in _ask("Keywords, comma separated").split(",")],
        "arxiv_categories": [
            value.strip() for value in _ask("arXiv categories, comma separated", "cs.AI").split(",")
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a paper-ospackage project")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, help="JSON file containing initialization values")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.non_interactive and args.config is None:
        parser.error("--non-interactive requires --config")
    if args.config:
        try:
            values = json.loads(args.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Initialization config is unreadable: {error}", file=sys.stderr)
            return 2
        if not isinstance(values, dict):
            print("Initialization config must be a JSON object", file=sys.stderr)
            return 2
    else:
        values = _interactive_values()

    try:
        rendered = _render(_normalize(values))
    except ValueError as error:
        print(f"Invalid initialization values: {error}", file=sys.stderr)
        return 2

    destination = args.root.resolve() / "project.yml"
    if destination.exists():
        current = destination.read_text(encoding="utf-8")
        if current == rendered:
            print(f"Already initialized: {destination}")
            return 0
        if "initialized: true" in current and not args.force:
            print(
                "Project is already initialized; pass --force to replace metadata.",
                file=sys.stderr,
            )
            return 2
    destination.write_text(rendered, encoding="utf-8")
    print(f"Initialized project metadata in {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
