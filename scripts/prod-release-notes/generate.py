#!/usr/bin/env python3
"""Generate PROD-to-PROD release notes for the DMI platform.

The DMI platform ships as several independently versioned services. Each one is
promoted DEV -> QA/QE -> UAT -> TRN/STG -> PROD on its own cadence, so by the
time a version reaches PROD there are usually several intermediate releases that
never went to production. This script answers the only question that matters at
release time: what changed in PROD between the version running now and the
version replacing it.

Two things make that harder than a tag-to-tag diff:

1. Some repositories never deploy on their own. They ship inside another service
   as an npm dependency (for example dmi-engine-antech-v6-integration ships
   inside dmi-engine). A change to one of those is invisible in the parent's
   commit log apart from a one-line version bump, so the script reads the pinned
   dependency version at the old and new tags and follows the difference into
   the bundled repository.

2. A shared library (dmi-engine-common) is consumed by several services at once.
   It is reported once, annotated with everything that picked it up, rather than
   repeated under each consumer.

Usage:
    generate.py --versions '{"dmi-api": {"from": "v1.14.5", "to": "v1.14.9"}}' \
                --release-name w33 \
                --workspace /path/containing/clones \
                --output notes.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Output helpers. Everything diagnostic goes to stderr so stdout stays clean.
# --------------------------------------------------------------------------

def info(msg: str) -> None:
    print(f"    {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def fail(msg: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"\n[error] {msg}\n", file=sys.stderr)
    sys.exit(1)


class ServiceError(Exception):
    """A failure scoped to one service. Reported in the notes; does not abort."""


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class Change:
    """One user-visible change: a merged PR, or a commit that landed without one."""
    title: str
    author: str
    date: str
    shas: list[str] = field(default_factory=list)
    number: int | None = None
    url: str = ""
    labels: list[str] = field(default_factory=list)
    branch: str = ""
    category: str = "Changes"
    category_source: str = "default"
    author_is_login: bool = False

    @property
    def sort_key(self) -> tuple:
        return (self.date or "", self.number or 0)


@dataclass
class ServiceReport:
    repo: str
    display: str
    role: str                      # deployable | bundled | shared
    status: str = "unchanged"      # changed | unchanged | error
    from_version: str | None = None
    to_version: str | None = None
    message: str = ""
    changes: list[Change] = field(default_factory=list)
    suppressed: dict[str, int] = field(default_factory=dict)
    consumers: list[str] = field(default_factory=list)   # bundled: who ships it
    dep_notes: list[str] = field(default_factory=list)   # "X unchanged at vN"

    @property
    def suppressed_total(self) -> int:
        return sum(self.suppressed.values())


# --------------------------------------------------------------------------
# Git
# --------------------------------------------------------------------------

FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"


def git(repo_dir: str, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", repo_dir, *args],
        capture_output=True, text=True,
    )
    if check and proc.returncode != 0:
        raise ServiceError(
            f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def tag_exists(repo_dir: str, tag: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", repo_dir, "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def resolve_tag(repo_dir: str, version: str) -> str:
    """Map a version string to a real tag. Tags may be 'v1.14.5' or '1.14.5'."""
    bare = version.lstrip("vV") if re.match(r"^[vV]\d", version) else version
    candidates: list[str] = []
    for candidate in (version, f"v{bare}", bare):
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    for candidate in candidates:
        if tag_exists(repo_dir, candidate):
            return candidate

    raise ServiceError(
        f"no tag found for version '{version}' (tried: {', '.join(candidates)}). "
        f"The release cannot be diffed against a version that was never tagged."
    )


# --------------------------------------------------------------------------
# Change collection
# --------------------------------------------------------------------------

# The owner segment is matched explicitly: a greedy \S+ would swallow the
# branch's own prefix (nominal-systems/fix/foo -> "foo" instead of "fix/foo").
MERGE_PR_RE = re.compile(r"^Merge pull request #(\d+) from [^/\s]+/(?P<branch>\S+)")
SQUASH_PR_RE = re.compile(r"\(#(\d+)\)\s*$")
VERSION_BUMP_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+]\S+)?$")
BOT_AUTHOR_RE = re.compile(r"dependabot|renovate|github-actions", re.I)
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"}


def read_commits(repo_dir: str, rev_range: str) -> list[dict]:
    """Every commit in the range, merges included, newest first."""
    fmt = FIELD_SEP.join(["%H", "%P", "%s", "%b", "%an", "%aI"]) + RECORD_SEP
    raw = git(repo_dir, "log", f"--format={fmt}", rev_range)

    commits = []
    for record in raw.split(RECORD_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        parts = record.split(FIELD_SEP)
        if len(parts) < 6:
            continue
        sha, parents, subject, body, author, date = parts[:6]
        commits.append({
            "sha": sha,
            "parents": parents.split(),
            "subject": subject.strip(),
            "body": body.strip(),
            "author": author.strip(),
            "date": date.strip(),
        })
    return commits


def changed_files(repo_dir: str, sha: str) -> set[str]:
    raw = git(repo_dir, "show", "--pretty=", "--name-only", sha, check=False)
    return {line.strip() for line in raw.splitlines() if line.strip()}


def branch_commits(repo_dir: str, merge_sha: str) -> list[str]:
    """Commits brought in by a merge, i.e. the PR's own commits."""
    raw = git(repo_dir, "rev-list", f"{merge_sha}^2", "--not", f"{merge_sha}^1", check=False)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def collect_changes(repo_dir: str, repo: str, rev_range: str, gh: "GitHub",
                    scope: str) -> tuple[list[Change], dict[str, int]]:
    """Group a commit range into merged PRs plus any commits that landed directly.

    Each commit is attributed at most once: commits carried in by a merge belong
    to that merge's PR, and everything left over is reported on its own.
    """
    commits = read_commits(repo_dir, rev_range)
    by_sha = {c["sha"]: c for c in commits}

    pr_commits: dict[int, dict] = {}   # pr number -> {shas, branch, seed commit}
    claimed: set[str] = set()

    # Pass 1: merge commits. These name their PR explicitly and tell us exactly
    # which commits the PR contributed.
    for commit in commits:
        if len(commit["parents"]) < 2:
            continue
        match = MERGE_PR_RE.match(commit["subject"])
        if not match:
            continue
        number = int(match.group(1))
        members = [sha for sha in branch_commits(repo_dir, commit["sha"]) if sha in by_sha]
        entry = pr_commits.setdefault(number, {"shas": [], "branch": "", "seed": commit})
        entry["branch"] = match.group("branch")
        entry["shas"].extend([commit["sha"], *members])
        claimed.update(entry["shas"])
        # The merge body's first line is the PR title.
        first_body_line = next((l for l in commit["body"].splitlines() if l.strip()), "")
        entry["title"] = first_body_line.strip() or commit["subject"]

    # Pass 2: squash merges, which carry "(#N)" in the subject.
    for commit in commits:
        if commit["sha"] in claimed or len(commit["parents"]) > 1:
            continue
        match = SQUASH_PR_RE.search(commit["subject"])
        if not match:
            continue
        number = int(match.group(1))
        entry = pr_commits.setdefault(number, {"shas": [], "branch": "", "seed": commit})
        entry["shas"].append(commit["sha"])
        entry.setdefault("title", SQUASH_PR_RE.sub("", commit["subject"]).strip())
        claimed.add(commit["sha"])

    suppressed: dict[str, int] = {}

    def suppress(reason: str) -> None:
        suppressed[reason] = suppressed.get(reason, 0) + 1

    changes: list[Change] = []

    # Merged PRs, enriched from the API where we can reach it.
    for number, entry in pr_commits.items():
        seed = entry["seed"]
        change = Change(
            title=entry.get("title") or seed["subject"],
            author=seed["author"],
            date=seed["date"],
            shas=entry["shas"],
            number=number,
            branch=entry["branch"],
            url=f"https://github.com/{gh.org}/{repo}/pull/{number}",
        )
        meta = gh.pull_request(repo, number)
        if meta:
            change.title = meta.get("title") or change.title
            login = (meta.get("user") or {}).get("login")
            if login:
                change.author, change.author_is_login = login, True
            change.date = meta.get("merged_at") or change.date
            change.labels = [l["name"] for l in meta.get("labels", [])]
            change.branch = (meta.get("head") or {}).get("ref") or change.branch
            change.url = meta.get("html_url") or change.url

        reason = suppression_reason(repo_dir, change.shas, change.title,
                                    change.author, scope)
        if reason:
            suppress(reason)
            continue
        classify(change, scope)
        changes.append(change)

    # Commits with no PR anywhere in sight.
    for commit in commits:
        if commit["sha"] in claimed or len(commit["parents"]) > 1:
            continue

        # A rebase merge leaves no marker in the message; ask the API.
        number = gh.pr_for_commit(repo, commit["sha"])
        if number is not None and number in pr_commits:
            continue

        change = Change(
            title=commit["subject"],
            author=commit["author"],
            date=commit["date"],
            shas=[commit["sha"]],
            number=number,
            url=(f"https://github.com/{gh.org}/{repo}/pull/{number}" if number
                 else f"https://github.com/{gh.org}/{repo}/commit/{commit['sha']}"),
        )
        if number is not None:
            meta = gh.pull_request(repo, number)
            if meta:
                change.title = meta.get("title") or change.title
                login = (meta.get("user") or {}).get("login")
                if login:
                    change.author, change.author_is_login = login, True
                change.labels = [l["name"] for l in meta.get("labels", [])]
                change.branch = (meta.get("head") or {}).get("ref") or ""
                change.url = meta.get("html_url") or change.url

        reason = suppression_reason(repo_dir, change.shas, change.title,
                                    change.author, scope)
        if reason:
            suppress(reason)
            continue
        classify(change, scope)
        changes.append(change)

    changes.sort(key=lambda c: c.sort_key, reverse=True)
    return changes, suppressed


