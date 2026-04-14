# Release Notes Generator

Generates static HTML release notes for the DMI platform by collecting git log
data between baseline and latest tags across all project repositories, and
publishes them to GitHub Pages.

## What gets generated

Each run produces a date-stamped directory at `docs/release-notes/YYYY-MM-DD/`
containing:

- `index.html` — the release notes page for that generation
- `data.json` — raw collected data (used by the index page)

An index page at `docs/release-notes/index.html` lists all generations, with
the most recent marked as "Latest".

GitHub Pages serves the `docs/` directory of `master`, so anything committed
there becomes available at <https://nominal-systems.github.io/dmi/>.

## Files

- `config.json` — baseline versions per project
- `generate-html.py` — collects git history and renders the notes page
- `generate-index.py` — rebuilds `docs/release-notes/index.html` from all
  dated subdirectories

## How to generate and publish a release

### Option A — GitHub Actions (recommended)

1. Go to **Actions → Generate Release Notes → Run workflow** (on `master`)
2. The workflow clones all project repos, generates the notes, rebuilds the
   index, and auto-commits to `master`
3. GitHub Pages picks up the change automatically

The workflow lives at `.github/workflows/release-notes.yml`.

### Option B — Locally

Prerequisites: all project repos must be checked out as siblings of `dmi/`
under a common workspace directory (e.g. `/Users/belbo/Nominal/`), and each
must have its tags fetched.

```bash
cd dmi/scripts/release-notes

# 1. Update baselines in config.json to the last published versions
#    (e.g. bump dmi-api baseline from v1.13.3 to v1.13.13)

# 2. Generate today's notes
DATE=$(date -u +%Y-%m-%d)
python3 generate-html.py \
  --config config.json \
  --output ../../docs/release-notes/$DATE

# 3. Rebuild the index
python3 generate-index.py --site-dir ../../docs

# 4. Preview locally (optional)
python3 -m http.server 8080 --directory ../../docs
# then open http://localhost:8080/release-notes/

# 5. Commit and push
cd ../..
git add docs/release-notes/
git commit -m "release-notes: $DATE"
git push
```

## Updating baselines

After a generation is published, update `config.json` so the next generation
starts where this one left off:

- `dmi-api` / `dmi-engine` / integrations: bump `baseline` to the latest tag
  shown in the just-published notes
- `dmi-api-admin-ui`: use the `UI_APP_VERSION` from
  `dmi-api/.github/workflows/build-and-push-to-registry.yml` as of the new
  `dmi-api` baseline
- `dmi-engine-antech-v6-integration` and `dmi-engine-wisdom-panel-integration`:
  use the versions pinned in `dmi-engine/package.json` as of the new
  `dmi-engine` baseline

## Previewing without generating

To preview a page that already exists in `docs/`:

```bash
python3 -m http.server 8080 --directory docs
# http://localhost:8080/release-notes/
```

## How commits are categorized

`generate-html.py` parses conventional commit prefixes (`feat:`, `fix:`,
`chore:`, etc.) and groups them into sections. Commits without a prefix are
categorized by keyword ("add", "fix", "refactor", "improve", ...). Version
bump commits (`1.2.3`) and merge commits are skipped.

Issue references (`#123`) are extracted from commit messages and linked to
the corresponding repo on GitHub.
