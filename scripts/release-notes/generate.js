#!/usr/bin/env node
// Generate release notes from GitHub issues closed between dates.
// CLI usage: node scripts/release-notes/generate.js <start: YYYY-MM-DD> [end: YYYY-MM-DD] [--owner OWNER] [--repo REPO] [--out PATH]
// Env usage (for scripts/run.js):
//   START_DATE (required), END_DATE, OWNER, REPO, OUT, GITHUB_TOKEN

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function isValidDateStr(s) {
  return /^\d{4}-\d{2}-\d{2}$/.test(s);
}

function toYMD(date) {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, '0');
  const d = String(date.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function parseArgsOrEnv() {
  const argv = process.argv.slice(2);
  let owner = process.env.OWNER || process.env.ORG || 'nominal-systems';
  let repo = process.env.REPO || '';
  let startDate = process.env.START_DATE || null;
  let endDate = process.env.END_DATE || null;
  let filePath = process.env.FILE || process.env.OUT || null; // OUT kept for compatibility

  if (argv.length >= 1) {
    startDate = argv[0];
    if (argv[1] && !argv[1].startsWith('--')) {
      endDate = argv[1];
    }
    for (let i = 2; i < argv.length; i += 2) {
      const flag = argv[i];
      const val = argv[i + 1];
      if (!flag) break;
      if (!val || val.startsWith('--')) throw new Error(`Missing value for option ${flag}`);
      if (flag === '--owner') owner = val;
      else if (flag === '--repo') repo = val;
      else if (flag === '--file' || flag === '--out') filePath = val;
      else throw new Error(`Unknown option: ${flag}`);
    }
  }

  if (startDate && !isValidDateStr(startDate)) throw new Error('Invalid START_DATE. Expected YYYY-MM-DD.');
  if (!endDate) endDate = toYMD(new Date());
  if (!isValidDateStr(endDate)) throw new Error('Invalid END_DATE. Expected YYYY-MM-DD.');

  return { owner, repo, startDate, endDate, filePath };
}

async function ghFetch(url, token) {
  const headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'dmi-release-notes-script'
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  if (typeof fetch !== 'function') {
    throw new Error('Global fetch is unavailable. Use Node.js 18+ or add a fetch polyfill.');
  }

  const res = await fetch(url, { headers });
  if (!res.ok) {
    const raw = await res.text().catch(() => '');
    let apiMsg = '';
    try {
      const j = JSON.parse(raw);
      if (j && typeof j.message === 'string') apiMsg = j.message;
    } catch {}

    const h = (name) => {
      try { return res.headers.get(name); } catch { return null; }
    };
    const status = res.status;
    const retryAfter = h('Retry-After');
    const rateReset = h('X-RateLimit-Reset');

    let retryAfterSeconds = null;
    let retryAtIso = null;
    let retryAtMs = null;
    if (status === 429 || status === 403) {
      if (retryAfter) {
        if (/^\d+$/.test(retryAfter)) {
          retryAfterSeconds = parseInt(retryAfter, 10);
          retryAtMs = Date.now() + retryAfterSeconds * 1000;
          retryAtIso = new Date(retryAtMs).toISOString();
        } else {
          const d = new Date(retryAfter);
          if (!isNaN(d.getTime())) {
            retryAtMs = d.getTime();
            retryAtIso = d.toISOString();
            retryAfterSeconds = Math.max(0, Math.round((retryAtMs - Date.now()) / 1000));
          }
        }
      } else if (rateReset) {
        const epochSec = parseInt(rateReset, 10);
        if (!Number.isNaN(epochSec)) {
          retryAtMs = epochSec * 1000;
          retryAtIso = new Date(retryAtMs).toISOString();
          retryAfterSeconds = Math.max(0, Math.round((retryAtMs - Date.now()) / 1000));
        }
      }
    }

    const baseMsg = apiMsg || raw || res.statusText || 'Unknown error';
    const err = new Error(`GitHub API error ${status}: ${baseMsg}`);
    err.status = status;
    err.retryAfterSeconds = retryAfterSeconds;
    err.retryAtIso = retryAtIso;
    err.retryAtMs = retryAtMs;
    throw err;
  }
  return res.json();
}

async function searchClosedIssues({ owner, repo, startDate, endDate, token }) {
  const perPage = 100;
  let page = 1;
  let items = [];
  const base = `https://api.github.com/search/issues`;
  const q = encodeURIComponent(`repo:${owner}/${repo} is:issue is:closed closed:${startDate}..${endDate}`);

  while (true) {
    const url = `${base}?q=${q}&per_page=${perPage}&page=${page}`;
    const data = await ghFetch(url, token);
    const batch = Array.isArray(data.items) ? data.items : [];
    items = items.concat(batch);
    if (batch.length < perPage) break;
    if (items.length >= 1000) break; // Search API cap safeguard
    page += 1;
  }

  const simplified = items
    .map(i => ({ number: i.number, title: i.title, url: i.html_url, closed_at: i.closed_at }))
    .sort((a, b) => new Date(b.closed_at) - new Date(a.closed_at));

  return simplified;
}

function getAuthToken() {
  const envToken = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  if (envToken && envToken.trim()) return envToken.trim();
  try {
    const out = execSync('gh auth token', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    if (out) return out;
  } catch (_) {
    // gh not available or not logged in
  }
  return '';
}

async function listOrgRepos(org, token) {
  const perPage = 100;
  let page = 1;
  let repos = [];
  while (true) {
    const url = `https://api.github.com/orgs/${encodeURIComponent(org)}/repos?per_page=${perPage}&page=${page}`;
    const data = await ghFetch(url, token);
    if (!Array.isArray(data) || data.length === 0) break;
    repos = repos.concat(data.map(r => ({ name: r.name, archived: !!r.archived, disabled: !!r.disabled, fork: !!r.fork })));
    if (data.length < perPage) break;
    page += 1;
  }
  return repos;
}

function humanizeSeconds(sec) {
  if (sec == null || !isFinite(sec)) return null;
  const s = Math.max(0, Math.round(sec));
  const parts = [];
  const days = Math.floor(s / 86400);
  let rem = s % 86400;
  const hours = Math.floor(rem / 3600);
  rem = rem % 3600;
  const minutes = Math.floor(rem / 60);
  const seconds = rem % 60;
  if (days) parts.push(`${days}d`);
  if (hours) parts.push(`${hours}h`);
  if (minutes) parts.push(`${minutes}m`);
  if (seconds || parts.length === 0) parts.push(`${seconds}s`);
  return parts.join(' ');
}

function formatLocalDateTime(ms) {
  if (ms == null) return null;
  const d = new Date(ms);
  if (isNaN(d.getTime())) return null;
  const pad = (n) => String(n).padStart(2, '0');
  const y = d.getFullYear();
  const m = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hh = pad(d.getHours());
  const mm = pad(d.getMinutes());
  const ss = pad(d.getSeconds());
  const tzMin = -d.getTimezoneOffset();
  const sign = tzMin >= 0 ? '+' : '-';
  const tzH = pad(Math.floor(Math.abs(tzMin) / 60));
  const tzM = pad(Math.abs(tzMin) % 60);
  return `${y}-${m}-${day} ${hh}:${mm}:${ss} ${sign}${tzH}:${tzM}`;
}

async function main() {
  let cfg;
  try {
    cfg = parseArgsOrEnv();
  } catch (e) {
    console.error(e.message);
    console.error('Usage (CLI): node scripts/release-notes/generate.js [start: YYYY-MM-DD] [end: YYYY-MM-DD] [--owner OWNER] [--repo REPO]');
    console.error('Or set env: [START_DATE], [END_DATE], [OWNER], [REPO]');
    process.exit(1);
    return;
  }

  const token = getAuthToken();

  // Resolve repo root and output path (default RELEASE_NOTES.md at repo root)
  const repoRoot = path.resolve(__dirname, '..', '..');
  let outFile = path.join(repoRoot, 'RELEASE_NOTES.md');
  if (cfg.filePath && cfg.filePath.trim().length > 0) {
    outFile = path.isAbsolute(cfg.filePath) ? cfg.filePath : path.join(repoRoot, cfg.filePath);
  }

  // If no start date provided, try to infer from the chosen output file
  if (!cfg.startDate) {
    try {
      const existing = fs.readFileSync(outFile, 'utf8');
      const m = existing.match(/^#\s+DMI Release Notes\s+(\d{4}-\d{2}-\d{2})/m);
      if (m) {
        cfg.startDate = m[1];
        console.error(`Inferred START_DATE=${cfg.startDate} from ${path.relative(repoRoot, outFile)}`);
      } else {
        throw new Error(`No previous release date found in ${outFile}`);
      }
    } catch (err) {
      console.error(`START_DATE not provided and could not infer from ${path.relative(repoRoot, outFile)}.`);
      console.error('Provide START_DATE or create the file with a header like:');
      console.error('# DMI Release Notes YYYY-MM-DD');
      process.exit(1);
      return;
    }
  }

  let currentAction = `list repositories for ${cfg.owner}`;
  try {
    // Determine repository list: specific repo if provided, else all repos in org
    let repoNames = [];
    if (cfg.repo && cfg.repo.trim()) {
      repoNames = [cfg.repo.trim()];
    } else {
      console.error(`Listing repositories for org ${cfg.owner} ...`);
      const repos = await listOrgRepos(cfg.owner, token);
      repoNames = repos.filter(r => !r.disabled).map(r => r.name);
    }

    console.error(`Fetching closed issues from ${cfg.startDate} to ${cfg.endDate} across ${repoNames.length} repo(s)...`);

    // Atomic aggregation: if any request fails, abort without writing
    var allIssues = [];
    for (const r of repoNames) {
      currentAction = `fetch issues for ${cfg.owner}/${r}`;
      const issues = await searchClosedIssues({ owner: cfg.owner, repo: r, startDate: cfg.startDate, endDate: cfg.endDate, token });
      for (const it of issues) {
        allIssues.push({ ...it, repo: `${cfg.owner}/${r}` });
      }
    }

    // Sort across repos by closed_at desc
    allIssues.sort((a, b) => new Date(b.closed_at) - new Date(a.closed_at));

    const lines = [];
    lines.push(`# DMI Release Notes ${cfg.endDate}`);
    lines.push('');
    if (allIssues.length === 0) {
      lines.push(`- No closed issues between ${cfg.startDate} and ${cfg.endDate}.`);
    } else {
      for (const it of allIssues) {
        lines.push(`- ${it.repo} [#${it.number}](${it.url}) ${it.title}`);
      }
    }
    lines.push('');

    const newBlock = lines.join('\n');
    let finalContent = newBlock;
    if (fs.existsSync(outFile)) {
      const existing = fs.readFileSync(outFile, 'utf8');
      finalContent = `${newBlock}\n${existing}`;
    }
    fs.writeFileSync(outFile, finalContent, 'utf8');
    console.log(`Prepended ${allIssues.length} issues to ${outFile}`);
    return;
  } catch (err) {
    console.error(`Sorry, I couldn't ${currentAction}.`);
    if (err && err.message) console.error(err.message);
    if (typeof err?.retryAfterSeconds === 'number' || err?.retryAtIso) {
      const pretty = humanizeSeconds(err.retryAfterSeconds);
      const when = formatLocalDateTime(err.retryAtMs) || err.retryAtIso || '';
      if (pretty || when) {
        console.error(`Rate limit encountered. Please retry in ~${pretty || 'a moment'}${when ? ` (at ${when})` : ''}.`);
      }
    }
    console.error(`No changes were made to ${path.relative(repoRoot, outFile)}.`);
    process.exit(2);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