def suppression_reason(repo_dir: str, shas: list[str], title: str, author: str,
                       scope: str) -> str | None:
    """Why this change should be collapsed into a count, or None to keep it.

    A first-party dependency bump is never suppressed: it is the visible trace of
    a bundled library moving, which is exactly the signal we are trying to keep.
    """
    if scope.lower() in title.lower():
        return None

    if VERSION_BUMP_RE.match(title.strip()):
        return "release version bump"

    if BOT_AUTHOR_RE.search(author):
        return "automated dependency bump"

    files: set[str] = set()
    for sha in shas:
        files |= changed_files(repo_dir, sha)
    if files and files <= LOCKFILES:
        return "lockfile-only update"
    if files and files <= (LOCKFILES | {"package.json"}) and _looks_like_dep_bump(title):
        return "third-party dependency bump"

    return None


def _looks_like_dep_bump(title: str) -> bool:
    return bool(re.match(r"^(chore\(deps\)|bump|update)\b", title.strip(), re.I))


# --------------------------------------------------------------------------
# Categorisation
#
# Four signals, in decreasing order of reliability. Every one of them is an
# explicit convention the team already follows, so nothing here is inferred from
# the prose of a title.
# --------------------------------------------------------------------------

CONVENTIONAL_RE = re.compile(
    r"^(?P<type>feat|feature|fix|bugfix|perf|refactor|docs|doc|test|tests|chore|build|ci|style|revert|security)"
    r"(?:\([^)]*\))?!?:\s",
    re.I,
)
BRANCH_PREFIX_RE = re.compile(
    r"^(?P<type>feat|feature|fix|bugfix|hotfix|perf|refactor|docs|chore|build|ci|test|security)[/-]",
    re.I,
)

