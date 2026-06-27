import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  buildLedger,
  assembleLedger,
  renderLedger,
  parseProjectsYaml,
  parseMetaYaml,
  isSelf,
  emitYaml,
} from '../skills/manage-skills/scripts/build-ledger.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const readFixture = (name) => JSON.parse(fs.readFileSync(path.join(here, 'fixtures', name), 'utf8'));

// --- Golden / characterization test -----------------------------------------
// Feed the captured live snapshot and assert the assembled records equal the
// records the pre-refactor script recorded in inventory.json. This is the
// regression net for the format change (md + json -> single ledger.yaml).
test('golden: assembleLedger reproduces the pre-refactor inventory records', () => {
  const snapshot = readFixture('ledger-snapshot.json');
  const expected = readFixture('expected-ledger-records.json');
  const got = assembleLedger(snapshot);

  assert.deepEqual(got.globalThirdParty, expected.globalThirdParty);
  assert.deepEqual(got.projectThirdParty, expected.projectThirdParty);
  assert.deepEqual(got.projectScanIssues, expected.projectScanIssues);
  assert.deepEqual(got.forks, expected.forks);
});

test('golden: buildLedger returns a YAML string with the expected top-level sections', () => {
  const snapshot = readFixture('ledger-snapshot.json');
  const yaml = buildLedger(snapshot);
  assert.equal(typeof yaml, 'string');
  assert.match(yaml, /^generated_by: "skills\/manage-skills\/scripts\/sync-registry\.mjs"$/m);
  assert.match(yaml, /^global_third_party:$/m);
  assert.match(yaml, /^project_third_party:$/m);
  assert.match(yaml, /^forks:$/m);
  // empty section renders as `key: []`
  assert.match(yaml, /^project_scan_issues: \[\]$/m);
});

test('renderLedger: renders assembled records to snake_case YAML without re-collecting', () => {
  const records = {
    globalThirdParty: [{ name: 'x', source: 's', sourceUrl: 'u', skillPath: 'p', updatedAt: 't' }],
    projectThirdParty: [],
    projectScanIssues: [],
    forks: [],
  };
  const yaml = renderLedger(records);
  assert.match(yaml, /^global_third_party:$/m);
  assert.match(yaml, /^ {4}source_url: "u"$/m); // camelCase -> snake_case key
  assert.match(yaml, /^project_third_party: \[\]$/m);
  assert.match(yaml, /^forks: \[\]$/m);
});

// --- isSelf: all three self-detection paths + a clear third-party ------------
const REPO = '/Users/jfmoe/Coder/skills';
const HOME = '/Users/jfmoe';

test('isSelf: source matches the self source', () => {
  assert.equal(isSelf({ source: 'jfmoe/skills' }, REPO, HOME), true);
});

test('isSelf: sourceUrl contains the self fragment', () => {
  assert.equal(isSelf({ sourceUrl: 'https://github.com/jfmoe/skills.git' }, REPO, HOME), true);
});

test('isSelf: local sourceType resolving to the repo root', () => {
  assert.equal(isSelf({ sourceType: 'local', source: '~/Coder/skills' }, REPO, HOME), true);
  assert.equal(isSelf({ sourceType: 'local', source: '/Users/jfmoe/Coder/skills' }, REPO, HOME), true);
});

test('isSelf: a clear third-party entry is not self', () => {
  assert.equal(isSelf({ source: 'mattpocock/skills', sourceUrl: 'https://github.com/mattpocock/skills.git' }, REPO, HOME), false);
  assert.equal(isSelf({ sourceType: 'local', source: '/somewhere/else' }, REPO, HOME), false);
  assert.equal(isSelf(null, REPO, HOME), false);
});

// --- YAML map parser (the `notes: |` block) ---------------------------------
test('parseMetaYaml: scalars and a `notes: |` block', () => {
  const text = [
    'source: owner/repo',
    'ref: main',
    'commit: abc123',
    'local_path: skills/foo',
    'fetched_at: 2026-06-27',
    'notes: |',
    '  - first line',
    '  - second line',
  ].join('\n');
  const meta = parseMetaYaml(text);
  assert.equal(meta.source, 'owner/repo');
  assert.equal(meta.commit, 'abc123');
  assert.equal(meta.local_path, 'skills/foo');
  assert.equal(meta.notes, '- first line\n- second line');
});

test('parseMetaYaml: strips surrounding quotes and tolerates empty text', () => {
  assert.deepEqual(parseMetaYaml(''), {});
  assert.equal(parseMetaYaml('source: "owner/repo"').source, 'owner/repo');
});

// --- YAML emitter: quote/escape, spaces, empty string, empty list -----------
test('emitYaml: escapes quotes and backslashes', () => {
  assert.equal(emitYaml({ k: 'a"b\\c' }), 'k: "a\\"b\\\\c"\n');
});

test('emitYaml: a value with spaces is still double-quoted', () => {
  assert.equal(emitYaml({ k: 'has spaces' }), 'k: "has spaces"\n');
});

test('emitYaml: empty string renders as ""', () => {
  assert.equal(emitYaml({ k: '' }), 'k: ""\n');
});

test('emitYaml: empty list renders as key: []', () => {
  assert.equal(emitYaml({ k: [] }), 'k: []\n');
});

test('emitYaml: a list of flat maps indents under a dash', () => {
  assert.equal(emitYaml({ items: [{ a: '1', b: '2' }] }), 'items:\n  - a: "1"\n    b: "2"\n');
});

// --- parseProjectsYaml -------------------------------------------------------
test('parseProjectsYaml: reads list items, strips comments and quotes', () => {
  const text = [
    '# header comment',
    'projects:',
    '  - ~/Coder/Aizo',
    '  - "/Users/jfmoe/Coder/voxlab"  # inline comment',
    '  - ~/Coder/persona',
  ].join('\n');
  assert.deepEqual(parseProjectsYaml(text), ['~/Coder/Aizo', '/Users/jfmoe/Coder/voxlab', '~/Coder/persona']);
});

test('parseProjectsYaml: empty text yields no projects', () => {
  assert.deepEqual(parseProjectsYaml(''), []);
});
