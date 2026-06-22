#!/usr/bin/env node

const DEFAULT_MODEL = "grok-4.20-multi-agent-console";
const EFFORTS = new Set(["low", "medium", "high", "xhigh"]);
const FORMATS = new Set(["text", "json"]);
const EFFORT_MODEL_MODES = new Set(["reasoning", "alias"]);
const ALLOWED_OPTIONS = new Set([
  "query",
  "effort",
  "effortModel",
  "format",
  "baseUrl",
  "apiKey",
  "model",
  "timeoutMs",
]);
const MULTI_AGENT_ALIASES = new Set([
  "grok-4.20-multi-agent-console",
  "grok-4.20-multi-agent-low",
  "grok-4.20-multi-agent-medium",
  "grok-4.20-multi-agent-high",
  "grok-4.20-multi-agent-xhigh",
]);

class CliError extends Error {
  constructor(message, exitCode = 1) {
    super(message);
    this.name = "CliError";
    this.exitCode = exitCode;
  }
}

function printHelp() {
  console.log(`Usage:
  node scripts/grok-search.mjs --query "..." [options]

Required:
  --query <text>          Search question or research task.

Options:
  --effort <effort>       Reasoning effort: low, medium, high, or xhigh. Default: medium.
  --effort-model <mode>   Apply effort as reasoning field or model alias. Default: reasoning.
  --format <format>       Output format: text or json. Default: text.
  --base-url <url>        grok2api base URL. Env: GROK_SEARCH_BASE_URL.
  --api-key <key>         grok2api API key. Env: GROK_SEARCH_API_KEY.
  --model <model>         Model. Env: GROK_SEARCH_MODEL. Default: ${DEFAULT_MODEL}.
  Env default effort:     GROK_SEARCH_EFFORT.
  --timeout-ms <number>   Request timeout in milliseconds. Default: 120000.
  -h, --help              Show this help.
`);
}

function parseArgs(argv) {
  const args = {};

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "-h" || token === "--help") {
      args.help = true;
      continue;
    }

    if (!token.startsWith("--")) {
      throw new CliError(`Unexpected positional argument: ${token}`);
    }

    const eqIndex = token.indexOf("=");
    let key;
    let value;

    if (eqIndex === -1) {
      key = token.slice(2);
      value = argv[i + 1];
      if (value === undefined || value.startsWith("--")) {
        throw new CliError(`Missing value for --${key}`);
      }
      i += 1;
    } else {
      key = token.slice(2, eqIndex);
      value = token.slice(eqIndex + 1);
    }

    const optionName = toCamelCase(key);
    if (!ALLOWED_OPTIONS.has(optionName)) {
      throw new CliError(`Unexpected option: --${key}`);
    }

    args[optionName] = value;
  }

  return args;
}

function toCamelCase(key) {
  return key.replace(/-([a-z])/g, (_, char) => char.toUpperCase());
}

function readConfig(args, env) {
  const query = stringValue(args.query, "query");
  const effort = stringValue(args.effort ?? env.GROK_SEARCH_EFFORT ?? "medium", "effort").toLowerCase();
  const effortModel = stringValue(args.effortModel ?? env.GROK_SEARCH_EFFORT_MODEL ?? "reasoning", "effort model").toLowerCase();
  const format = stringValue(args.format ?? "text", "format").toLowerCase();
  const baseUrl = stringValue(args.baseUrl ?? env.GROK_SEARCH_BASE_URL, "base URL");
  const apiKey = stringValue(args.apiKey ?? env.GROK_SEARCH_API_KEY, "API key");
  const requestedModel = stringValue(args.model ?? env.GROK_SEARCH_MODEL ?? DEFAULT_MODEL, "model");
  const timeoutMs = parseTimeout(args.timeoutMs ?? "120000");

  if (!FORMATS.has(format)) {
    throw new CliError(`Invalid --format "${format}". Expected one of: ${Array.from(FORMATS).join(", ")}.`);
  }

  if (!EFFORTS.has(effort)) {
    throw new CliError(`Invalid --effort "${effort}". Expected one of: ${Array.from(EFFORTS).join(", ")}.`);
  }

  if (!EFFORT_MODEL_MODES.has(effortModel)) {
    throw new CliError(`Invalid --effort-model "${effortModel}". Expected one of: ${Array.from(EFFORT_MODEL_MODES).join(", ")}.`);
  }

  const model = resolveModel(requestedModel, effort, effortModel);

  return {
    query,
    effort,
    effortModel,
    format,
    baseUrl,
    apiKey,
    requestedModel,
    model,
    timeoutMs,
  };
}

function stringValue(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new CliError(`Missing ${label}.`);
  }
  return value.trim();
}