TYPE_TO_CATEGORY = {
    "feat": "Features", "feature": "Features",
    "fix": "Fixes", "bugfix": "Fixes", "hotfix": "Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "docs": "Documentation", "doc": "Documentation",
    "test": "Tests", "tests": "Tests",
    "build": "Build & CI", "ci": "Build & CI",
    "chore": "Maintenance", "style": "Maintenance", "revert": "Maintenance",
    "security": "Security",
}

LABEL_TO_CATEGORY = {
    "bug": "Fixes", "bugfix": "Fixes", "fix": "Fixes", "defect": "Fixes",
    "enhancement": "Features", "feature": "Features", "features": "Features",
    "performance": "Performance",
    "documentation": "Documentation",
    "refactor": "Refactoring",
    "security": "Security",
}

BUNDLED_CATEGORY = "Bundled components"

CATEGORY_ORDER = [
    "Features", "Fixes", BUNDLED_CATEGORY, "Performance", "Security", "Refactoring",
    "Documentation", "Tests", "Build & CI", "Maintenance", "Changes",
]


def classify(change: Change, scope: str = "@nominal-systems/") -> None:
    # A first-party version bump is the visible trace of a bundled library moving.
    # It gets its own bucket so it is not buried among routine chores - the detail
    # lives in that library's own section.
    if scope.lower() in change.title.lower():
        change.category = BUNDLED_CATEGORY
        change.category_source = "first-party dependency bump"
        return

    match = CONVENTIONAL_RE.match(change.title)
    if match:
        change.category = TYPE_TO_CATEGORY.get(match.group("type").lower(), "Changes")
        change.category_source = "conventional commit prefix"
        return

    for label in change.labels:
        category = LABEL_TO_CATEGORY.get(label.strip().lower())
        if category:
            change.category = category
            change.category_source = f"PR label '{label}'"
            return

    match = BRANCH_PREFIX_RE.match(change.branch or "")
    if match:
        change.category = TYPE_TO_CATEGORY.get(match.group("type").lower(), "Changes")
        change.category_source = "branch prefix"
        return

    change.category = "Changes"
    change.category_source = "default"


