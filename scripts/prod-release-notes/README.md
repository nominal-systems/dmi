# PROD release notes

Answers one question: **what actually changed in PROD between the version
production is running and the version replacing it?**

Each DMI service is promoted DEV → QA/QE → UAT → TRN/STG → PROD on its own
cadence, so several intermediate releases usually happen before anything reaches
production. These notes are PROD-to-PROD: they span every one of those
intermediate versions, not just the last hop.

- Workflow: [`.github/workflows/prod-release-notes.yml`](../../.github/workflows/prod-release-notes.yml)
- Generator: [`generate.py`](generate.py) (Python 3 standard library only)
- Topology: [`config.json`](config.json)

This is separate from the older `release-notes.yml`, which publishes the
date-stamped HTML site under `docs/` from a fixed per-project baseline. That one
is not PROD-to-PROD and is left untouched.

## Running it

Actions → **PROD Release Notes** → Run workflow.

| Input | Meaning |
| --- | --- |
| `release_name` | Free text, e.g. `w33`. Used for the title, the artifact name and the draft release tag. |
| `versions` | JSON map of PROD versions (below). |
| `create_release` | Leave checked to create/update the draft release; uncheck for markdown only. |

`versions` for the w33 release:

```json
{
  "dmi-api":                       { "from": "v1.14.5", "to": "v1.14.9" },
  "dmi-engine":                    { "from": "v1.5.1",  "to": "v1.5.5"  },
  "dmi-engine-idexx-integration":  { "from": "v1.2.5",  "to": "v1.2.6"  },
  "dmi-engine-antech-integration": { "from": "v1.4.1",  "to": null      },
  "dmi-engine-zoetis-integration": { "from": "v1.1.2",  "to": null      }
}
```

`"to": null` (or leaving the repo out entirely) means **unchanged this
release** — it is reported as such rather than as an empty section. Only the
five standalone deployables are valid keys; bundled repos are discovered
automatically and must not be listed.

Tags may be written `v1.14.5` or `1.14.5`; both are resolved.

### Output

1. The markdown is written to the run summary and uploaded as an artifact, so it
   can be read before anything is published.
2. A **draft** GitHub Release on `nominal-systems/dmi` tagged with the release
   name. It stays a draft until somebody publishes it. Re-running with the same
   release name updates that draft instead of creating a second one.

### Running it locally

Clone the repos side by side (as in `~/Nominal`), then:

```bash
GH_TOKEN=$(gh auth token) python3 scripts/prod-release-notes/generate.py \
  --versions @w33.json \
  --release-name w33 \
  --workspace ~/Nominal \
  --output w33.md
```

Add `--offline` to skip the GitHub API entirely. Titles, authors and categories
then come from commit metadata alone, which is a little less precise but needs
no token.

Exit codes: `0` fine, `1` bad input (nothing written), `2` notes written but at
least one service failed — the failures are listed in the notes themselves.

## How it works

**Ranges.** Each service's `from`/`to` is resolved to a real tag, and every
commit between them is collected.

**Pull requests over commits.** Merge commits (`Merge pull request #N`) and
squash merges (`... (#N)`) are recognised; rebase merges are recovered from the
API. Commits carried in by a merge are folded into that PR, so nothing is listed
twice, and a commit pushed straight to the branch with no PR is still reported.

**Bundled libraries.** Some repos never deploy on their own — they ship inside
another service as an npm dependency. A naive tag-to-tag diff loses those
changes, showing only a one-line version bump. So for each service the generator
reads the first-party dependency versions at the old tag and at the new tag, and
where one moved, follows it into that repository and collects its commits too.
It prefers `package-lock.json` (the version that actually shipped) over the
`package.json` range, because `^0.4.21` does not by itself tell you what was
installed. Where a pin did not move, that is stated explicitly
("Antech V6 Integration unchanged at v0.4.21") rather than passed over.

A library consumed by more than one service (`dmi-engine-common`) is reported
once, annotated with everything that picked it up.

**Grouping.** Change type is derived, in order of preference, from: the
conventional-commit prefix, the PR labels, then the branch prefix (`fix/`,
`feat/`). Anything with none of those goes to a **Changes** bucket rather than
being guessed at from the wording of the title. Bug fixes and features are
therefore separate sections wherever the signal exists.

**Noise.** Release version-bump commits, Dependabot/Renovate commits and
lockfile-only changes are collapsed into a count. First-party dependency bumps
are never suppressed — they are the visible trace of a bundled library moving,
and get their own **Bundled components** group.

## Maintaining the topology

`config.json` is the single source of truth, and the clone list in the workflow
is derived from it.

- `deployables` — services with their own container and their own PROD version.
  These are the only valid keys in the `versions` input.
- `display_names` — cosmetic names, and also the list of bundled repos the
  workflow clones. **If a new first-party dependency starts shipping inside a
  service, add it here**, otherwise the generator reports
  `no clone at ...` for it rather than silently omitting it.
