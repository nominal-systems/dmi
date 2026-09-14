#!/usr/bin/env python3
"""Turn a generated PROD release note into a page on the GitHub Pages site.

The workflow (.github/workflows/prod-release-notes.yml) runs this right after
generate.py. It reads the markdown the generator wrote, derives the page
metadata from it, and writes one document into the Jekyll `release_notes`
collection under docs/_release_notes/. The site lists the collection
newest-first on /release-notes/ and renders each document with the
`release-note` layout.

The markdown body is kept verbatim apart from the leading H1, which the layout
renders from the front matter instead. The body is wrapped in
{% raw %} ... {% endraw %} so that a commit title containing Liquid syntax
({{ or {%) cannot break, or be interpreted by, the site build.

Idempotent: the file name is derived from the release slug, so re-running the
workflow for the same release overwrites the same page.

Usage:
    publish_page.py --notes release-notes-w33.md \
                    --release-name w33 \
                    --slug w33 \
                    --site-dir docs \
                    [--date 2026-08-25T21:15:41Z]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

H1_RE = re.compile(r"^# DMI PROD Release Notes - (.+?)\s*$", re.M)
GENERATED_RE = re.compile(r"\bGenerated (\d{4}-\d{2}-\d{2})\.")
TABLE_ROW_RE = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*$")
BUNDLED_RE = re.compile(r"\s*_\(bundled\)_\s*$")


def yaml_str(value: str) -> str:
    # JSON strings are valid YAML double-quoted scalars, so this is a safe way
    # to quote titles that contain colons, quotes or leading symbols.
    return json.dumps(value, ensure_ascii=False)


def parse_versions(markdown: str) -> list[dict]:
    """Read the '## Versions' table into a list of rows for the front matter."""
    rows: list[dict] = []
    in_table = False
    for line in markdown.splitlines():
        if line.strip() == "## Versions":
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("## "):
            break
        match = TABLE_ROW_RE.match(line)
        if not match:
            continue
        service, before, after, state = (m.strip() for m in match.groups())
        if service == "Service" or set(service) <= {"-", " "}:
            continue  # header and separator rows
        bundled = bool(BUNDLED_RE.search(service))
        service = BUNDLED_RE.sub("", service)
        rows.append({
            "service": service,
            "before": before,
            "after": after,
            "state": state.replace("**", ""),
            "bundled": bundled,
        })
    return rows


def excerpt_for(versions: list[dict], generated_on: str) -> str:
    changed = [v for v in versions if v["after"] not in ("unchanged", "-")]
    if not changed:
        return f"PROD release note generated {generated_on}."
    parts = [f"{v['service']} {v['before']} → {v['after']}" for v in changed]
    return f"{len(changed)} service{'s' if len(changed) != 1 else ''} changed: " + ", ".join(parts) + "."


def build_document(markdown: str, release_name: str, slug: str,
                   date: datetime) -> str:
    h1 = H1_RE.search(markdown)
    if not h1:
        sys.exit("publish_page: the notes do not start with the expected "
                 "'# DMI PROD Release Notes - <name>' heading.")

    generated = GENERATED_RE.search(markdown)
    generated_on = generated.group(1) if generated else date.strftime("%Y-%m-%d")

    # Drop the H1 line (and the blank line after it); the layout renders the
    # title from the front matter. Everything else is left exactly as written.
    body = markdown[:h1.start()] + markdown[h1.end():]
    body = body.lstrip("\n")

    versions = parse_versions(markdown)

    lines = [
        "---",
        "layout: release-note",
        f"title: {yaml_str('DMI PROD Release ' + release_name)}",
        f"release_name: {yaml_str(release_name)}",
        f"release_tag: {yaml_str(slug)}",
        f"date: {date.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"generated_on: {generated_on}",
        # A one-line excerpt for the feed and the index. Without it Jekyll
        # would cut the body at the first blank line, inside the raw block.
        f"excerpt: {yaml_str(excerpt_for(versions, generated_on))}",
    ]
    if versions:
        lines.append("versions:")
        for row in versions:
            lines.append(f"  - service: {yaml_str(row['service'])}")
            lines.append(f"    before: {yaml_str(row['before'])}")
            lines.append(f"    after: {yaml_str(row['after'])}")
            lines.append(f"    state: {yaml_str(row['state'])}")
            lines.append(f"    bundled: {'true' if row['bundled'] else 'false'}")
    else:
        lines.append("versions: []")
    lines.append("---")
    lines.append("{% raw %}")
    lines.append(body.rstrip("\n"))
    lines.append("{% endraw %}")
    return "\n".join(lines) + "\n"


def page_name(slug: str) -> str:
    # The page URL is the release slug, lower-cased so /release-notes/w33/ and
    # /release-notes/redis-separation/ read like the rest of the site.
    name = slug.lower()
    name = re.sub(r"[^a-z0-9.-]+", "-", name).strip("-.")
    if not name:
        sys.exit(f"publish_page: slug '{slug}' leaves no usable characters.")
    return name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--notes", required=True, help="Markdown written by generate.py.")
    parser.add_argument("--release-name", required=True, help="Release name as typed, e.g. w33.")
    parser.add_argument("--slug", required=True,
                        help="Release slug as used for the tag and artifact, e.g. Redis-Separation.")
    parser.add_argument("--site-dir", default="docs", help="Jekyll site root (default: docs).")
    parser.add_argument("--date", default="",
                        help="ISO-8601 timestamp used to order the page "
                             "(default: the 'Generated' date in the notes, midnight UTC).")
    args = parser.parse_args()

    with open(args.notes, encoding="utf-8") as handle:
        markdown = handle.read()

    if args.date:
        date = datetime.fromisoformat(args.date.replace("Z", "+00:00"))
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
    else:
        # Default to the date stamped in the notes themselves rather than the
        # clock: a re-run on the same day that changes nothing then produces a
        # byte-identical page and the workflow has nothing to commit.
        generated = GENERATED_RE.search(markdown)
        if generated:
            date = datetime.strptime(generated.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    document = build_document(markdown, args.release_name.strip(), args.slug, date)

    target_dir = os.path.join(args.site_dir, "_release_notes")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, page_name(args.slug) + ".md")

    previous = None
    if os.path.exists(target):
        with open(target, encoding="utf-8") as handle:
            previous = handle.read()
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(document)

    action = "unchanged" if previous == document else ("updated" if previous is not None else "created")
    print(f"{action}: {target}")
    # Exposed for the workflow so it can build the page URL without repeating
    # the slug rules.
    print(f"page_name={page_name(args.slug)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