def strip_conventional_prefix(title: str) -> str:
    return CONVENTIONAL_RE.sub("", title).strip() or title


# --------------------------------------------------------------------------
# GitHub API (read-only, plain urllib so there is nothing to install)
# --------------------------------------------------------------------------

class GitHub:
    def __init__(self, org: str, token: str | None, offline: bool = False):
        self.org = org
        self.token = token
        self.offline = offline or not token
        self._pr_cache: dict[tuple[str, int], dict | None] = {}
        self._commit_cache: dict[tuple[str, str], int | None] = {}
        if self.offline:
            warn("running without a GitHub token: PR titles, authors and labels "
                 "fall back to commit metadata.")

    def _get(self, path: str):
        if self.offline:
            return None
        request = urllib.request.Request(
            f"https://api.github.com{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "dmi-prod-release-notes",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code in (401, 403):
                warn(f"GitHub API {exc.code} on {path} - token lacks access to this "
                     f"repository, or the rate limit is exhausted. Falling back to "
                     f"commit metadata.")
                return None
            warn(f"GitHub API error {exc.code} on {path}")
            return None
        except Exception as exc:  # network hiccup: degrade, do not abort
            warn(f"GitHub API request failed for {path}: {exc}")
            return None

    def pull_request(self, repo: str, number: int) -> dict | None:
        key = (repo, number)
        if key not in self._pr_cache:
            self._pr_cache[key] = self._get(f"/repos/{self.org}/{repo}/pulls/{number}")
        return self._pr_cache[key]

    def pr_for_commit(self, repo: str, sha: str) -> int | None:
        key = (repo, sha)
        if key not in self._commit_cache:
            data = self._get(f"/repos/{self.org}/{repo}/commits/{sha}/pulls")
            merged = [p for p in (data or []) if p.get("merged_at")]
            self._commit_cache[key] = merged[0]["number"] if merged else None
        return self._commit_cache[key]


# --------------------------------------------------------------------------
# Bundled dependency discovery
# --------------------------------------------------------------------------

def read_json_at(repo_dir: str, ref: str, path: str) -> dict | None:
    raw = git(repo_dir, "show", f"{ref}:{path}", check=False)
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        warn(f"{path} at {ref} is not valid JSON; ignoring")
        return None


def first_party_deps(repo_dir: str, ref: str, scope: str) -> dict[str, str]:
    """Resolved versions of first-party dependencies at a ref.

    package.json only records a range ('^0.4.21'), and what actually shipped is
    whatever the lockfile resolved that range to. The lockfile wins where it is
    present; the range's base version is the fallback.
    """
    package = read_json_at(repo_dir, ref, "package.json")
    if not package:
        raise ServiceError(f"no package.json at {ref}")

    declared: dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, spec in (package.get(section) or {}).items():
            if name.startswith(scope):
                declared[name] = spec

    lock = read_json_at(repo_dir, ref, "package-lock.json") or {}
    resolved_from_lock: dict[str, str] = {}
    for path, entry in (lock.get("packages") or {}).items():
        # Only top-level installs: 'node_modules/<pkg>', not nested copies.
        if not path.startswith("node_modules/"):
            continue
        name = path[len("node_modules/"):]
        if name.startswith(scope) and entry.get("version"):
            resolved_from_lock[name] = entry["version"]

    out: dict[str, str] = {}
    for name, spec in declared.items():
        out[name] = resolved_from_lock.get(name) or spec.lstrip("^~>=< v")
    return out


def package_to_repo(name: str, config: dict) -> str:
    overrides = config.get("package_to_repo") or {}
    if name in overrides:
        return overrides[name]
    return name.split("/", 1)[-1]


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------

def parse_versions(raw: str, deployables: list[str]) -> dict[str, dict]:
    raw = raw.strip()
    if not raw:
        fail("--versions is empty. Provide a JSON object such as "
             '{"dmi-api": {"from": "v1.14.5", "to": "v1.14.9"}}')

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"--versions is not valid JSON: {exc}\n"
             f"Received: {raw[:400]}\n"
             'Expected an object such as {"dmi-api": {"from": "v1.14.5", "to": "v1.14.9"}}')

    if not isinstance(data, dict):
        fail(f"--versions must be a JSON object mapping repo -> versions, "
             f"got {type(data).__name__}.")

    known = set(deployables)
    problems: list[str] = []
    parsed: dict[str, dict] = {}

    for repo, value in data.items():
        if repo not in known:
            problems.append(
                f"  - '{repo}' is not a known standalone deployable. "
                f"Valid keys: {', '.join(sorted(known))}"
            )
            continue

        if value is None:
            parsed[repo] = {"from": None, "to": None}
            continue

        if not isinstance(value, dict):
            problems.append(f"  - '{repo}' must map to an object or null, "
                            f"got {type(value).__name__}.")
            continue

        unknown_keys = set(value) - {"from", "to"}
        if unknown_keys:
            problems.append(f"  - '{repo}' has unexpected key(s): "
                            f"{', '.join(sorted(unknown_keys))}. Only 'from' and 'to' are allowed.")
            continue

        from_v, to_v = value.get("from"), value.get("to")
        for field_name, field_value in (("from", from_v), ("to", to_v)):
            if field_value is not None and not isinstance(field_value, str):
                problems.append(f"  - '{repo}.{field_name}' must be a string or null, "
                                f"got {type(field_value).__name__}.")
        if to_v is not None and not from_v:
            problems.append(f"  - '{repo}' has 'to' but no 'from'. A PROD-to-PROD range "
                            f"needs the version currently in production.")

        parsed[repo] = {"from": from_v, "to": to_v}

    if problems:
        fail("the version map is malformed:\n" + "\n".join(problems))

    if not parsed:
        fail("the version map contains no recognised services; nothing to report.")

    if not any(v.get("to") and v.get("to") != v.get("from") for v in parsed.values()):
        fail("every service in the version map is unchanged - there is no release "
             "to describe. Check the 'to' versions.")

    return parsed


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def build_reports(versions: dict[str, dict], config: dict, workspace: str,
                  gh: GitHub) -> tuple[list[ServiceReport], list[ServiceReport]]:
    scope = config.get("npm_scope", "@nominal-systems/")
    display_names = config.get("display_names") or {}
    deployable_display = {d["repo"]: d.get("display", d["repo"])
                          for d in config["deployables"]}

    def display_for(repo: str) -> str:
        return deployable_display.get(repo) or display_names.get(repo) or repo

    deployable_reports: list[ServiceReport] = []
    # repo -> {'from':..., 'to':..., 'consumers': [...]}
    bundled_ranges: dict[str, dict] = {}

    def note_bundled(repo: str, from_v: str, to_v: str, consumer: str) -> None:
        existing = bundled_ranges.get(repo)
        if existing is None:
            bundled_ranges[repo] = {"from": from_v, "to": to_v, "consumers": [consumer]}
            return
        if consumer not in existing["consumers"]:
            existing["consumers"].append(consumer)
        # Different consumers can pin different versions. Widen to cover both so
        # no commit is lost.
        if version_key(from_v) < version_key(existing["from"]):
            existing["from"] = from_v
        if version_key(to_v) > version_key(existing["to"]):
            existing["to"] = to_v

    # --- standalone deployables -------------------------------------------
    for entry in config["deployables"]:
        repo = entry["repo"]
        spec = versions.get(repo, {"from": None, "to": None})
        report = ServiceReport(repo=repo, display=display_for(repo), role="deployable",
                               from_version=spec.get("from"), to_version=spec.get("to"))
        repo_dir = os.path.join(workspace, repo)

        try:
            if not os.path.isdir(os.path.join(repo_dir, ".git")):
                raise ServiceError(
                    f"no clone at {repo_dir}. The workflow clones every repo it needs; "
                    f"locally, clone it next to the others."
                )

            if not spec.get("to") or spec.get("to") == spec.get("from"):
                report.status = "unchanged"
                report.message = ("not part of this release"
                                  if not spec.get("from")
                                  else f"unchanged at {spec['from']}")
                # A service that did not move still pins dependencies, but since
                # nothing about it changed, nothing bundled inside it changed.
            else:
                from_tag = resolve_tag(repo_dir, spec["from"])
                to_tag = resolve_tag(repo_dir, spec["to"])
                info(f"{repo}: {from_tag}..{to_tag}")
                report.changes, report.suppressed = collect_changes(
                    repo_dir, repo, f"{from_tag}..{to_tag}", gh, scope)
                report.status = "changed"

                # Follow first-party dependencies into their own repos.
                old_deps = first_party_deps(repo_dir, from_tag, scope)
                new_deps = first_party_deps(repo_dir, to_tag, scope)
                for name in sorted(set(old_deps) | set(new_deps)):
                    dep_repo = package_to_repo(name, config)
                    old_v, new_v = old_deps.get(name), new_deps.get(name)
                    if old_v and new_v and old_v != new_v:
                        note_bundled(dep_repo, old_v, new_v, repo)
                    elif old_v and new_v:
                        report.dep_notes.append(
                            f"{display_for(dep_repo)} unchanged at v{old_v}")
                    elif new_v and not old_v:
                        report.dep_notes.append(
                            f"{display_for(dep_repo)} newly added at v{new_v}")
                    elif old_v and not new_v:
                        report.dep_notes.append(
                            f"{display_for(dep_repo)} removed (was v{old_v})")
        except ServiceError as exc:
            report.status = "error"
            report.message = str(exc)
            warn(f"{repo}: {exc}")

        deployable_reports.append(report)

    # --- bundled repos, followed transitively -----------------------------
    bundled_reports: list[ServiceReport] = []
    processed: set[str] = set()
    max_depth = int(config.get("bundled_max_depth", 3))

    for depth in range(max_depth):
        pending = [r for r in bundled_ranges if r not in processed]
        if not pending:
            break
        for repo in pending:
            processed.add(repo)
            span = bundled_ranges[repo]
            consumers = [display_for(c) for c in span["consumers"]]
            report = ServiceReport(
                repo=repo, display=display_for(repo),
                role="shared" if len(span["consumers"]) > 1 else "bundled",
                from_version=span["from"], to_version=span["to"],
                consumers=consumers,
            )
            repo_dir = os.path.join(workspace, repo)
            try:
                if not os.path.isdir(os.path.join(repo_dir, ".git")):
                    raise ServiceError(f"no clone at {repo_dir}")
                from_tag = resolve_tag(repo_dir, span["from"])
                to_tag = resolve_tag(repo_dir, span["to"])
                info(f"{repo} (bundled): {from_tag}..{to_tag}")
                report.changes, report.suppressed = collect_changes(
                    repo_dir, repo, f"{from_tag}..{to_tag}", gh, scope)
                report.status = "changed"

                if depth + 1 < max_depth:
                    old_deps = first_party_deps(repo_dir, from_tag, scope)
                    new_deps = first_party_deps(repo_dir, to_tag, scope)
                    for name in sorted(set(old_deps) | set(new_deps)):
                        dep_repo = package_to_repo(name, config)
                        old_v, new_v = old_deps.get(name), new_deps.get(name)
                        if old_v and new_v and old_v != new_v:
                            note_bundled(dep_repo, old_v, new_v, repo)
                        elif old_v and new_v:
                            report.dep_notes.append(
                                f"{display_for(dep_repo)} unchanged at v{old_v}")
            except ServiceError as exc:
                report.status = "error"
                report.message = str(exc)
                warn(f"{repo}: {exc}")

            bundled_reports.append(report)

    bundled_reports.sort(key=lambda r: r.display)
    return deployable_reports, bundled_reports


