import test from 'node:test';
import assert from 'node:assert/strict';

import {
  CliError,
  DEFAULT_MODEL,
  parseArgs,
  resolveConfig,
  buildRequestBody,
  extractAnswer,
  searchGrok,
  formatResult,
} from '../skills/grok-search/scripts/grok-client.mjs';

// Build a valid config for the orchestrator/formatter tests.
const validConfig = (overrides = {}) =>
  resolveConfig({ query: 'q', baseUrl: 'https://grok.test', apiKey: 'k', ...overrides }, {});

// --- parseArgs ---------------------------------------------------------------
test('parseArgs: parses flag values', () => {
  assert.deepEqual(parseArgs(['--query', 'hello', '--effort', 'high']), { query: 'hello', effort: 'high' });
});

test('parseArgs: kebab-case flags become camelCase keys', () => {
  assert.deepEqual(parseArgs(['--effort-model', 'alias', '--timeout-ms', '5000']), {
    effortModel: 'alias',
    timeoutMs: '5000',
  });
});

test('parseArgs: --key=value form', () => {
  assert.deepEqual(parseArgs(['--query=hello']), { query: 'hello' });
});

test('parseArgs: unknown flag throws', () => {
  assert.throws(() => parseArgs(['--bogus', 'x']), /Unexpected option: --bogus/);
});

test('parseArgs: --help sets the help flag', () => {
  assert.deepEqual(parseArgs(['--help']), { help: true });
  assert.deepEqual(parseArgs(['-h']), { help: true });
});

// --- resolveConfig -----------------------------------------------------------
test('resolveConfig: falls back to env for base url and api key', () => {
  const cfg = resolveConfig({ query: 'q' }, { GROK_SEARCH_BASE_URL: 'https://env.test', GROK_SEARCH_API_KEY: 'envkey' });
  assert.equal(cfg.baseUrl, 'https://env.test');
  assert.equal(cfg.apiKey, 'envkey');
});

test('resolveConfig: missing base url is a specific error', () => {
  assert.throws(() => resolveConfig({ query: 'q', apiKey: 'k' }, {}), /Missing base URL/);
});

test('resolveConfig: missing api key is a specific error', () => {
  assert.throws(() => resolveConfig({ query: 'q', baseUrl: 'https://grok.test' }, {}), /Missing API key/);
});

test('resolveConfig: invalid effort is rejected', () => {
  assert.throws(() => resolveConfig({ query: 'q', baseUrl: 'https://grok.test', apiKey: 'k', effort: 'ultra' }, {}), /Invalid --effort/);
});

test('resolveConfig: applies defaults', () => {
  const cfg = validConfig();
  assert.equal(cfg.effort, 'medium');
  assert.equal(cfg.format, 'text');
  assert.equal(cfg.effortModel, 'reasoning');
  assert.equal(cfg.timeoutMs, 120000);
  assert.equal(cfg.model, DEFAULT_MODEL);
});

// --- buildRequestBody --------------------------------------------------------
test('buildRequestBody: carries model, query, and effort', () => {
  const body = buildRequestBody(validConfig({ effort: 'high' }));
  assert.equal(body.model, DEFAULT_MODEL);
  assert.equal(body.stream, false);
  assert.equal(body.reasoning.effort, 'high');
  assert.equal(body.input[0].content[0].text, 'q');
});

// --- extractAnswer: all four response shapes + a no-match case ---------------
test('extractAnswer: output_text shape', () => {
  assert.equal(extractAnswer({ output_text: '  hello  ' }), 'hello');
});

test('extractAnswer: output array shape', () => {
  assert.equal(extractAnswer({ output: [{ content: [{ type: 'output_text', text: 'from output' }] }] }), 'from output');
});

test('extractAnswer: choices shape', () => {
  assert.equal(extractAnswer({ choices: [{ message: { content: 'from choices' } }] }), 'from choices');
});

test('extractAnswer: message.content shape', () => {
  assert.equal(extractAnswer({ message: { content: [{ text: 'from message' }] } }), 'from message');
});

test('extractAnswer: no assistant text throws', () => {
  assert.throws(() => extractAnswer({ unrelated: true }), /Could not find assistant text/);
});

// --- searchGrok with a fake transport ----------------------------------------
test('searchGrok: 200 + good body returns answer and raw', async () => {
  const transport = async () => ({ status: 200, ok: true, bodyText: JSON.stringify({ output_text: 'the answer' }) });
  const { answer, raw } = await searchGrok(validConfig(), transport);
  assert.equal(answer, 'the answer');
  assert.equal(raw.output_text, 'the answer');
});

test('searchGrok: non-200 maps to an HTTP CliError', async () => {
  const transport = async () => ({ status: 500, ok: false, bodyText: 'upstream boom' });
  await assert.rejects(() => searchGrok(validConfig(), transport), (e) => {
    assert.ok(e instanceof CliError);
    assert.match(e.message, /HTTP 500 from grok2api/);
    return true;
  });
});

test('searchGrok: malformed JSON maps to a parse CliError', async () => {
  const transport = async () => ({ status: 200, ok: true, bodyText: 'not json {' });
  await assert.rejects(() => searchGrok(validConfig(), transport), /Invalid JSON response/);
});

test('searchGrok: a thrown timeout maps to a timeout CliError', async () => {
  const transport = async () => {
    const err = new Error('aborted');
    err.name = 'AbortError';
    throw err;
  };
  await assert.rejects(() => searchGrok(validConfig({ timeoutMs: '4242' }), transport), /timed out after 4242 ms/);
});

// --- formatResult: text vs json ----------------------------------------------
test('formatResult: text format returns the bare answer', () => {
  assert.equal(formatResult(validConfig(), 'the answer'), 'the answer');
});

test('formatResult: json format embeds answer, raw, and query', () => {
  const cfg = validConfig({ format: 'json' });
  const raw = { output_text: 'the answer' };
  const parsed = JSON.parse(formatResult(cfg, 'the answer', raw));
  assert.equal(parsed.answer, 'the answer');
  assert.equal(parsed.query, 'q');
  assert.deepEqual(parsed.raw, raw);
});
