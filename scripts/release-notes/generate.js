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
  let outPath = process.env.OUT || null;
  let startDate = process.env.START_DATE || null;
  let endDate = process.env.END_DATE || null;

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
      else if (flag === '--out') outPath = val;
      else throw new Error(`Unknown option: ${flag}`);
    }
  }

  if (!startDate) throw new Error('START_DATE is required (YYYY-MM-DD).');
  if (!isValidDateStr(startDate)) throw new Error('Invalid START_DATE. Expected YYYY-MM-DD.');
  if (!endDate) endDate = toYMD(new Date());
  if (!isValidDateStr(endDate)) throw new Error('Invalid END_DATE. Expected YYYY-MM-DD.');

  return { owner, repo, outPath, startDate, endDate };
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
    const text = await res.text().catch(() => '');
    throw new Error(`GitHub API error ${res.status}: ${text || res.statusText}`);
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

async function main() {
  let cfg;
  try {
    cfg = parseArgsOrEnv();
  } catch (e) {
    console.error(e.message);
    console.error('Usage (CLI): node scripts/release-notes/generate.js <start: YYYY-MM-DD> [end: YYYY-MM-DD] [--owner OWNER] [--repo REPO] [--out PATH]');
    console.error('Or set env: START_DATE, [END_DATE], [OWNER], [REPO], [OUT]');
    process.exit(1);
    return;
  }

  const token = getAuthToken();

  // Determine repository list: specific repo if provided, else all repos in org
  let repoNames = [];
  if (cfg.repo && cfg.repo.trim()) {
    repoNames = [cfg.repo.trim()];
  } else {
    console.error(`Listing repositories for org ${cfg.owner} ...`);
    try {
      const repos = await listOrgRepos(cfg.owner, token);
      // Include all repos accessible; skip disabled
      repoNames = repos.filter(r => !r.disabled).map(r => r.name);
    } catch (err) {
      console.error('Failed to list organization repositories:', err.message);
      process.exit(2);
      return;
    }
  }

  console.error(`Fetching closed issues from ${cfg.startDate} to ${cfg.endDate} across ${repoNames.length} repo(s)...`);

  const allIssues = [];
  for (const r of repoNames) {
    try {
      const issues = await searchClosedIssues({ owner: cfg.owner, repo: r, startDate: cfg.startDate, endDate: cfg.endDate, token });
      for (const it of issues) {
        allIssues.push({ ...it, repo: `${cfg.owner}/${r}` });
      }
    } catch (err) {
      console.error(`Failed to fetch issues for ${cfg.owner}/${r}: ${err.message}`);
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

  const filename = cfg.outPath && cfg.outPath.trim().length > 0
    ? cfg.outPath
    : path.join(process.cwd(), `DMI-Release-Notes-${cfg.endDate}.md`);

  fs.writeFileSync(filename, lines.join('\n'), 'utf8');
  console.log(`Wrote ${allIssues.length} issues to ${filename}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
