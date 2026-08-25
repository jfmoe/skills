#!/usr/bin/env node

import { createHash } from 'node:crypto'
import { spawnSync } from 'node:child_process'
import { existsSync, lstatSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const bundleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const repositoryRoot = resolve(bundleRoot, '../../..')
const pinnedCommit = 'b150a551b8d465e31e418e1b2eaf5e79bbb7d28e'
const expectedSkills = new Set([
  'apply-documentation-standards',
  'audit-code-simplifications',
  'plan-code-changes',
  'review-code-changes',
  'review-code-prose',
  'select-relevant-checks',
  'trim-cot-leakage',
])
const instructionBasenames = new Set([
  'AGENTS.md',
  'CLAUDE.md',
  'GEMINI.md',
  'CODEX.md',
  'COPILOT.md',
  'CURSOR.md',
  'WINDSURF.md',
  'AIDER.md',
  'QWEN.md',
  'KIMI.md',
])
const allowedDispositions = new Set([
  'adapted-general',
  'adapted-project-guardrail',
  'adapted-review-maintenance',
  'adapted-review-response',
  'excluded-display-metadata',
  'excluded-fixture',
  'excluded-product-evidence-workflow',
  'excluded-product-specific-skill',
  'excluded-remote-mutation-workflow',
  'fork-apply-documentation-standards',
  'fork-audit-code-simplifications',
  'fork-plan-code-changes',
  'fork-review-code-changes',
  'fork-review-code-prose',
  'fork-select-relevant-checks',
  'fork-trim-cot-leakage',
  'legal',
  'reference-preset',
  'reference-symlink-instruction',
  'reference-symlink-skill-root',
  'reference-project-process',
  'reference-project-specific',
  'reference-translation',
  'source-support',
])

function fail(message) {
  failures.push(message)
}

function parseOptions(argv) {
  if (argv.length === 0) return {}
  if (argv.length === 2 && argv[0] === '--upstream' && argv[1] !== '') {
    return { upstream: resolve(argv[1]) }
  }
  throw new Error('usage: verify-review-bundle.mjs [--upstream <repository>]')
}

function runUpstreamGit(root, args, buffer = false) {
  const result = spawnSync('git', ['-C', root, ...args], {
    encoding: buffer ? undefined : 'utf8',
    maxBuffer: 20 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  if (result.status !== 0) {
    const stderr = buffer ? result.stderr.toString('utf8') : result.stderr
    throw new Error(stderr.trim() || `git ${args.join(' ')} failed`)
  }
  return result.stdout
}

function upstreamPromptSurface(paths) {
  return new Set(paths.filter((path) => {
    const basename = path.split('/').at(-1)
    return instructionBasenames.has(basename) ||
      path === '.claude/skills' ||
      basename === 'SKILL.md' ||
      path.startsWith('apps/cli/config/agent-presets/') ||
      /prompt|instruction/i.test(basename)
  }))
}

function verifyPinnedUpstream(upstreamRoot, sourceRows, scanRows) {
  runUpstreamGit(upstreamRoot, ['rev-parse', '--verify', `${pinnedCommit}^{commit}`])

  const records = runUpstreamGit(
    upstreamRoot,
    ['ls-tree', '-r', '-z', pinnedCommit],
  ).split('\0').filter(Boolean)
  const tree = new Map()
  for (const record of records) {
    const match = /^(\d+)\s+(\w+)\s+([0-9a-f]{40})\t([\s\S]+)$/.exec(record)
    if (match === null) throw new Error('invalid git ls-tree record')
    tree.set(match[4], { mode: match[1], type: match[2], sha: match[3] })
  }

  for (const row of sourceRows) {
    const entry = tree.get(row.source_path)
    if (entry === undefined || entry.type !== 'blob') {
      fail('pinned tree is missing source path: ' + row.source_path)
      continue
    }
    if (entry.sha !== row.blob_sha) {
      fail('pinned tree blob SHA differs: ' + row.source_path)
    }
    const upstream = runUpstreamGit(
      upstreamRoot,
      ['cat-file', 'blob', entry.sha],
      true,
    )
    const mirror = readFileSync(resolve(repositoryRoot, row.mirror_path))
    if (!upstream.equals(mirror)) {
      fail('pinned tree bytes differ from mirror: ' + row.source_path)
    }
  }

  const treePaths = [...tree.keys()]
  const recordedScan = new Set(scanRows.map((row) => row.path))
  const expectedScan = upstreamPromptSurface(treePaths)
  for (const path of expectedScan) {
    if (!recordedScan.has(path)) fail('prompt-surface scan is missing: ' + path)
  }
  for (const path of recordedScan) {
    if (!expectedScan.has(path)) fail('prompt-surface scan has an extra path: ' + path)
  }

  const sourcePaths = new Set(sourceRows.map((row) => row.source_path))
  const families = [
    ['repository Skill tree', treePaths.filter((path) => path.startsWith('.agents/skills/'))],
    ['shipped preset tree', treePaths.filter((path) => path.startsWith('apps/cli/config/agent-presets/'))],
    [
      'standing instruction entrypoints',
      treePaths.filter((path) => instructionBasenames.has(path.split('/').at(-1)) || path === '.claude/skills'),
    ],
  ]
  for (const [name, paths] of families) {
    for (const path of paths) {
      if (!sourcePaths.has(path)) fail(name + ' is missing from source manifest: ' + path)
    }
  }

  if (failures.length === 0) {
    console.log(
      'review-bundle upstream: ' + sourceRows.length + ' sources, ' +
      scanRows.length + ' scan paths, and all instruction/Skill/preset entrypoints verified',
    )
  }
}

function parseTsv(path) {
  const lines = readFileSync(path, 'utf8').trimEnd().split('\n')
  const headers = lines[0].split('\t')
  return lines.slice(1).map((line, lineIndex) => {
    const fields = line.split('\t')
    if (fields.length !== headers.length) {
      throw new Error(
        relative(bundleRoot, path) + ':' + (lineIndex + 2) + ' has ' +
        fields.length + ' fields; expected ' + headers.length,
      )
    }
    return Object.fromEntries(headers.map((header, index) => [header, fields[index]]))
  })
}

function gitBlobHash(buffer) {
  return createHash('sha1')
    .update(Buffer.from('blob ' + buffer.length + '\0'))
    .update(buffer)
    .digest('hex')
}

function walk(directory) {
  const files = []
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name)
    if (entry.isDirectory()) files.push(...walk(path))
    else if (entry.isFile() || entry.isSymbolicLink()) files.push(path)
  }
  return files
}

function relativeBundle(path) {
  return relative(bundleRoot, path).split('\\').join('/')
}

function isRawEvidence(path) {
  if (path.startsWith('upstream/repository/')) return true
  if (!path.startsWith('artifacts/registry/upstream/')) return false
  const basename = path.split('/').at(-1)
  return !['meta.yaml', 'meta.zh.md', 'SOURCES.md', 'SOURCES.zh.md'].includes(basename)
}

function isProvenance(path) {
  return path.endsWith('/SOURCES.md') ||
    path.endsWith('/SOURCES.zh.md') ||
    path === 'SOURCES.md' ||
    path === 'SOURCES.zh.md'
}

function isStructuredEvidence(path) {
  return path === 'audit/source-manifest.tsv' ||
    path === 'audit/prompt-surface-scan.tsv' ||
    path === 'ARTIFACT_INDEX.tsv'
}

function markdownStructure(text) {
  const headings = []
  const fences = []
  let activeFence
  let fenceBody = []

  for (const line of text.split('\n')) {
    const heading = /^(#{1,6})\s+/.exec(line)
    if (heading !== null && activeFence === undefined) headings.push(heading[1].length)

    const fence = /^((?:\x60){3,}|~{3,})(.*)$/.exec(line)
    if (fence !== null) {
      if (activeFence === undefined) {
        activeFence = fence[1][0]
        fenceBody = [line]
      } else if (fence[1][0] === activeFence) {
        fenceBody.push(line)
        fences.push(fenceBody.join('\n'))
        activeFence = undefined
        fenceBody = []
      } else {
        fenceBody.push(line)
      }
    } else if (activeFence !== undefined) {
      fenceBody.push(line)
    }
  }

  return { headings, fences, openFence: activeFence !== undefined }
}

function readSkillName(path) {
  const text = readFileSync(path, 'utf8')
  const match = /^---\nname:\s*([^\n]+)\n/m.exec(text)
  return match?.[1]?.trim()
}

const failures = []

try {
  const options = parseOptions(process.argv.slice(2))
  const sourceRows = parseTsv(resolve(bundleRoot, 'audit/source-manifest.tsv'))
  if (sourceRows.length !== 70) {
    fail('source manifest has ' + sourceRows.length + ' rows; expected 70')
  }

  const sourcePaths = new Set()
  const mirrorPaths = new Set()
  for (const row of sourceRows) {
    if (sourcePaths.has(row.source_path)) fail('duplicate source path: ' + row.source_path)
    if (mirrorPaths.has(row.mirror_path)) fail('duplicate mirror path: ' + row.mirror_path)
    sourcePaths.add(row.source_path)
    mirrorPaths.add(row.mirror_path)

    if (!allowedDispositions.has(row.disposition)) {
      fail('unknown disposition for ' + row.source_path + ': ' + row.disposition)
    }
    if (row.blob_sha.length !== 40) fail('invalid blob SHA for ' + row.source_path)

    const mirror = resolve(repositoryRoot, row.mirror_path)
    if (!existsSync(mirror) || !statSync(mirror).isFile()) {
      fail('missing source mirror: ' + row.mirror_path)
      continue
    }

    const buffer = readFileSync(mirror)
    const actualHash = gitBlobHash(buffer)
    if (actualHash !== row.blob_sha) {
      fail('source mirror hash mismatch: ' + row.mirror_path)
    }

    const actualLines = buffer.length === 0
      ? 0
      : buffer.toString('utf8').replace(/\n$/, '').split('\n').length
    if (String(actualLines) !== row.lines) {
      fail('source mirror line count mismatch: ' + row.mirror_path)
    }
  }

  const scanRows = parseTsv(resolve(bundleRoot, 'audit/prompt-surface-scan.tsv'))
  if (scanRows.length !== 125) {
    fail('prompt-surface scan has ' + scanRows.length + ' rows; expected 125')
  }
  const scanPaths = new Set()
  for (const row of scanRows) {
    if (scanPaths.has(row.path)) fail('duplicate prompt-surface path: ' + row.path)
    scanPaths.add(row.path)
    if (row.disposition === 'in-source-manifest' && !sourcePaths.has(row.path)) {
      fail('scan path claims manifest coverage but is absent: ' + row.path)
    }
  }

  if (options.upstream !== undefined) {
    verifyPinnedUpstream(options.upstream, sourceRows, scanRows)
  }

  const allFiles = walk(bundleRoot).map(relativeBundle).sort()
  for (const path of allFiles) {
    const basename = path.split('/').at(-1)
    if (lstatSync(resolve(bundleRoot, path)).isSymbolicLink()) {
      fail('symbolic link is not allowed in the inactive review bundle: ' + path)
    }
    if (basename === 'SKILL.md' || basename === 'AGENTS.md' || basename === 'CLAUDE.md') {
      fail('discovery-sensitive filename is active: ' + path)
    }
  }

  const skillRoot = resolve(bundleRoot, 'artifacts/skills')
  const actualSkills = new Set(
    readdirSync(skillRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name),
  )
  for (const name of expectedSkills) {
    if (!actualSkills.has(name)) fail('missing candidate Skill: ' + name)
  }
  for (const name of actualSkills) {
    if (!expectedSkills.has(name)) fail('unexpected candidate Skill: ' + name)
  }

  for (const name of expectedSkills) {
    const english = resolve(skillRoot, name, 'SKILL.md.review')
    const chinese = resolve(skillRoot, name, 'SKILL.zh.md.review')
    for (const path of [english, chinese]) {
      if (!existsSync(path)) {
        fail('missing Skill entrypoint: ' + relativeBundle(path))
        continue
      }
      if (readSkillName(path) !== name) {
        fail('Skill name does not match folder: ' + relativeBundle(path))
      }
    }
    for (const path of [
      resolve(skillRoot, name, 'agents/openai.yaml.review'),
      resolve(skillRoot, name, 'agents/openai.zh.yaml.review'),
      resolve(skillRoot, name, 'SOURCES.md'),
      resolve(skillRoot, name, 'SOURCES.zh.md'),
    ]) {
      if (!existsSync(path)) fail('missing Skill companion: ' + relativeBundle(path))
    }
  }

  const artifactRows = parseTsv(resolve(bundleRoot, 'ARTIFACT_INDEX.tsv'))
  const indexed = new Set()
  for (const row of artifactRows) {
    for (const key of ['artifact_path', 'counterpart_path', 'sources_path']) {
      const value = row[key]
      if (value === '') {
        fail('artifact index has empty ' + key + ' for ' + (row.artifact_path || '<unknown>'))
        continue
      }
      if (!existsSync(resolve(bundleRoot, value))) {
        fail('artifact index target missing: ' + value)
      }
    }
    for (const path of [row.artifact_path, row.counterpart_path]) {
      if (indexed.has(path)) fail('artifact indexed more than once: ' + path)
      indexed.add(path)
    }

    if (row.kind === 'markdown' || row.kind === 'skill') {
      const english = readFileSync(resolve(bundleRoot, row.artifact_path), 'utf8')
      const chinese = readFileSync(resolve(bundleRoot, row.counterpart_path), 'utf8')
      const a = markdownStructure(english)
      const b = markdownStructure(chinese)
      if (a.openFence || b.openFence) {
        fail('unclosed Markdown fence in pair: ' + row.artifact_path)
      }
      if (JSON.stringify(a.headings) !== JSON.stringify(b.headings)) {
        fail('heading structure differs in translation pair: ' + row.artifact_path)
      }
      if (JSON.stringify(a.fences) !== JSON.stringify(b.fences)) {
        fail('fenced code differs in translation pair: ' + row.artifact_path)
      }
    }
  }

  for (const path of allFiles) {
    if (isRawEvidence(path) || isProvenance(path) || isStructuredEvidence(path)) continue
    if (!indexed.has(path)) fail('derived artifact is not indexed: ' + path)
  }

  const sourceDocuments = allFiles.filter(
    (path) => isProvenance(path) && path.endsWith('SOURCES.md'),
  )
  for (const path of sourceDocuments) {
    const text = readFileSync(resolve(bundleRoot, path), 'utf8')
    const genericProjectRecord = path.startsWith('artifacts/project/') ||
      path.startsWith('artifacts/user/')
    if (!text.includes(pinnedCommit) && !genericProjectRecord) {
      fail('source record does not name pinned commit: ' + path)
    }
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error))
}

if (failures.length > 0) {
  for (const failure of failures) console.error('review-bundle: ' + failure)
  process.exit(1)
}

console.log(
  'review-bundle: source coverage, hashes, isolation, translations, and artifact provenance verified',
)
