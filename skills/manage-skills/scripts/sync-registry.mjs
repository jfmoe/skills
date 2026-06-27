#!/usr/bin/env node
// sync-registry.mjs
// Thin IO shell around build-ledger.mjs: discover + read the input files, hand
// their text to the pure core, and write the single registry/ledger.yaml.
//
// Inputs (nothing here is hand-maintained except registry/projects.yaml):
//   - registry/projects.yaml                project paths to scan (the only manual input)
//   - ~/.agents/.skill-lock.json            global install lock (source of global third-party)
//   - <project>/skills-lock.json            per-project install lock (source of project third-party)
//   - registry/upstream/<skill>/meta.yaml   fork provenance
//
// Output (generated — never hand-edit):
//   - registry/ledger.yaml                  single YAML ledger (full field set)
//
// Usage:
//   node skills/manage-skills/scripts/sync-registry.mjs [repoRoot]
//   SKILLS_REPO=/path/to/repo node .../sync-registry.mjs
//
// Output is deterministic (sorted, no timestamps) so reruns produce clean git diffs.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

import { assembleLedger, buildLedger, parseProjectsYaml } from './build-ledger.mjs';

const HOME = os.homedir();

function expandHome(p) {
  if (!p) return p;
  return p.replace(/^~(?=$|\/)/, HOME);
}

function readTextOrNull(file) {
  try {
    return fs.readFileSync(file, 'utf8');
  } catch {
    return null;
  }
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

// Read every input file as text and assemble the snapshot the pure core expects.
function readSnapshot(repoRoot) {
  const globalLockText = readTextOrNull(path.join(HOME, '.agents/.skill-lock.json'));

  const projectPaths = parseProjectsYaml(readTextOrNull(path.join(repoRoot, 'registry/projects.yaml')) || '');
  const projects = projectPaths.map((projRaw) => {
    const proj = path.resolve(expandHome(projRaw));
    return { path: proj, lockText: readTextOrNull(path.join(proj, 'skills-lock.json')) };
  });

  const forks = [];
  const upstreamDir = path.join(repoRoot, 'registry/upstream');
  if (fs.existsSync(upstreamDir)) {
    for (const name of fs.readdirSync(upstreamDir)) {
      const skillDir = path.join(upstreamDir, name);
      if (!fs.statSync(skillDir).isDirectory()) continue;
      const metaText = readTextOrNull(path.join(skillDir, 'meta.yaml'));
      if (metaText == null) continue;
      forks.push({ skill: name, metaText });
    }
  }

  return { homeDir: HOME, repoRoot, globalLockText, projects, forks };
}

// --- main ---

const repoRoot = resolveRepoRoot();
const snapshot = readSnapshot(repoRoot);

fs.writeFileSync(path.join(repoRoot, 'registry/ledger.yaml'), buildLedger(snapshot));

const { globalThirdParty, projectThirdParty, projectScanIssues, forks } = assembleLedger(snapshot);
console.error(
  `synced registry: ${globalThirdParty.length} global, ${projectThirdParty.length} project, ${forks.length} fork(s); ` +
    `${projectScanIssues.length} scan note(s)`,
);