def version_key(version: str) -> tuple:
    parts = re.findall(r"\d+", version or "")
    return tuple(int(p) for p in parts[:4]) or (0,)


# --------------------------------------------------------------------------
# Markdown rendering
# --------------------------------------------------------------------------

def vtag(version: str | None) -> str:
    if not version:
        return "-"
    return version if version.startswith("v") else f"v{version}"


def render(release_name: str, deployables: list[ServiceReport],
           bundled: list[ServiceReport], config: dict, generated_on: str) -> str:
    org = config["org"]
    lines: list[str] = []
    add = lines.append

    add(f"# DMI PROD Release Notes - {release_name}")
    add("")
    add(f"Everything that reaches production between the versions running now and the "
        f"versions this release promotes. Generated {generated_on}.")
    add("")

    # --- version table ----------------------------------------------------
    add("## Versions")
    add("")
    add("| Service | PROD before | PROD after | |")
    add("| --- | --- | --- | --- |")
    for report in deployables:
        if report.status == "error":
            state = "**failed**"
            before, after = vtag(report.from_version), vtag(report.to_version)
        elif report.status == "unchanged":
            state = "unchanged"
            before = vtag(report.from_version)
            after = "unchanged" if report.from_version else "-"
        else:
            state = f"{len(report.changes)} change{'s' if len(report.changes) != 1 else ''}"
            before, after = vtag(report.from_version), vtag(report.to_version)
        add(f"| {report.display} | {before} | {after} | {state} |")

    for report in bundled:
        label = f"{report.display} _(bundled)_"
        state = ("**failed**" if report.status == "error"
                 else f"{len(report.changes)} change{'s' if len(report.changes) != 1 else ''}")
        add(f"| {label} | {vtag(report.from_version)} | {vtag(report.to_version)} | {state} |")
    add("")

    if bundled:
        add("Bundled components have no PROD deployment of their own; they ship inside "
            "the service listed with them below.")
        add("")

    # --- per service ------------------------------------------------------
    add("## Changes by service")
    add("")

    any_content = False
    for report in [*deployables, *bundled]:
        any_content |= render_service(add, report, org)

    if not any_content:
        add("_No changes found in any service._")
        add("")

    # --- footer -----------------------------------------------------------
    render_footer(add, deployables, bundled, config)
    return "\n".join(lines).rstrip() + "\n"


