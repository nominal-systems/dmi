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

Generate Markdown release notes for issues closed between two dates. By default it aggregates across all repositories in a GitHub organization (owner). You can optionally target a single repo. The script always writes to `RELEASE_NOTES.md` at the repository root and prepends new content so the latest release appears first.

- Prereq: Node 18+ (for global `fetch`).
- Auth: Uses `GITHUB_TOKEN`/`GH_TOKEN` if set, otherwise falls back to `gh auth token` (GitHub CLI) if available.
 - Atomic: If any GitHub API request fails, the script logs the error and does not modify `RELEASE_NOTES.md`.
 - Rate limits: If rate-limited, the error includes a suggested retry time based on `Retry-After` or `X-RateLimit-Reset`.
- Run:

```bash
# Interactive via runner (writes to RELEASE_NOTES.md at repo root)
node scripts/run.js

# Direct CLI
node scripts/release-notes/generate.js [start: YYYY-MM-DD] [end: YYYY-MM-DD] [--owner OWNER] [--repo REPO]
```

Examples:

```bash
# From January 1st to today (all repos in org)
node scripts/release-notes/generate.js 2025-01-01 --owner nominal-systems

# For a specific repo and window, to custom file
node scripts/release-notes/generate.js 2025-05-01 2025-06-01 --owner nominal-systems --repo some-repo

Non-interactive from last release until today

```bash
# No dates provided: script infers START_DATE from the top header in RELEASE_NOTES.md
node scripts/release-notes/generate.js --owner nominal-systems
```
```

Output: header `# DMI Release Notes <end-date>`, then a bullet list of closed issues. The issue number is the link (not the full URL). Each bullet includes the `owner/repo` prefix when aggregating across multiple repositories. New sections are prepended to `RELEASE_NOTES.md`.
