// build-ledger.mjs
// Pure core of the registry sync: text in, YAML string out. No filesystem, no
// process.env, no side effects on import. The thin shell (sync-registry.mjs)
// reads the files, calls buildLedger, and writes the single registry/ledger.yaml.
//
// Input snapshot shape (all file contents already read as text):
//   {
//     homeDir:        string,            // for resolving ~ in local sources
//     repoRoot:       string,            // for the local-source self check
//     globalLockText: string | null,     // ~/.agents/.skill-lock.json
//     projects:       [{ path, lockText: string | null }],  // resolved dir + its skills-lock.json
//     forks:          [{ skill, metaText: string }],         // registry/upstream/<skill>/meta.yaml
//   }

import path from 'node:path';

// Sources that mean "this is my own skill", not third-party.
const SELF_SOURCES = new Set(['jfmoe/skills']);
const SELF_URL_FRAGMENT = 'jfmoe/skills';

// The shell that writes the ledger; recorded in the ledger header.
export const GENERATED_BY = 'skills/manage-skills/scripts/sync-registry.mjs';

function expandHome(p, homeDir) {
  if (!p) return p;
  return p.replace(/^~(?=$|\/)/, homeDir);
}

function parseJson(text) {
  if (text == null) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// --- parsers (pure, text in) ------------------------------------------------

// projects.yaml is a flat YAML list of paths. Strips comments and quotes.
export function parseProjectsYaml(text) {
  const out = [];
  for (const raw of (text || '').split(/\r?\n/)) {
    const line = raw.replace(/#.*$/, '').trimEnd();
    const m = line.match(/^\s*-\s*(.+?)\s*$/);
    if (m) out.push(m[1].replace(/^['"]|['"]$/g, ''));
  }
  return out;
}

// meta.yaml is a top-level `key: value` map. A `key: |` (or `>`) block scalar is
// captured as joined text. (notes is parsed but intentionally absent from the
// ledger — it is human provenance, not inventory data.)
export function parseMetaYaml(text) {
  const obj = {};
  if (!text) return obj;
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    const val = m[2];
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

// --- classification ---------------------------------------------------------

export function isSelf(entry, repoRoot, homeDir) {
  if (!entry) return false;
  const src = entry.source || '';
  if (SELF_SOURCES.has(src)) return true;
  if ((entry.sourceUrl || '').includes(SELF_URL_FRAGMENT)) return true;
  if (entry.sourceType === 'local') {
    const resolved = path.resolve(expandHome(src, homeDir));
    if (resolved === repoRoot) return true;
  }
  return false;
}

// --- collectors (snapshot in, camelCase rows out) ---------------------------

function collectGlobal(raw) {
  const lock = parseJson(raw.globalLockText);
  const rows = [];
  if (lock && lock.skills) {
    for (const [name, entry] of Object.entries(lock.skills)) {
      if (isSelf(entry, raw.repoRoot, raw.homeDir)) continue;
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

function collectProjects(raw) {
  const rows = [];
  const issues = [];
  for (const { path: proj, lockText } of raw.projects || []) {
    if (lockText == null) {
      issues.push({ project: proj, reason: 'no skills-lock.json' });
      continue;
    }
    const lock = parseJson(lockText);
    if (!lock || !lock.skills) {
      issues.push({ project: proj, reason: 'unreadable skills-lock.json' });
      continue;
    }
    for (const [name, entry] of Object.entries(lock.skills)) {
      if (isSelf(entry, raw.repoRoot, raw.homeDir)) continue;
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

function collectForks(raw) {
  const rows = (raw.forks || []).map(({ skill, metaText }) => {
    const meta = parseMetaYaml(metaText);
    return {
      skill,
      source: meta.source || '',
      ref: meta.ref || '',
      commit: meta.commit || '',
      upstreamPath: meta.upstream_path || '',
      localPath: meta.local_path || '',
      fetchedAt: meta.fetched_at || '',
    };
  });
  rows.sort((a, b) => a.skill.localeCompare(b.skill));
  return rows;
}

// Assemble the four record sets (camelCase, mirroring the old inventory.json).
// Exported so the golden test can compare records directly.
export function assembleLedger(raw) {
  const globalThirdParty = collectGlobal(raw);
  const { rows: projectThirdParty, issues: projectScanIssues } = collectProjects(raw);
  const forks = collectForks(raw);
  return { globalThirdParty, projectThirdParty, projectScanIssues, forks };
}

// --- YAML emitter (hand-rolled, zero deps) ----------------------------------
// Rule: every scalar is double-quoted and escaped. No "does this need quoting"
// heuristics. Handles our document shape only: a top-level map whose values are
// scalars, empty arrays, or arrays of flat maps.

function quoteScalar(value) {
  const escaped = String(value ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t');
  return `"${escaped}"`;
}

export function emitYaml(doc) {
  const lines = [];
  for (const [key, value] of Object.entries(doc)) {
    if (Array.isArray(value)) {
      if (value.length === 0) {
        lines.push(`${key}: []`);
        continue;
      }
      lines.push(`${key}:`);
      for (const item of value) {
        Object.entries(item).forEach(([k, v], idx) => {
          lines.push(`${idx === 0 ? '  - ' : '    '}${k}: ${quoteScalar(v)}`);
        });
      }
    } else {
      lines.push(`${key}: ${quoteScalar(value)}`);
    }
  }
  return lines.join('\n') + '\n';
}

// --- public entry points ----------------------------------------------------

// Render already-assembled records to the YAML ledger (snake_case keys, full
// field set). Split from buildLedger so a caller that already has the records
// (e.g. the shell, which also wants the row counts) renders without re-running
// the collectors.
export function renderLedger(records) {
  const { globalThirdParty, projectThirdParty, projectScanIssues, forks } = records;
  return emitYaml({
    generated_by: GENERATED_BY,
    global_third_party: globalThirdParty.map((r) => ({
      name: r.name,
      source: r.source,
      source_url: r.sourceUrl,
      skill_path: r.skillPath,
      updated_at: r.updatedAt,
    })),
    project_third_party: projectThirdParty.map((r) => ({
      project: r.project,
      name: r.name,
      source: r.source,
      skill_path: r.skillPath,
    })),
    project_scan_issues: projectScanIssues.map((r) => ({
      project: r.project,
      reason: r.reason,
    })),
    forks: forks.map((r) => ({
      skill: r.skill,
      source: r.source,
      ref: r.ref,
      commit: r.commit,
      upstream_path: r.upstreamPath,
      local_path: r.localPath,
      fetched_at: r.fetchedAt,
    })),
  });
}

export function buildLedger(raw) {
  return renderLedger(assembleLedger(raw));
}
