#!/usr/bin/env node

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

function git(args, allowFailure = false) {
  const result = spawnSync('git', args, {
    cwd: repositoryRoot,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  if (!allowFailure && result.status !== 0) {
    throw new Error(result.stderr.trim() || `git ${args.join(' ')} failed`)
  }
  return result
}

function readArguments(argv) {
  let mode
  let base
  let config = 'agent-guardrails.config.json'

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index]
    if (argument === '--staged') {
      if (mode !== undefined) throw new Error('choose exactly one of --staged or --base')
      mode = 'staged'
      continue
    }
    if (argument === '--base') {
      if (mode !== undefined || argv[index + 1] === undefined) {
        throw new Error('--base requires one revision and cannot be combined with --staged')
      }
      mode = 'base'
      base = argv[index + 1]
      index += 1
      continue
    }
    if (argument === '--config') {
      if (argv[index + 1] === undefined) throw new Error('--config requires a path')
      config = argv[index + 1]
      index += 1
      continue
    }
    throw new Error(`unknown argument: ${argument}`)
  }

  if (mode === undefined) throw new Error('choose exactly one of --staged or --base <revision>')
  return { mode, base, config }
}

function parseNameStatus(output) {
  const fields = output.split('\0')
  if (fields.at(-1) === '') fields.pop()

  const paths = new Set()
  for (let index = 0; index < fields.length;) {
    const status = fields[index]
    index += 1
    if (/^[RC]/.test(status)) {
      if (fields[index] === undefined || fields[index + 1] === undefined) {
        throw new Error('invalid rename/copy record from git diff')
      }
      paths.add(fields[index])
      paths.add(fields[index + 1])
      index += 2
    } else {
      if (fields[index] === undefined) throw new Error('invalid path record from git diff')
      paths.add(fields[index])
      index += 1
    }
  }
  return paths
}

function validateConfig(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('configuration must be an object')
  }

  const arrays = ['protectedPaths', 'sourceProjectionGroups', 'requiredCompanions']
  for (const key of arrays) {
    if (!Array.isArray(value[key])) throw new Error(`${key} must be an array`)
  }

  for (const path of value.protectedPaths) {
    if (typeof path !== 'string' || path === '') throw new Error('protectedPaths entries must be non-empty strings')
  }

  for (const group of value.sourceProjectionGroups) {
    if (
      group === null ||
      typeof group !== 'object' ||
      typeof group.source !== 'string' ||
      group.source === '' ||
      !Array.isArray(group.projections) ||
      group.projections.length === 0 ||
      group.projections.some((path) => typeof path !== 'string' || path === '')
    ) {
      throw new Error('sourceProjectionGroups entries require source and non-empty projections')
    }
  }

  for (const pair of value.requiredCompanions) {
    if (
      pair === null ||
      typeof pair !== 'object' ||
      typeof pair.artifact !== 'string' ||
      pair.artifact === '' ||
      typeof pair.companion !== 'string' ||
      pair.companion === '' ||
      (pair.updateTogether !== undefined && typeof pair.updateTogether !== 'boolean')
    ) {
      throw new Error('requiredCompanions entries require artifact, companion, and optional boolean updateTogether')
    }
  }
}

function touches(protectedPath, changedPath) {
  return protectedPath.endsWith('/')
    ? changedPath.startsWith(protectedPath)
    : changedPath === protectedPath
}

const repositoryRootResult = spawnSync('git', ['rev-parse', '--show-toplevel'], {
  encoding: 'utf8',
  stdio: ['ignore', 'pipe', 'pipe'],
})
if (repositoryRootResult.status !== 0) {
  console.error(repositoryRootResult.stderr.trim() || 'not inside a Git repository')
  process.exit(2)
}
const repositoryRoot = repositoryRootResult.stdout.trim()

try {
  const options = readArguments(process.argv.slice(2))
  const configPath = resolve(repositoryRoot, options.config)
  const config = JSON.parse(readFileSync(configPath, 'utf8'))
  validateConfig(config)

  let diffArguments
  let snapshotPrefix
  if (options.mode === 'staged') {
    diffArguments = ['diff', '--cached', '--name-status', '-z', '--find-renames']
    snapshotPrefix = ':'
  } else {
    git(['rev-parse', '--verify', `${options.base}^{commit}`])
    diffArguments = ['diff', '--name-status', '-z', '--find-renames', options.base, 'HEAD']
    snapshotPrefix = 'HEAD:'
  }

  const changedPaths = parseNameStatus(git(diffArguments).stdout)
  const exists = (path) => git(['cat-file', '-e', `${snapshotPrefix}${path}`], true).status === 0
  const failures = []

  for (const protectedPath of config.protectedPaths) {
    for (const changedPath of changedPaths) {
      if (touches(protectedPath, changedPath)) {
        failures.push(`protected path changed: ${changedPath} (rule: ${protectedPath})`)
      }
    }
  }

  for (const group of config.sourceProjectionGroups) {
    const members = [group.source, ...group.projections]
    if (!members.some((path) => changedPaths.has(path))) continue
    for (const path of members) {
      if (!changedPaths.has(path)) failures.push(`source/projection group did not change together: ${path}`)
      if (!exists(path)) failures.push(`source/projection member missing from target snapshot: ${path}`)
    }
  }

  for (const pair of config.requiredCompanions) {
    const touched = changedPaths.has(pair.artifact) || changedPaths.has(pair.companion)
    if (!touched) continue
    if (!exists(pair.artifact)) failures.push(`required artifact missing from target snapshot: ${pair.artifact}`)
    if (!exists(pair.companion)) failures.push(`required companion missing from target snapshot: ${pair.companion}`)
    if (pair.updateTogether === true) {
      if (!changedPaths.has(pair.artifact)) failures.push(`artifact did not change with companion: ${pair.artifact}`)
      if (!changedPaths.has(pair.companion)) failures.push(`companion did not change with artifact: ${pair.companion}`)
    }
  }

  if (failures.length > 0) {
    for (const failure of failures) console.error(`agent-guardrails: ${failure}`)
    process.exit(1)
  }

  console.log(`agent-guardrails: checked ${changedPaths.size} changed path(s)`)
} catch (error) {
  console.error(`agent-guardrails: ${error instanceof Error ? error.message : String(error)}`)
  process.exit(2)
}
