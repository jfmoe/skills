// grok-client.mjs
// Pure core of the grok-search CLI. No network here: searchGrok takes a
// `transport` seam so the logic is testable offline with a fake transport.
//
//   transport(endpoint, opts) -> { status, ok, bodyText }   (may throw)
//
// The core owns argument/config parsing, the request body, status-checking,
// JSON.parse, the multi-shape answer extraction, output formatting, and the
// mapping of failures to CliError / exit codes. The CLI shell (grok-search.mjs)
// supplies the production transport (fetch + AbortController) and does the I/O.

export const DEFAULT_MODEL = "grok-4.20-multi-agent-console";
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

export class CliError extends Error {
  constructor(message, exitCode = 1) {
    super(message);
    this.name = "CliError";
    this.exitCode = exitCode;
  }
}

export function helpText() {
  return `Usage:
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
`;
}

function toCamelCase(key) {
  return key.replace(/-([a-z])/g, (_, char) => char.toUpperCase());
}

export function parseArgs(argv) {
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

export function resolveConfig(args, env) {
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

export function buildEndpoint(baseUrl) {
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

export function buildRequestBody(config) {
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

export function extractAnswer(body) {
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

// Orchestrator: build the request, drive the transport seam, and own the
// status-check / parse / extraction / error-mapping. Returns { answer, raw }.
export async function searchGrok(config, transport) {
  const endpoint = buildEndpoint(config.baseUrl);

  let result;
  try {
    result = await transport(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
        Connection: "close",
      },
      body: JSON.stringify(buildRequestBody(config)),
      timeoutMs: config.timeoutMs,
    });
  } catch (error) {
    if (error instanceof CliError) {
      throw error;
    }
    if (error?.name === "AbortError") {
      throw new CliError(`Request timed out after ${config.timeoutMs} ms.`);
    }
    throw new CliError(`Request failed: ${error?.message ?? String(error)}`);
  }

  const { status, ok, bodyText } = result;

  if (!ok) {
    throw new CliError(`HTTP ${status} from grok2api: ${excerpt(bodyText)}`);
  }

  let raw;
  try {
    raw = JSON.parse(bodyText);
  } catch (error) {
    throw new CliError(`Invalid JSON response: ${error.message}. Body: ${excerpt(bodyText)}`);
  }

  return { answer: extractAnswer(raw), raw };
}

export function formatResult(config, answer, raw) {
  if (config.format === "json") {
    return JSON.stringify(
      {
        effort: config.effort,
        effortModel: config.effortModel,
        query: config.query,
        model: config.model,
        requestedModel: config.requestedModel,
        answer,
        raw,
      },
      null,
      2,
    );
  }

  return answer;
}
