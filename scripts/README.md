# Utility Scripts

This directory contains small utility scripts used when working with DMI.
The `run.js` program provides an interactive way to run the available scripts.

1. Copy `.env.example` to `.env` and adjust the values for your environment.
2. Run `npm install` to install the dependencies.
3. Execute the runner:

```bash
node run.js
```

You will be prompted to choose one of the scripts and review or override its
configuration values before execution.

## Release Notes

Generate Markdown release notes for issues closed between two dates. By default it aggregates across all repositories in a GitHub organization (owner). You can optionally target a single repo.

- Prereq: Node 18+ (for global `fetch`).
- Auth: Uses `GITHUB_TOKEN`/`GH_TOKEN` if set, otherwise falls back to `gh auth token` (GitHub CLI) if available.
- Run:

```bash
# Interactive via runner
node scripts/run.js

# Direct CLI
node scripts/release-notes/generate.js <start: YYYY-MM-DD> [end: YYYY-MM-DD] [--owner OWNER] [--repo REPO] [--out PATH]
```

Examples:

```bash
# From January 1st to today (all repos in org)
node scripts/release-notes/generate.js 2025-01-01 --owner nominal-systems

# For a specific repo and window, to custom file
node scripts/release-notes/generate.js 2025-05-01 2025-06-01 --owner nominal-systems --repo some-repo --out notes.md
```

Output: header `# DMI Release Notes <end-date>`, then a bullet list of closed issues. The issue number is the link (not the full URL). Each bullet includes the `owner/repo` prefix when aggregating across multiple repositories.
