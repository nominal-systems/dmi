#!/usr/bin/env python3
"""
Generate release notes HTML page from git history across multiple repositories.

Usage:
    python3 generate-html.py [--config CONFIG] [--output OUTPUT_DIR] [--serve]

The script reads baseline versions from config.json, collects git log data
between baseline tags and the latest tag for each project, categorizes commits,
and generates a static HTML page suitable for GitHub Pages.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "config.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "site"

# Conventional commit type mappings
COMMIT_CATEGORIES = {
    "feat": {"label": "Features", "icon": "rocket", "order": 1},
    "fix": {"label": "Bug Fixes", "icon": "bug", "order": 2},
    "perf": {"label": "Performance", "icon": "zap", "order": 3},
    "refactor": {"label": "Refactoring", "icon": "recycle", "order": 4},
    "chore": {"label": "Maintenance", "icon": "wrench", "order": 5},
    "docs": {"label": "Documentation", "icon": "book", "order": 6},
    "test": {"label": "Tests", "icon": "test-tube", "order": 7},
    "ci": {"label": "CI/CD", "icon": "settings", "order": 8},
    "style": {"label": "Style", "icon": "palette", "order": 9},
    "build": {"label": "Build", "icon": "package", "order": 10},
    "other": {"label": "Other Changes", "icon": "git-commit", "order": 99},
}

# Patterns to skip (version bumps, merge commits)
SKIP_PATTERNS = [
    r"^\d+\.\d+\.\d+",                     # Version-only commits like "1.4.5"
    r"^Merge branch",                        # Merge commits
    r"^Merge pull request",                  # PR merges
    r"^Merge remote-tracking",               # Remote merges
]


def run_git(repo_path, *args):
    """Run a git command in the given repo and return stdout."""
    cmd = ["git", "-C", str(repo_path)] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"  Warning: git command failed in {repo_path}: {' '.join(args)}", file=sys.stderr)
        print(f"  stderr: {e.stderr.strip()}", file=sys.stderr)
        return ""


def get_latest_stable_tag(repo_path):
    """Get the latest stable (non-prerelease) tag, sorted by version."""
    tags = run_git(repo_path, "tag", "-l", "--sort=-v:refname")
    if not tags:
        return None
    for tag in tags.splitlines():
        tag = tag.strip()
        # Skip prereleases (e.g., v2.0.0-0)
        if re.search(r"-\d+$", tag) or "-alpha" in tag or "-beta" in tag or "-rc" in tag:
            continue
        return tag
    return tags.splitlines()[0].strip()


def get_tag_date(repo_path, tag):
    """Get the date of a tag."""
    date_str = run_git(repo_path, "log", "-1", "--format=%aI", tag)
    if date_str:
        return datetime.fromisoformat(date_str)
    return None


def get_commits_between(repo_path, from_ref, to_ref):
    """Get commits between two refs with hash, date, and message."""
    if from_ref:
        range_spec = f"{from_ref}..{to_ref}"
    else:
        range_spec = to_ref

    log = run_git(repo_path, "log", "--format=%H|%aI|%s", range_spec)
    if not log:
        return []

    commits = []
    for line in log.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        sha, date_str, message = parts
        commits.append({
            "sha": sha,
            "short_sha": sha[:7],
            "date": date_str,
            "message": message,
        })
    return commits


def categorize_commit(message):
    """Parse a conventional commit message and return (category, scope, description)."""
    # Check skip patterns
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, message, re.IGNORECASE):
            return None, None, None

    # Conventional commit: type(scope): description
    m = re.match(r"^(\w+?)(?:\(([^)]*)\))?:\s*(.+)$", message)
    if m:
        ctype = m.group(1).lower()
        scope = m.group(2)
        desc = m.group(3)
        if ctype in COMMIT_CATEGORIES:
            return ctype, scope, desc
        return "other", scope, desc

    # Non-conventional: categorize by keywords
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["add ", "added ", "implement", "new ", "support "]):
        return "feat", None, message
    elif any(w in msg_lower for w in ["fix ", "fixed ", "resolve", "patch"]):
        return "fix", None, message
    elif any(w in msg_lower for w in ["refactor", "rename", "restructure", "simplify"]):
        return "refactor", None, message
    elif any(w in msg_lower for w in ["improve", "optimi", "enhance", "upgrade"]):
        return "perf", None, message
    else:
        return "other", None, message


def collect_github_issues(repo_path, github_org, repo_name, from_ref, to_ref):
    """Extract GitHub issue references from commits between two refs."""
    commits = get_commits_between(repo_path, from_ref, to_ref)
    issues = set()
    for c in commits:
        # Match #123 patterns in commit messages
        refs = re.findall(r"#(\d+)", c["message"])
        for ref in refs:
            issues.add(int(ref))
    return sorted(issues)


def collect_project_data(project, workspace_root, github_org):
    """Collect all release notes data for a single project."""
    repo_path = workspace_root / project["directory"]
    if not (repo_path / ".git").exists():
        print(f"  Skipping {project['name']}: not a git repo at {repo_path}", file=sys.stderr)
        return None

    baseline = project.get("baseline")
    latest = get_latest_stable_tag(repo_path)

    if not latest:
        print(f"  Skipping {project['name']}: no tags found", file=sys.stderr)
        return None

    # If baseline equals latest, no changes
    if baseline and baseline == latest:
        print(f"  {project['name']}: no changes (baseline = latest = {baseline})", file=sys.stderr)
        return None

    # Verify baseline tag exists
    if baseline:
        check = run_git(repo_path, "rev-parse", "--verify", f"refs/tags/{baseline}")
        if not check:
            print(f"  Warning: baseline tag {baseline} not found in {project['name']}", file=sys.stderr)
            return None

    print(f"  {project['name']}: {baseline or '(beginning)'} -> {latest}", file=sys.stderr)

    commits = get_commits_between(repo_path, baseline, latest)
    baseline_date = get_tag_date(repo_path, baseline) if baseline else None
    latest_date = get_tag_date(repo_path, latest)

    # Categorize commits
    categorized = defaultdict(list)
    for commit in commits:
        cat, scope, desc = categorize_commit(commit["message"])
        if cat is None:
            continue  # Skipped (version bump, merge, etc.)
        entry = {
            "sha": commit["short_sha"],
            "full_sha": commit["sha"],
            "date": commit["date"],
            "scope": scope,
            "description": desc or commit["message"],
            "original_message": commit["message"],
        }
        categorized[cat].append(entry)

    # Collect referenced issues
    issues = collect_github_issues(repo_path, github_org, project["name"], baseline, latest)

    # Get intermediate version tags
    if baseline:
        tags_str = run_git(repo_path, "tag", "-l", "--sort=v:refname", "--merged", latest)
    else:
        tags_str = run_git(repo_path, "tag", "-l", "--sort=v:refname")
    all_tags = [t.strip() for t in tags_str.splitlines() if t.strip()]
    intermediate_versions = []
    past_baseline = baseline is None
    for tag in all_tags:
        if not past_baseline:
            if tag == baseline:
                past_baseline = True
            continue
        if tag == latest or re.search(r"-\d+$", tag) or "-alpha" in tag or "-beta" in tag:
            continue
        tag_date = get_tag_date(repo_path, tag)
        intermediate_versions.append({
            "tag": tag,
            "date": tag_date.isoformat() if tag_date else None,
        })
    intermediate_versions.append({
        "tag": latest,
        "date": latest_date.isoformat() if latest_date else None,
    })

    return {
        "name": project["name"],
        "display_name": project["display_name"],
        "description": project["description"],
        "baseline": baseline,
        "latest": latest,
        "baseline_date": baseline_date.isoformat() if baseline_date else None,
        "latest_date": latest_date.isoformat() if latest_date else None,
        "total_commits": len(commits),
        "categorized": dict(categorized),
        "issues": issues,
        "versions": intermediate_versions,
        "github_url": f"https://github.com/{github_org}/{project['name']}",
    }


def generate_html(data, config):
    """Generate the release notes HTML page."""
    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")

    # Count totals
    total_commits = sum(p["total_commits"] for p in data)
    total_features = sum(len(p["categorized"].get("feat", [])) for p in data)
    total_fixes = sum(len(p["categorized"].get("fix", [])) for p in data)
    total_projects = len(data)

    # Build project sections
    project_sections = []
    for proj in data:
        categories_html = []
        # Sort categories by order
        sorted_cats = sorted(
            proj["categorized"].items(),
            key=lambda x: COMMIT_CATEGORIES.get(x[0], {}).get("order", 99)
        )
        for cat, entries in sorted_cats:
            cat_info = COMMIT_CATEGORIES.get(cat, COMMIT_CATEGORIES["other"])
            items_html = ""
            for entry in entries:
                scope_badge = ""
                if entry["scope"]:
                    scope_badge = f'<span class="scope">{entry["scope"]}</span>'
                items_html += f"""
                    <li>
                        <a href="{proj['github_url']}/commit/{entry['full_sha']}" class="sha" target="_blank">{entry['sha']}</a>
                        {scope_badge}
                        <span class="commit-desc">{_escape(entry['description'])}</span>
                    </li>"""

            categories_html.append(f"""
                <div class="category">
                    <h4 class="category-title">
                        <span class="category-icon" data-icon="{cat_info['icon']}"></span>
                        {cat_info['label']}
                        <span class="count">{len(entries)}</span>
                    </h4>
                    <ul class="commit-list">{items_html}
                    </ul>
                </div>""")

        # Issues section
        issues_html = ""
        if proj["issues"]:
            issue_links = ", ".join(
                f'<a href="{proj["github_url"]}/issues/{i}" target="_blank">#{i}</a>'
                for i in proj["issues"]
            )
            issues_html = f"""
                <div class="issues-section">
                    <h4>Referenced Issues</h4>
                    <p>{issue_links}</p>
                </div>"""

        # Version badges
        versions_html = ""
        if proj["versions"]:
            badges = "".join(
                f'<a href="{proj["github_url"]}/releases/tag/{v["tag"]}" class="version-badge" target="_blank">{v["tag"]}</a>'
                for v in proj["versions"]
            )
            versions_html = f'<div class="version-list">{badges}</div>'

        baseline_label = proj["baseline"] if proj["baseline"] else "initial"

        project_sections.append(f"""
        <section class="project" id="{proj['name']}">
            <div class="project-header">
                <div class="project-info">
                    <h3>
                        <a href="{proj['github_url']}" target="_blank">{_escape(proj['display_name'])}</a>
                    </h3>
                    <p class="project-desc">{_escape(proj['description'])}</p>
                </div>
                <div class="project-meta">
                    <span class="version-range">{baseline_label} &rarr; {proj['latest']}</span>
                    <span class="commit-count">{proj['total_commits']} commits</span>
                </div>
            </div>
            {versions_html}
            <div class="categories">
                {''.join(categories_html)}
            </div>
            {issues_html}
        </section>""")

    # Navigation
    nav_items = "".join(
        f'<a href="#{p["name"]}" class="nav-item">'
        f'<span class="nav-name">{_escape(p["display_name"])}</span>'
        f'<span class="nav-range">{p["baseline"] or "initial"} &rarr; {p["latest"]}</span>'
        f'</a>'
        for p in data
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_escape(config['title'])}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --surface-2: #1c2129;
            --border: #30363d;
            --text: #e6edf3;
            --text-muted: #8b949e;
            --text-dim: #6e7681;
            --accent: #58a6ff;
            --accent-subtle: #1f6feb22;
            --green: #3fb950;
            --green-subtle: #23863622;
            --red: #f85149;
            --purple: #bc8cff;
            --orange: #d29922;
            --yellow: #e3b341;
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
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        /* Header */
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

        /* Stats */
        .stats {{
            display: flex;
            gap: 24px;
            justify-content: center;
            margin-top: 32px;
            flex-wrap: wrap;
        }}

        .stat {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px 32px;
            text-align: center;
            min-width: 140px;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent);
            line-height: 1.2;
        }}

        .stat:nth-child(2) .stat-value {{ color: var(--green); }}
        .stat:nth-child(3) .stat-value {{ color: var(--red); }}
        .stat:nth-child(4) .stat-value {{ color: var(--purple); }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }}

        /* Layout */
        .content {{
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 32px;
            padding: 40px 0 80px;
        }}

        @media (max-width: 768px) {{
            .content {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{ display: none; }}
        }}

        /* Sidebar nav */
        .sidebar {{
            position: sticky;
            top: 24px;
            align-self: start;
        }}

        .sidebar h2 {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-dim);
            margin-bottom: 12px;
            padding-left: 12px;
        }}

        .nav-item {{
            display: block;
            padding: 8px 12px;
            border-radius: var(--radius);
            color: var(--text-muted);
            text-decoration: none;
            transition: all 0.15s;
            margin-bottom: 2px;
        }}

        .nav-item:hover {{
            background: var(--surface);
            color: var(--text);
        }}

        .nav-name {{
            display: block;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .nav-range {{
            display: block;
            font-size: 0.75rem;
            color: var(--text-dim);
        }}

        /* Project sections */
        .project {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 28px;
            margin-bottom: 24px;
            scroll-margin-top: 24px;
        }}

        .project-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .project-info h3 {{
            font-size: 1.35rem;
            font-weight: 600;
        }}

        .project-info h3 a {{
            color: var(--text);
            text-decoration: none;
        }}

        .project-info h3 a:hover {{
            color: var(--accent);
        }}

        .project-desc {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 2px;
        }}

        .project-meta {{
            display: flex;
            gap: 16px;
            align-items: center;
            flex-shrink: 0;
        }}

        .version-range {{
            background: var(--accent-subtle);
            color: var(--accent);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
        }}

        .commit-count {{
            color: var(--text-muted);
            font-size: 0.8rem;
            white-space: nowrap;
        }}

        /* Version badges */
        .version-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 20px;
        }}

        .version-badge {{
            background: var(--surface-2);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            text-decoration: none;
            font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
            transition: all 0.15s;
        }}

        .version-badge:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        /* Categories */
        .category {{
            margin-bottom: 16px;
        }}

        .category:last-child {{
            margin-bottom: 0;
        }}

        .category-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-muted);
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .count {{
            background: var(--surface-2);
            color: var(--text-dim);
            font-size: 0.7rem;
            padding: 1px 7px;
            border-radius: 10px;
            font-weight: 500;
        }}

        .commit-list {{
            list-style: none;
        }}

        .commit-list li {{
            padding: 5px 0;
            font-size: 0.88rem;
            display: flex;
            align-items: baseline;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .sha {{
            font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
            font-size: 0.78rem;
            color: var(--accent);
            text-decoration: none;
            background: var(--accent-subtle);
            padding: 1px 6px;
            border-radius: 4px;
            flex-shrink: 0;
        }}

        .sha:hover {{
            text-decoration: underline;
        }}

        .scope {{
            background: var(--green-subtle);
            color: var(--green);
            font-size: 0.75rem;
            padding: 1px 8px;
            border-radius: 10px;
            font-weight: 500;
            flex-shrink: 0;
        }}

        .commit-desc {{
            color: var(--text);
        }}

        /* Issues */
        .issues-section {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
        }}

        .issues-section h4 {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .issues-section a {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.88rem;
        }}

        .issues-section a:hover {{
            text-decoration: underline;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 32px 0;
            border-top: 1px solid var(--border);
            color: var(--text-dim);
            font-size: 0.8rem;
        }}

        .footer a {{
            color: var(--text-muted);
            text-decoration: none;
        }}

        .footer a:hover {{
            color: var(--accent);
        }}
    </style>
</head>
<body>
    <header class="hero">
        <div class="container">
            <h1>{_escape(config['title'])}</h1>
            <p class="subtitle">Generated on {generated_at}</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_projects}</div>
                    <div class="stat-label">Projects</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_commits}</div>
                    <div class="stat-label">Commits</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_features}</div>
                    <div class="stat-label">Features</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_fixes}</div>
                    <div class="stat-label">Bug Fixes</div>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="content">
            <nav class="sidebar">
                <h2>Projects</h2>
                {nav_items}
            </nav>
            <main>
                {''.join(project_sections)}
            </main>
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p>Generated by <a href="https://github.com/{config['github_org']}">Nominal Systems</a> release notes tool</p>
        </div>
    </footer>

    <script>
        // Smooth scroll for nav
        document.querySelectorAll('.nav-item').forEach(a => {{
            a.addEventListener('click', e => {{
                e.preventDefault();
                const target = document.querySelector(a.getAttribute('href'));
                if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});

        // Highlight active nav on scroll
        const sections = document.querySelectorAll('.project');
        const navItems = document.querySelectorAll('.nav-item');
        const observer = new IntersectionObserver(entries => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    navItems.forEach(n => n.style.background = '');
                    const active = document.querySelector(`.nav-item[href="#${{entry.target.id}}"]`);
                    if (active) active.style.background = 'var(--surface)';
                }}
            }});
        }}, {{ threshold: 0.3 }});
        sections.forEach(s => observer.observe(s));
    </script>
</body>
</html>"""

    return html


