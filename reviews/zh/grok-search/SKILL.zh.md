---
name: grok-search
description: 当用户要求获取最新的网络搜索、X/Twitter 搜索、近期帖子或时事动态时使用。
---

# Grok 搜索

使用已配置的 grok2api 端点，向 Grok 多智能体控制台模型请求最新的 Web 或 X 证据。

## 步骤

1. 选择 effort（投入程度）。
   默认使用 `medium`。简单探测用 `low`，较难的综合分析用 `high`，仅当任务确实值得最慢的运行时才用 `xhigh`。

   完成标准：恰好选定一个 effort。

2. 立即运行 CLI。
   在本 skill 目录下执行：

   ```bash
   node scripts/grok-search.mjs --query "latest context to verify" --effort medium
   ```

   选项：`--effort low|medium|high|xhigh`、`--effort-model reasoning|alias`、`--format text|json`、`--base-url`、`--api-key`、`--model`、`--timeout-ms`。`GROK_SEARCH_MODEL` 默认为 `grok-4.20-multi-agent-console`；`GROK_SEARCH_EFFORT` 默认为 `medium`。以 `node scripts/grok-search.mjs --help` 作为 CLI 的权威说明。

   完成标准：脚本返回一个答案，或返回明确的配置、HTTP、JSON 或超时错误。

3. 仅在失败后才处理缺失的配置。
   如果 CLI 报告 `Missing base URL` 或 `Missing API key`，告知用户设置 `GROK_SEARCH_BASE_URL` 和 `GROK_SEARCH_API_KEY`，或传入 `--base-url` 和 `--api-key`。

   完成标准：用户清楚知道是哪个缺失的设置阻塞了搜索。

4. 汇报证据。
   说明答案来自通过 grok2api 进行的 Grok Web/X 搜索。仅当模型确实返回了来源名称、URL、引用和引文片段时才予以保留。不要编造 `search_sources` 或引用。

   完成标准：用户能够区分搜索得到的证据与你自己的推断。