- `excluded` — repos deliberately left out, with the reason printed in the
  footer of every release note.
- npm package → repo name is derived by stripping the `@nominal-systems/`
  scope; use `package_to_repo` only where that derivation is wrong.

## GitHub configuration

The default `GITHUB_TOKEN` is scoped to `dmi` alone and cannot read the other
repositories — and three of them (`dmi-engine-idexx-integration`,
`dmi-engine-antech-integration`, `dmi-engine-zoetis-integration`) are private.
A cross-repository credential is therefore required.

The workflow accepts either, and prefers the App:

| | Credential | Expires? |
| --- | --- | --- |
| Preferred | GitHub App installation token, minted per run | Private key never expires |
| Fallback | `RELEASE_NOTES_TOKEN`, else the existing `GH_PAT` | Yes — up to 1 year |

The draft release itself is created with the default `secrets.GITHUB_TOKEN`,
because it lands on this repository.

### Recommended: GitHub App

An installation token is minted at the start of every run and lasts one hour.
The App's private key does not expire, so there is nothing to rotate on a
calendar, and the App is owned by the organisation rather than by a person — it
does not break when someone changes roles or leaves.

The org already has an App that is most of the way there: **`dmi-ci`**
(org-owned, created 2026-07-14) with `contents: read` and `metadata: read`. It
needs **Pull requests: Read** added and needs to cover all eight repositories
below. Extending it is less work than creating a new App; create a separate one
only if you would rather keep release-notes access isolated from the rest of CI.

**Permissions** (repository permissions, read-only throughout):

| Permission | Level | Why |
| --- | --- | --- |
| Contents | Read | clone history and tags, read `package.json` / `package-lock.json` at each tag |
| Pull requests | Read | PR titles, authors, labels, merge dates |
| Metadata | Read | mandatory |

**Repositories** it must be installed on: `dmi-api`, `dmi-engine`,
`dmi-engine-idexx-integration`, `dmi-engine-antech-integration`,
`dmi-engine-zoetis-integration`, `dmi-engine-antech-v6-integration`,
`dmi-engine-wisdom-panel-integration`, `dmi-engine-common`.

No write access anywhere.

**Click path**

1. `nominal-systems` → Settings → Developer settings → GitHub Apps → either
   **Edit** `dmi-ci`, or **New GitHub App** for a dedicated one.
2. Permissions & events → Repository permissions → set Contents, Pull requests
   and Metadata to **Read-only**. Save. (Changing permissions on an existing App
   raises a request an org owner must accept on the installation.)
3. Install App → nominal-systems → **Only select repositories** → the eight above.
4. On the App's General page, note the **App ID**, then
   **Generate a private key** — this downloads a `.pem` file once.
5. `dmi` → Settings → Secrets and variables → Actions:
   - **Variables** tab → New repository variable → `RELEASE_NOTES_APP_ID` = the App ID.
   - **Secrets** tab → New repository secret → `RELEASE_NOTES_APP_PRIVATE_KEY` =
     the entire contents of the `.pem`, including the
     `-----BEGIN RSA PRIVATE KEY-----` and `-----END …-----` lines.
6. Delete the downloaded `.pem` afterwards.

The App ID is deliberately a *variable*, not a secret: it is not sensitive, and
the workflow uses it to detect whether the App is configured at all. With the
variable unset the App step is skipped and the PAT fallback takes over, so the
workflow keeps working throughout the switchover.

Two honest caveats. The App does not remove the need to store a credential — it
replaces an expiring token with a non-expiring private key, which is a *more*
powerful secret if it ever leaks (it can mint tokens for everything the App is
installed on). Keeping the App read-only and narrowly installed is what limits
that. And minting the token uses `actions/create-github-app-token`, a
marketplace action; it is GitHub's own, and the alternative is hand-rolling
RS256 JWT signing in bash, which would be worse to debug than the dependency.

### Fallback: fine-grained PAT

Works, and needs no org-owner involvement if you already own a suitable token,
but it expires — silently, and most likely mid-release. Use it to get going and
switch to the App when convenient.

Same permissions as the table above. Personal Settings → Developer settings →
Personal access tokens → Fine-grained tokens → Generate new token; resource
owner `nominal-systems`; **Only select repositories** → the eight above;
Contents: Read-only, Pull requests: Read-only, Metadata: Read-only. If the org
requires approval, an owner approves it under the org's Personal access tokens
settings. Then `dmi` → Settings → Secrets and variables → Actions → New
repository secret named **`RELEASE_NOTES_TOKEN`**.

If neither `RELEASE_NOTES_TOKEN` nor the App is configured, the workflow falls
back to the existing `GH_PAT` secret, which today already clones all eight
repositories. If whichever token is in use lacks **Pull requests: Read**, the
run still succeeds: the API returns 403, a warning is logged, and titles and
authors fall back to commit metadata.
