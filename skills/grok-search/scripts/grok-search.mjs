#!/usr/bin/env node
// grok-search.mjs
// Thin CLI shell around grok-client.mjs. It reads argv/env, supplies the
// production transport (fetch + an AbortController timeout), writes to stdout,
// and sets the exit code. All logic lives in grok-client.mjs.

import {
  CliError,
  helpText,
  parseArgs,
  resolveConfig,
  searchGrok,
  formatResult,
} from "./grok-client.mjs";

// Production transport: the seam's real implementation. Wraps fetch with an
// AbortController timeout and returns the raw { status, ok, bodyText } the core
// expects. Network/timeout failures throw (the core maps them to CliError).
async function fetchTransport(endpoint, opts) {
  if (typeof fetch !== "function") {
    throw new CliError("This script requires Node.js 18+ with global fetch.");
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), opts.timeoutMs);

  try {
    const response = await fetch(endpoint, {
      method: opts.method,
      headers: opts.headers,
      body: opts.body,
      signal: controller.signal,
    });
    const bodyText = await response.text();
    return { status: response.status, ok: response.ok, bodyText };
  } finally {
    clearTimeout(timeout);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(helpText());
    return;
  }

  const config = resolveConfig(args, process.env);
  const { answer, raw } = await searchGrok(config, fetchTransport);
  console.log(formatResult(config, answer, raw));
}

main().catch((error) => {
  const exitCode = error instanceof CliError ? error.exitCode : 1;
  console.error(error?.message ?? String(error));
  process.exit(exitCode);
});
