#!/usr/bin/env python3
"""
Generate an index page listing all release notes generations.

Scans _site/release-notes/ for date-stamped subdirectories and creates:
  - _site/release-notes/index.html  (listing page)
  - _site/index.html                (redirect to /release-notes/)
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def generate_index(site_dir: Path):
    """Scan for generations and create index pages."""
    rn_dir = site_dir / "release-notes"
    if not rn_dir.exists():
        print("No release-notes directory found")
        return

    # Find all date-stamped generation directories
    generations = []
    for d in sorted(rn_dir.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        # Read data.json for metadata if available
        data_file = d / "data.json"
        meta = {}
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
                meta["generated_at"] = data.get("generated_at", "")
                meta["project_count"] = len(data.get("projects", []))
                meta["total_commits"] = sum(
                    p.get("total_commits", 0) for p in data.get("projects", [])
                )
                meta["projects"] = [
                    {
                        "name": p["display_name"],
                        "baseline": p.get("baseline", ""),
                        "latest": p.get("latest", ""),
                    }
                    for p in data.get("projects", [])
                ]
            except (json.JSONDecodeError, KeyError):
                pass

        generations.append({
            "date": d.name,
            "path": f"{d.name}/",
            **meta,
        })

    if not generations:
        print("No generations found")
        return

    # Build generation cards
    cards_html = ""
    for i, gen in enumerate(generations):
        is_latest = i == 0
        badge = '<span class="badge latest">Latest</span>' if is_latest else ""

        # Format the date nicely
        try:
            date_obj = datetime.strptime(gen["date"], "%Y-%m-%d")
            display_date = date_obj.strftime("%B %d, %Y")
        except ValueError:
            display_date = gen["date"]

        stats = ""
        if gen.get("project_count"):
            stats = f"""
                <div class="gen-stats">
                    <span>{gen['project_count']} projects</span>
                    <span>&middot;</span>
                    <span>{gen['total_commits']} commits</span>
                </div>"""

        projects_preview = ""
        if gen.get("projects"):
            items = "".join(
                f'<span class="project-chip">{p["name"]} <em>{p["baseline"]} → {p["latest"]}</em></span>'
                for p in gen["projects"]
            )
            projects_preview = f'<div class="project-chips">{items}</div>'

        cards_html += f"""
        <a href="{gen['path']}" class="generation-card{' latest-card' if is_latest else ''}">
            <div class="gen-header">
                <h3>{display_date}</h3>
                {badge}
            </div>
            {stats}
            {projects_preview}
        </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMI Release Notes</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --surface-2: #1c2129;
            --border: #30363d;
            --border-accent: #58a6ff44;
            --text: #e6edf3;
            --text-muted: #8b949e;
            --text-dim: #6e7681;
            --accent: #58a6ff;
            --green: #3fb950;
            --radius: 8px;
            --radius-lg: 12px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        .hero {{
            padding: 64px 0 48px;
            text-align: center;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(180deg, #161b2280 0%, transparent 100%);
        }}

        .hero h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
        }}

        .hero .subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
        }}

        .generations {{
            padding: 40px 0 80px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .generation-card {{
            display: block;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            text-decoration: none;
            color: var(--text);
            transition: all 0.15s;
        }}

        .generation-card:hover {{
            border-color: var(--accent);
            transform: translateY(-1px);
        }}

        .latest-card {{
            border-color: var(--border-accent);
        }}

        .gen-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}

        .gen-header h3 {{
            font-size: 1.2rem;
            font-weight: 600;
        }}

        .badge {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 2px 10px;
            border-radius: 20px;
        }}

        .badge.latest {{
            background: #3fb95022;
            color: var(--green);
        }}

        .gen-stats {{
            display: flex;
            gap: 8px;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 12px;
        }}

        .project-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .project-chip {{
            background: var(--surface-2);
            border: 1px solid var(--border);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .project-chip em {{
            font-style: normal;
            color: var(--text-dim);
            font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
            font-size: 0.7rem;
        }}

        .footer {{
            text-align: center;
            padding: 32px 0;
            border-top: 1px solid var(--border);
            color: var(--text-dim);
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <header class="hero">
        <div class="container">
            <h1>DMI Release Notes</h1>
            <p class="subtitle">{len(generations)} generation{"s" if len(generations) != 1 else ""} available</p>
        </div>
    </header>

    <div class="container">
        <div class="generations">
            {cards_html}
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p>Generated by <a href="https://github.com/nominal-systems" style="color: var(--text-muted); text-decoration: none;">Nominal Systems</a> release notes tool</p>
        </div>
    </footer>
</body>
</html>"""

    # Write release-notes index
    index_path = rn_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Written index to {index_path}")

    # Don't write a root redirect — the site root is managed separately (e.g. Jekyll)


def main():
    parser = argparse.ArgumentParser(description="Generate release notes index page")
    parser.add_argument("--site-dir", required=True, help="Path to _site directory")
    args = parser.parse_args()
    generate_index(Path(args.site_dir))


if __name__ == "__main__":
    main()
