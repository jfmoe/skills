#!/usr/bin/env node
// sync-registry.mjs
// Regenerate the central third-party ledger from REAL installed state.
//
// Inputs (nothing here is hand-maintained except registry/projects.yaml):
//   - registry/projects.yaml          project paths to scan (the only manual input)
//   - ~/.agents/.skill-lock.json       global install lock (source of global third-party)
//   - <project>/skills-lock.json       per-project install lock (source of project third-party)
//   - registry/upstream/<skill>/meta.yaml   fork provenance
//
// Outputs (generated — never hand-edit):
//   - registry/third-party.md          human-readable ledger
//   - registry/inventory.json          machine-readable ledger
//
// Usage:
//   node skills/manage-skills/scripts/sync-registry.mjs [repoRoot]
//   SKILLS_REPO=/path/to/repo node .../sync-registry.mjs
//
// Output is deterministic (sorted, no timestamps) so reruns produce clean git diffs.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const HOME = os.homedir();

// Sources that mean "this is my own skill", not third-party.
const SELF_SOURCES = new Set(['jfmoe/skills']);
const SELF_URL_FRAGMENT = 'jfmoe/skills';

function expandHome(p) {
  if (!p) return p;
  return p.replace(/^~(?=$|\/)/, HOME);
}

function looksLikeRepo(p) {
  return !!p && fs.existsSync(path.join(p, 'registry')) && fs.existsSync(path.join(p, 'skills'));
}

// Walk up from a starting directory until we find a dir that looks like the repo
// root. Depth-robust: it does not assume how deeply the script is nested, so the
// script keeps working wherever the skill folder is moved.
function findRepoRootUpward(startDir) {
  let dir = path.resolve(startDir);
  for (;;) {
    if (looksLikeRepo(dir)) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return null; // reached the filesystem root
    dir = parent;
  }
}