def _escape(text):
    """Escape HTML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    parser = argparse.ArgumentParser(description="Generate DMI release notes HTML")
    parser.add_argument("--config", "-c", default=str(DEFAULT_CONFIG), help="Path to config.json")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), help="Output directory for HTML")
    parser.add_argument("--workspace", "-w", default=None, help="Override workspace root (where repos are)")
    parser.add_argument("--serve", "-s", action="store_true", help="Start local preview server after generating")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port for preview server (default: 8080)")
    args = parser.parse_args()

    config_path = Path(args.config)
    output_dir = Path(args.output)

    print(f"Loading config from {config_path}", file=sys.stderr)
    with open(config_path) as f:
        config = json.load(f)

    # Resolve workspace root: CLI override, or relative to config file
    if args.workspace:
        workspace_root = Path(args.workspace).resolve()
    else:
        workspace_root = (config_path.parent / config["workspace_root"]).resolve()
    github_org = config["github_org"]

    print(f"Workspace root: {workspace_root}", file=sys.stderr)
    print(f"Collecting release notes...\n", file=sys.stderr)

    project_data = []
    for project in config["projects"]:
        data = collect_project_data(project, workspace_root, github_org)
        if data:
            project_data.append(data)

    if not project_data:
        print("\nNo project data collected. Check your config and repository paths.", file=sys.stderr)
        sys.exit(1)

    print(f"\nCollected data from {len(project_data)} projects.", file=sys.stderr)

    # Generate HTML
    html = generate_html(project_data, config)

    # Write output
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Written to {index_path}", file=sys.stderr)

    # Also write data as JSON for potential reuse
    data_path = output_dir / "data.json"
    data_path.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "config": config,
        "projects": project_data,
    }, indent=2, default=str), encoding="utf-8")
    print(f"Data written to {data_path}", file=sys.stderr)

    if args.serve:
        print(f"\nStarting preview server at http://localhost:{args.port}", file=sys.stderr)
        print("Press Ctrl+C to stop.\n", file=sys.stderr)
        os.chdir(str(output_dir))
        server = HTTPServer(("localhost", args.port), SimpleHTTPRequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", file=sys.stderr)


if __name__ == "__main__":
    main()