function parseTimeout(value) {
  const timeoutMs = Number(value);
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new CliError(`Invalid --timeout-ms "${value}". Expected a positive number.`);
  }
  return timeoutMs;
}

function resolveModel(requestedModel, effort, effortModel) {
  if (effortModel === "alias" && MULTI_AGENT_ALIASES.has(requestedModel)) {
    return `grok-4.20-multi-agent-${effort}`;
  }
  return requestedModel;
}

function buildEndpoint(baseUrl) {
  const root = baseUrl.replace(/\/+$/, "");
  return root.endsWith("/v1") ? `${root}/responses` : `${root}/v1/responses`;
}

function buildInstructions() {
  return [
    "Use the search tools to search both X/Twitter and the Web for relevant content.",
    "Answer the user's query with fresh evidence.",
    "Preserve source names, URLs, citations, handles, dates, and quoted snippets when the search result provides them.",
    "If search evidence is unavailable or thin, say so plainly.",
  ].join(" ");
}

function buildRequestBody(config) {
  return {
    model: config.model,
    instructions: buildInstructions(),
    input: [
      {
        role: "user",
        content: [
          {
            type: "input_text",
            text: config.query,
          },
        ],
      },
    ],
    stream: false,
    temperature: 0.2,
    top_p: 0.95,
    reasoning: {
      effort: config.effort,
    },
  };
}

async function postResponses(config) {
  if (typeof fetch !== "function") {
    throw new CliError("This script requires Node.js 18+ with global fetch.");
  }

  const endpoint = buildEndpoint(config.baseUrl);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.timeoutMs);

  let response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
        Connection: "close",
      },
      body: JSON.stringify(buildRequestBody(config)),
      signal: controller.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new CliError(`Request timed out after ${config.timeoutMs} ms.`);
    }
    throw new CliError(`Request failed: ${error?.message ?? String(error)}`);
  } finally {
    clearTimeout(timeout);
  }

  const responseText = await response.text();

  if (!response.ok) {
    throw new CliError(`HTTP ${response.status} from grok2api: ${excerpt(responseText)}`);
  }

  try {
    return JSON.parse(responseText);
  } catch (error) {
    throw new CliError(`Invalid JSON response: ${error.message}. Body: ${excerpt(responseText)}`);
  }
}

function extractAnswer(body) {
  if (typeof body?.output_text === "string" && body.output_text.trim()) {
    return body.output_text.trim();
  }

  const outputText = extractFromOutput(body?.output);
  if (outputText) {
    return outputText;
  }

  const choiceText = extractFromChoices(body?.choices);
  if (choiceText) {
    return choiceText;
  }

  const messageText = extractContent(body?.message?.content);
  if (messageText) {
    return messageText;
  }

  throw new CliError("Could not find assistant text in the response.");
}

function extractFromOutput(output) {
  if (!Array.isArray(output)) {
    return "";
  }

  const chunks = [];
  for (const item of output) {
    const content = item?.content;
    const text = extractContent(content);
    if (text) {
      chunks.push(text);
    }
  }

  return chunks.join("\n").trim();
}

function extractFromChoices(choices) {
  if (!Array.isArray(choices)) {
    return "";
  }

  const chunks = [];
  for (const choice of choices) {
    const text = extractContent(choice?.message?.content ?? choice?.text);
    if (text) {
      chunks.push(text);
    }
  }

  return chunks.join("\n").trim();
}

function extractContent(content) {
  if (typeof content === "string") {
    return content.trim();
  }

  if (!Array.isArray(content)) {
    return "";
  }

  const chunks = [];
  for (const part of content) {
    if (typeof part === "string") {
      chunks.push(part);
      continue;
    }

    const text = part?.text ?? part?.output_text;
    if (typeof text === "string" && text.trim()) {
      chunks.push(text.trim());
    }
  }

  return chunks.join("\n").trim();
}

function excerpt(text) {
  if (!text) {
    return "<empty body>";
  }
  return text.length > 500 ? `${text.slice(0, 500)}...` : text;
}

function writeResult(config, raw, answer) {
  if (config.format === "json") {
    console.log(JSON.stringify({
      effort: config.effort,
      effortModel: config.effortModel,
      query: config.query,
      model: config.model,
      requestedModel: config.requestedModel,
      answer,
      raw,
    }, null, 2));
    return;
  }

  console.log(answer);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const config = readConfig(args, process.env);
  const raw = await postResponses(config);
  const answer = extractAnswer(raw);
  writeResult(config, raw, answer);
}

main().catch((error) => {
  const exitCode = error instanceof CliError ? error.exitCode : 1;
  console.error(error?.message ?? String(error));
  process.exit(exitCode);
});