function resolveRepoRoot() {
  const scriptDir = path.dirname(new URL(import.meta.url).pathname);
  const walked = findRepoRootUpward(scriptDir);
  const candidates = [process.argv[2], process.env.SKILLS_REPO, walked, path.join(HOME, 'Coder/skills')]
    .filter(Boolean)
    .map((c) => path.resolve(expandHome(c)));
  for (const c of candidates) {
    if (looksLikeRepo(c)) return c;
  }
  throw new Error('Could not locate the skills repo root. Pass it as the first argument or set SKILLS_REPO.');
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

// Minimal YAML helpers — only what projects.yaml / meta.yaml need.
function parseProjectsYaml(file) {
  if (!fs.existsSync(file)) return [];
  const out = [];
  for (let raw of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const line = raw.replace(/#.*$/, '').trimEnd();
    const m = line.match(/^\s*-\s*(.+?)\s*$/);
    if (m) out.push(m[1].replace(/^['"]|['"]$/g, ''));
  }
  return out;
}

function parseSimpleYamlMap(file) {
  // Handles top-level `key: value` scalars. A `key: |` block is captured as joined text.
  const obj = {};
  if (!fs.existsSync(file)) return obj;
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    let val = m[2];
    if (val === '|' || val === '>') {
      const block = [];
      while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) {
        block.push(lines[++i].replace(/^\s+/, ''));
      }
      obj[key] = block.join('\n');
    } else {
      obj[key] = val.replace(/^['"]|['"]$/g, '');
    }
  }
  return obj;
}

function isSelf(entry, repoRoot) {
  if (!entry) return false;
  const src = entry.source || '';
  if (SELF_SOURCES.has(src)) return true;
  if ((entry.sourceUrl || '').includes(SELF_URL_FRAGMENT)) return true;
  if (entry.sourceType === 'local') {
    const resolved = path.resolve(expandHome(src));
    if (resolved === repoRoot) return true;
  }
  return false;
}

function shorten(p) {
  return p.startsWith(HOME) ? '~' + p.slice(HOME.length) : p;
}

function mdEscape(s) {
  return String(s ?? '').replace(/\|/g, '\\|');
}

// --- collectors ---

function collectGlobal(repoRoot) {
  const lock = readJson(path.join(HOME, '.agents/.skill-lock.json'));
  const rows = [];
  if (lock && lock.skills) {
    for (const [name, entry] of Object.entries(lock.skills)) {
      if (isSelf(entry, repoRoot)) continue;
      rows.push({
        name,
        source: entry.source || '',
        sourceUrl: entry.sourceUrl || '',
        skillPath: entry.skillPath || '',
        updatedAt: entry.updatedAt || '',
      });
    }
  }
  rows.sort((a, b) => a.name.localeCompare(b.name));
  return rows;
}

function collectProjects(repoRoot) {
  const projects = parseProjectsYaml(path.join(repoRoot, 'registry/projects.yaml'));
  const rows = [];
  const issues = [];
  for (const projRaw of projects) {
    const proj = path.resolve(expandHome(projRaw));
    const lockFile = path.join(proj, 'skills-lock.json');
    if (!fs.existsSync(lockFile)) {
      issues.push({ project: proj, reason: 'no skills-lock.json' });
      continue;
    }
    const lock = readJson(lockFile);
    if (!lock || !lock.skills) {
      issues.push({ project: proj, reason: 'unreadable skills-lock.json' });
      continue;
    }
    for (const [name, entry] of Object.entries(lock.skills)) {
      if (isSelf(entry, repoRoot)) continue;
      rows.push({
        project: proj,
        name,
        source: entry.source || '',
        skillPath: entry.skillPath || '',
      });
    }
  }
  rows.sort((a, b) => a.project.localeCompare(b.project) || a.name.localeCompare(b.name));
  return { rows, issues };
}

function collectForks(repoRoot) {
  const dir = path.join(repoRoot, 'registry/upstream');
  const rows = [];
  if (!fs.existsSync(dir)) return rows;
  for (const name of fs.readdirSync(dir)) {
    const skillDir = path.join(dir, name);
    if (!fs.statSync(skillDir).isDirectory()) continue;
    const meta = parseSimpleYamlMap(path.join(skillDir, 'meta.yaml'));
    rows.push({
      skill: name,
      source: meta.source || '',
      ref: meta.ref || '',
      commit: meta.commit || '',
      upstreamPath: meta.upstream_path || '',
      localPath: meta.local_path || '',
      fetchedAt: meta.fetched_at || '',
    });
  }
  rows.sort((a, b) => a.skill.localeCompare(b.skill));
  return rows;
}

// --- rendering ---

function renderMarkdown({ global, projects, forks }) {
  const L = [];
  L.push('# Third-Party Skills');
  L.push('');
  L.push('> Generated by `skills/manage-skills/scripts/sync-registry.mjs`. Do not edit by hand.');
  L.push('> Refresh: `node skills/manage-skills/scripts/sync-registry.mjs`');
  L.push('');

  L.push('## Global third-party');
  L.push('');
  if (global.length === 0) {
    L.push('_None._');
  } else {
    L.push('| Skill | Source | Skill Path |');
    L.push('| --- | --- | --- |');
    for (const r of global) {
      L.push(`| ${mdEscape(r.name)} | ${mdEscape(r.source)} | ${mdEscape(r.skillPath)} |`);
    }
  }
  L.push('');

  L.push('## Project third-party');
  L.push('');
  if (projects.rows.length === 0) {
    L.push('_None._');
  } else {
    L.push('| Project | Skill | Source | Skill Path |');
    L.push('| --- | --- | --- | --- |');
    for (const r of projects.rows) {
      L.push(`| ${mdEscape(shorten(r.project))} | ${mdEscape(r.name)} | ${mdEscape(r.source)} | ${mdEscape(r.skillPath)} |`);
    }
  }
  if (projects.issues.length) {
    L.push('');
    L.push('### Scan notes');
    L.push('');
    for (const it of projects.issues) {
      L.push(`- \`${shorten(it.project)}\`: ${it.reason}`);
    }
  }
  L.push('');

  L.push('## Forks (modified third-party)');
  L.push('');
  if (forks.length === 0) {
    L.push('_None._');
  } else {
    L.push('| Skill | Local Path | Upstream | Ref | Fetched |');
    L.push('| --- | --- | --- | --- | --- |');
    for (const r of forks) {
      L.push(`| ${mdEscape(r.skill)} | ${mdEscape(r.localPath)} | ${mdEscape(r.source)} | ${mdEscape(r.ref || r.commit)} | ${mdEscape(r.fetchedAt)} |`);
    }
  }
  L.push('');
  return L.join('\n');
}

// --- main ---

const repoRoot = resolveRepoRoot();
const global = collectGlobal(repoRoot);
const projects = collectProjects(repoRoot);
const forks = collectForks(repoRoot);

const md = renderMarkdown({ global, projects, forks });
const inventory = {
  generatedBy: 'skills/manage-skills/scripts/sync-registry.mjs',
  globalThirdParty: global,
  projectThirdParty: projects.rows,
  projectScanIssues: projects.issues,
  forks,
};

fs.writeFileSync(path.join(repoRoot, 'registry/third-party.md'), md);
fs.writeFileSync(path.join(repoRoot, 'registry/inventory.json'), JSON.stringify(inventory, null, 2) + '\n');

console.error(
  `synced registry: ${global.length} global, ${projects.rows.length} project, ${forks.length} fork(s); ` +
    `${projects.issues.length} scan note(s)`,
);