def render_service(add, report: ServiceReport, org: str) -> bool:
    heading = f"### {report.display}"
    if report.role in ("bundled", "shared"):
        heading += " (bundled)"
    add(heading)

    if report.role in ("bundled", "shared") and report.consumers:
        add("")
        add(f"_Ships inside: {', '.join(report.consumers)}._")

    if report.status == "error":
        add("")
        add(f"> **Could not generate notes for this service.** {report.message}")
        add("")
        return False

    if report.status == "unchanged":
        add("")
        add(f"_No change in this release - {report.message}._")
        add("")
        return False

    add("")
    add(f"`{vtag(report.from_version)}` -> `{vtag(report.to_version)}`")
    add("")

    if not report.changes:
        add("_No user-visible changes; the version moved for release housekeeping only._")
    else:
        grouped: dict[str, list[Change]] = {}
        for change in report.changes:
            grouped.setdefault(change.category, []).append(change)

        ordered = [c for c in CATEGORY_ORDER if c in grouped]
        ordered += [c for c in grouped if c not in CATEGORY_ORDER]

        for category in ordered:
            add(f"**{category}**")
            add("")
            for change in grouped[category]:
                add(f"- {format_change(change, report.repo, org)}")
            add("")

    if report.dep_notes:
        add("<sub>" + " &middot; ".join(report.dep_notes) + "</sub>")
        add("")

    if report.suppressed_total:
        detail = ", ".join(f"{count} {reason}{'' if count == 1 else 's'}"
                           for reason, count in sorted(report.suppressed.items()))
        add(f"<details><summary>{report.suppressed_total} suppressed "
            f"({detail})</summary>")
        add("")
        add("Routine dependency and release-housekeeping commits are collapsed here. "
            "Bundled-library bumps are never suppressed - they appear as their own "
            "section above.")
        add("")
        add("</details>")
        add("")

    return True


