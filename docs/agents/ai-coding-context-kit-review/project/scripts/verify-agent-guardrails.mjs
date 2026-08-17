#!/usr/bin/env node

import { readFileSync } from 'node:fs'
import { isAbsolute, relative, resolve, sep } from 'node:path'
import { spawnSync } from 'node:child_process'

const args = process.argv.slice(2)
let mode
let base
let configArgument = 'agent-guardrails.config.json'

for (let index = 0; index < args.length; index += 1) {
  const argument = args[index]
  if (argument === '--staged' || argument === '--all') {
    if (mode) failUsage('Choose exactly one of --staged, --base, or --all.')
    mode = argument.slice(2)
    continue
  }
  if (argument === '--base') {
    if (mode) failUsage('Choose exactly one of --staged, --base, or --all.')
    base = args[index + 1]
    if (!base) failUsage('--base requires a Git ref or commit.')
    mode = 'base'
    index += 1
    continue
  }
  if (argument === '--config') {
    configArgument = args[index + 1]
    if (!configArgument) failUsage('--config requires a path.')
    index += 1
    continue
  }
  failUsage(`Unknown argument: ${argument}`)
}

if (!mode) failUsage('Choose one of --staged, --base <ref>, or --all.')

const repoRoot = runGit(['rev-parse', '--show-toplevel']).trim()
const configPath = isAbsolute(configArgument)
  ? configArgument
  : resolve(repoRoot, configArgument)
const snapshotPaths = new Set(readSnapshotPaths())
const configRepositoryPath = repositoryPathFor(configPath)

let config
try {
  const configText = configRepositoryPath === undefined
    ? readFileSync(configPath, 'utf8')
    : readSnapshotFile(configRepositoryPath)
  config = JSON.parse(configText)
} catch (error) {
  fail(`Cannot parse ${configPath}: ${error.message}`)
}

const changedPaths = new Set(readChangedPaths())
const errors = []

for (const pair of arrayField(config, 'artifactSourcePairs')) {
  const artifact = checkedPath(pair.artifact, 'artifactSourcePairs[].artifact')
  const source = checkedPath(pair.source, 'artifactSourcePairs[].source')
  const artifactExists = snapshotPaths.has(artifact)
  const sourceExists = snapshotPaths.has(source)
  if (artifactExists && !sourceExists) {
    errors.push(`${artifact} exists without its source document ${source}`)
  }
  if (!artifactExists && sourceExists) {
    errors.push(`${source} exists without its artifact ${artifact}`)
  }
}

for (const rule of arrayField(config, 'protectedPathPrefixes')) {
  const prefix = checkedPath(rule.prefix, 'protectedPathPrefixes[].prefix')
  const allowed = arrayValue(rule.allowPrefixes).map((value) =>
    checkedPath(value, 'protectedPathPrefixes[].allowPrefixes[]'),
  )
  for (const changedPath of changedPaths) {
    if (matchesPrefix(changedPath, prefix) && !allowed.some((value) => matchesPrefix(changedPath, value))) {
      errors.push(`${changedPath} changes protected path ${prefix}: ${rule.reason ?? 'use the owning workflow'}`)
    }
  }
}

for (const pair of arrayField(config, 'sourceProjectionPairs')) {
  const sources = requiredPathArray(pair.sources, 'sourceProjectionPairs[].sources')
  const projections = requiredPathArray(pair.projections, 'sourceProjectionPairs[].projections')
  const projectionChanged = [...changedPaths].some((changedPath) =>
    projections.some((prefix) => matchesPrefix(changedPath, prefix)),
  )
  const sourceChanged = [...changedPaths].some((changedPath) =>
    sources.some((prefix) => matchesPrefix(changedPath, prefix)),
  )
  if (projectionChanged && !sourceChanged) {
    errors.push(`A generated projection changed without an owning source (${sources.join(', ')}): ${pair.reason ?? 'update the canonical source and regenerate'}`)
  }
}

if (errors.length > 0) {
  console.error('Agent guardrails failed:')
  for (const error of errors) console.error(`- ${error}`)
  process.exit(1)
}

const checkedPathCount = mode === 'all' ? snapshotPaths.size : changedPaths.size
const checkedScope = mode === 'all' ? 'tracked paths scanned' : 'changed paths checked'
console.log(`Agent guardrails passed (${checkedPathCount} ${checkedScope}).`)

function readChangedPaths() {
  if (mode === 'all') return []
  if (mode === 'staged') {
    return outputLines(runGit(['diff', '--cached', '--name-only', '--no-renames', '--diff-filter=ACMDT']))
  }
  return outputLines(runGit(['diff', '--name-only', '--no-renames', '--diff-filter=ACMDT', `${base}...HEAD`]))
}

function readSnapshotPaths() {
  if (mode === 'base') {
    return outputLines(runGit(['ls-tree', '-r', '--name-only', 'HEAD']))
  }
  return outputLines(runGit(['ls-files', '--cached']))
}

function readSnapshotFile(repositoryPath) {
  if (!snapshotPaths.has(repositoryPath)) {
    fail(`Configuration not found in the ${mode === 'base' ? 'HEAD' : 'index'} snapshot: ${repositoryPath}`)
  }
  const objectName = mode === 'base' ? `HEAD:${repositoryPath}` : `:${repositoryPath}`
  return runGit(['show', objectName])
}

function runGit(gitArgs) {
  const result = spawnSync('git', gitArgs, { encoding: 'utf8' })
  if (result.error) fail(`Cannot run git ${gitArgs.join(' ')}: ${result.error.message}`)
  if (result.status !== 0) fail(result.stderr.trim() || `git ${gitArgs.join(' ')} failed`)
  return result.stdout
}

function outputLines(output) {
  return output
    .split(/\r?\n/u)
    .map(normalizePath)
    .filter(Boolean)
}

function normalizePath(value) {
  return value.replaceAll('\\', '/').replace(/^\.\//u, '').replace(/\/+$/u, '')
}

function checkedPath(value, field) {
  if (typeof value !== 'string' || value.trim() === '') fail(`${field} must be a non-empty string`)
  const normalized = normalizePath(value.trim())
  if (isAbsolute(normalized) || normalized.split('/').includes('..')) {
    fail(`${field} must stay inside the repository: ${value}`)
  }
  return normalized
}

function repositoryPathFor(absolutePath) {
  const fromRoot = relative(repoRoot, absolutePath)
  if (fromRoot === '' || fromRoot === '..' || fromRoot.startsWith(`..${sep}`) || isAbsolute(fromRoot)) {
    return undefined
  }
  return normalizePath(fromRoot)
}

function matchesPrefix(repositoryPath, prefix) {
  return repositoryPath === prefix || repositoryPath.startsWith(`${prefix}/`)
}

function arrayField(object, field) {
  const value = object[field]
  if (value === undefined) return []
  if (!Array.isArray(value)) fail(`${field} must be an array`)
  return value
}

function arrayValue(value) {
  if (value === undefined) return []
  if (!Array.isArray(value)) fail('allowPrefixes must be an array')
  return value
}

function requiredPathArray(value, field) {
  if (!Array.isArray(value) || value.length === 0) fail(`${field} must be a non-empty array`)
  return value.map((entry) => checkedPath(entry, `${field}[]`))
}

function failUsage(message) {
  console.error(message)
  console.error('Usage: verify-agent-guardrails.mjs (--staged | --base <ref> | --all) [--config <path>]')
  process.exit(2)
}

function fail(message) {
  console.error(message)
  process.exit(1)
}
