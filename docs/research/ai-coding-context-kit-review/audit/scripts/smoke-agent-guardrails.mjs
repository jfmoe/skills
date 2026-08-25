#!/usr/bin/env node

import {
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const bundleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const verifier = resolve(bundleRoot, 'artifacts/project/scripts/verify-agent-guardrails.mjs')
const temporaryRoots = []

function run(cwd, command, args, expected = 0) {
  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  if (result.status !== expected) {
    throw new Error(
      command + ' ' + args.join(' ') + ' exited ' + result.status +
      ' instead of ' + expected + '\n' + result.stdout + result.stderr,
    )
  }
  return result
}

function write(path, content) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, content)
}

function createRepository() {
  const root = mkdtempSync(join(tmpdir(), 'agent-guardrails-'))
  temporaryRoots.push(root)
  mkdirSync(join(root, 'scripts'), { recursive: true })
  copyFileSync(verifier, join(root, 'scripts/verify-agent-guardrails.mjs'))
  write(join(root, 'agent-guardrails.config.json'), JSON.stringify({
    protectedPaths: ['frozen/'],
    sourceProjectionGroups: [{
      source: 'docs/source.md',
      projections: ['docs/generated.md'],
    }],
    requiredCompanions: [{
      artifact: 'AGENTS.md',
      companion: 'AGENTS.sources.md',
      updateTogether: true,
    }],
  }, null, 2) + '\n')
  write(join(root, 'docs/source.md'), 'source\n')
  write(join(root, 'docs/generated.md'), 'generated\n')
  write(join(root, 'AGENTS.md'), 'rules\n')
  write(join(root, 'AGENTS.sources.md'), 'sources\n')
  write(join(root, 'frozen/policy.md'), 'frozen\n')

  run(root, 'git', ['init', '-q'])
  run(root, 'git', ['config', 'user.name', 'Guardrail Smoke'])
  run(root, 'git', ['config', 'user.email', 'guardrail@example.invalid'])
  run(root, 'git', ['add', '.'])
  run(root, 'git', ['commit', '-qm', 'baseline'])
  return root
}

function verify(root, args, expected) {
  return run(root, process.execPath, ['scripts/verify-agent-guardrails.mjs', ...args], expected)
}

try {
  {
    const root = createRepository()
    write(join(root, 'docs/source.md'), 'source changed\n')
    write(join(root, 'docs/generated.md'), 'generated changed\n')
    write(join(root, 'AGENTS.md'), 'rules changed\n')
    write(join(root, 'AGENTS.sources.md'), 'sources changed\n')
    run(root, 'git', ['add', '.'])
    verify(root, ['--staged'], 0)
  }

  {
    const root = createRepository()
    write(join(root, 'AGENTS.md'), 'rules changed\n')
    run(root, 'git', ['add', 'AGENTS.md'])
    run(root, 'git', ['update-index', '--force-remove', 'AGENTS.sources.md'])
    const result = verify(root, ['--staged'], 1)
    if (!result.stderr.includes('required companion missing from target snapshot')) {
      throw new Error('staged deletion was not reported as a missing companion')
    }
  }

  {
    const root = createRepository()
    run(root, 'git', ['mv', 'frozen/policy.md', 'moved-policy.md'])
    const result = verify(root, ['--staged'], 1)
    if (!result.stderr.includes('protected path changed')) {
      throw new Error('protected rename was not rejected')
    }
  }

  {
    const root = createRepository()
    write(join(root, 'docs/generated.md'), 'projection only\n')
    run(root, 'git', ['add', 'docs/generated.md'])
    const result = verify(root, ['--staged'], 1)
    if (!result.stderr.includes('source/projection group did not change together')) {
      throw new Error('one-sided projection change was not rejected')
    }
  }

  {
    const root = createRepository()
    const base = run(root, 'git', ['rev-parse', 'HEAD']).stdout.trim()
    write(join(root, 'docs/source.md'), 'source changed\n')
    write(join(root, 'docs/generated.md'), 'generated changed\n')
    write(join(root, 'AGENTS.md'), 'rules changed\n')
    write(join(root, 'AGENTS.sources.md'), 'sources changed\n')
    run(root, 'git', ['add', '.'])
    run(root, 'git', ['commit', '-qm', 'valid change'])
    verify(root, ['--base', base], 0)
  }

  console.log('agent-guardrails smoke: 5 scenarios passed')
} finally {
  for (const root of temporaryRoots) rmSync(root, { recursive: true, force: true })
}