def format_change(change: Change, repo: str, org: str) -> str:
    title = strip_conventional_prefix(change.title)
    parts = [title]
    if change.number:
        parts.append(f"([#{change.number}]({change.url}))")
    else:
        parts.append(f"([`{change.shas[0][:8]}`]({change.url}))")

    trailer = []
    if change.author:
        trailer.append(f"@{change.author}" if change.author_is_login else change.author)
    if change.date:
        trailer.append(change.date[:10])
    if trailer:
        parts.append(f"- {' &middot; '.join(trailer)}")
    return " ".join(parts)


def render_footer(add, deployables, bundled, config) -> None:
    add("---")
    add("")
    add("## Notes")
    add("")

    excluded = config.get("excluded") or {}
    if excluded:
        add("**Excluded from this release note**")
        add("")
        for repo, reason in sorted(excluded.items()):
            add(f"- `{repo}` - {reason}")
        add("")

    unchanged = [r for r in deployables if r.status == "unchanged"]
    if unchanged:
        add("**Unchanged in PROD this release**")
        add("")
        for report in unchanged:
            add(f"- {report.display} - {report.message}")
        add("")

    failed = [r for r in [*deployables, *bundled] if r.status == "error"]
    if failed:
        add("**Services that could not be processed**")
        add("")
        for report in failed:
            add(f"- {report.display} - {report.message}")
        add("")

    add("**How this was built**")
    add("")
    add("- Ranges are PROD-to-PROD: every commit between the version production is "
        "running and the version replacing it, including releases that only ever "
        "reached DEV, QA or UAT.")
    add("- Bundled components are resolved by reading the dependency version pinned in "
        "the parent at each tag, preferring `package-lock.json` (what actually shipped) "
        "over the `package.json` range.")
    add("- Change types come from, in order: conventional-commit prefix, PR label, "
        "branch prefix. Anything with none of those lands in **Changes** rather than "
        "being guessed at.")
    add("")


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate PROD-to-PROD release notes for the DMI platform.")
    parser.add_argument("--versions", required=True,
                        help="JSON version map, or @path to a file containing it.")
    parser.add_argument("--release-name", required=True, help="e.g. w33")
    parser.add_argument("--workspace", required=True,
                        help="Directory containing the repository clones.")
    parser.add_argument("--config",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "config.json"))
    parser.add_argument("--output", required=True, help="Markdown file to write.")
    parser.add_argument("--generated-on", default="",
                        help="Date stamp for the header (default: today, UTC).")
    parser.add_argument("--offline", action="store_true",
                        help="Skip all GitHub API calls; use commit metadata only.")
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        fail(f"config not found: {args.config}")
    with open(args.config) as handle:
        config = json.load(handle)

    raw_versions = args.versions
    if raw_versions.startswith("@"):
        path = raw_versions[1:]
        if not os.path.isfile(path):
            fail(f"--versions points at {path}, which does not exist.")
        with open(path) as handle:
            raw_versions = handle.read()

    release_name = args.release_name.strip()
    if not release_name:
        fail("--release-name must not be empty; it names the release and the file.")

    deployables = [d["repo"] for d in config["deployables"]]
    versions = parse_versions(raw_versions, deployables)

    if not os.path.isdir(args.workspace):
        fail(f"--workspace {args.workspace} is not a directory.")

    generated_on = args.generated_on
    if not generated_on:
        from datetime import datetime, timezone
        generated_on = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    gh = GitHub(config["org"], token, offline=args.offline)

    print("Collecting changes...", file=sys.stderr)
    deployable_reports, bundled_reports = build_reports(
        versions, config, args.workspace, gh)

    markdown = render(release_name, deployable_reports, bundled_reports,
                      config, generated_on)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    with open(args.output, "w") as handle:
        handle.write(markdown)

    failed = [r for r in [*deployable_reports, *bundled_reports] if r.status == "error"]
    changed = [r for r in [*deployable_reports, *bundled_reports] if r.status == "changed"]
    print(f"\nWrote {args.output}: {len(changed)} service(s) with changes, "
          f"{len(failed)} failed.", file=sys.stderr)

    # A failed service is reported inside the notes rather than aborting the run,
    # but the exit code still flags that the notes are incomplete.
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
