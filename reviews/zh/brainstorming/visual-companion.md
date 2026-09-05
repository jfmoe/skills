# 视觉伴侣指南

基于浏览器的可视化头脑风暴伴侣，用于展示模型稿（mockup）、图表和选项。

## 何时使用

逐问题决定，而不是按会话决定。判断标准是：**这个问题用户看到它是否比读到它更容易理解？**

**用浏览器** 当内容本身是视觉性的：

- **UI 模型稿** —— 线框图、布局、导航结构、组件设计
- **架构图** —— 系统组件、数据流、关系图
- **并排视觉对比** —— 对比两种布局、两种配色方案、两个设计方向
- **设计打磨** —— 当问题涉及观感、间距、视觉层级时
- **空间关系** —— 以图表呈现的状态机、流程图、实体关系

**用终端** 当内容是文本或表格时：

- **需求与范围问题** —— "X 是什么意思？"、"哪些功能在范围内？"
- **概念性 A/B/C 选择** —— 在用文字描述的方案之间做选择
- **取舍清单** —— 优缺点、对比表格
- **技术决策** —— API 设计、数据建模、架构方案选型
- **澄清问题** —— 答案是文字、而不是视觉偏好的任何内容

*关于* UI 话题的问题不自动等于视觉问题。"你想要什么样的向导页？"是概念性问题——用终端。"这几种向导页布局哪种感觉对？"是视觉问题——用浏览器。

## 工作原理

服务器监视一个目录中的 HTML 文件，并把最新的一个提供给浏览器。你把 HTML 内容写入 `screen_dir`，用户在自己的浏览器中看到它，并可以点击选择选项。选择会被记录到 `state_dir/events`，你在下一轮对话中读取它。

**内容片段 vs 完整文档：** 如果你的 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务器会原样提供它（只注入辅助脚本）。否则，服务器会自动把你的内容包进框架模板——添加头部、CSS 主题、连接状态和全部交互基础设施。**默认写内容片段。** 只有当你需要完全控制页面时才写完整文档。

## 启动会话

```bash
# Start AFTER the user approves the companion. --open auto-opens their browser on
# the first screen; --project-dir persists mockups and enables same-port restart.
scripts/start-server.sh --project-dir /path/to/project --open

# Returns: {"type":"server-started","port":52341,
#           "url":"http://localhost:52341/?key=ab12…",
#           "screen_dir":"/path/to/project/.brainstorm/12345-1706000000/content",
#           "state_dir":"/path/to/project/.brainstorm/12345-1706000000/state"}
```

保存响应中的 `screen_dir` 和 `state_dir`。使用 `--open` 时，浏览器会在你推送第一个屏幕时自动打开——你不需要让用户自己打开，但仍要把 URL 作为备用方案分享出去（无头/远程环境不会自动打开）。

**URL 中包含一个会话密钥（`?key=…`）。** 服务器拒绝任何不带密钥的请求，所以总是把 `url` 字段中的**完整** URL 给用户——永远不要剥掉查询字符串，也永远不要给出光秃秃的 `http://host:port`。该密钥对 HTTP 和 WebSocket 访问做门禁，防止误入的浏览器标签页或网络上的其他机器读取屏幕内容或注入事件。首次加载后浏览器会通过 cookie 记住密钥，因此刷新和 `/files/*` 资源不需要重复带密钥。

**查找连接信息：** 服务器会把启动 JSON 写入 `$STATE_DIR/server-info`。如果你把服务器放在后台启动而没有捕获 stdout，读取该文件即可获得 URL 和端口。使用 `--project-dir` 时，在 `<project>/.brainstorm/` 下查看会话目录。

**注意：** 把项目根目录传给 `--project-dir`，模型稿就会持久化在 `.brainstorm/` 中，在服务器重启后仍然存在。不传的话，文件会进入 `/tmp` 并被清理。提醒用户把 `.brainstorm/` 加入 `.gitignore`（如果还没加）。

**按平台启动服务器：**

**Claude Code：**
```bash
# Default mode works — the script backgrounds the server itself.
scripts/start-server.sh --project-dir /path/to/project --open
```

在 Windows 上，脚本会自动检测并切换到前台模式（会阻塞工具调用）。对 Bash 工具调用使用 `run_in_background: true`，让服务器在对话轮次之间存活，然后在下一轮读取 `$STATE_DIR/server-info` 获取 URL 和端口。

**Codex：**
```bash
# Codex reaps background processes. The script auto-detects CODEX_CI and
# switches to foreground mode. Run it normally — no extra flags needed.
scripts/start-server.sh --project-dir /path/to/project --open
```

**Copilot CLI：**
```bash
# Use --foreground and start the server via the bash tool with mode: "async"
# so the process survives across turns. Capture the returned shellId for
# read_bash / stop_bash if you need to interact with it later.
scripts/start-server.sh --project-dir /path/to/project --open --foreground
```

**其他环境：** 服务器必须在后台跨对话轮次持续运行。如果你的环境会回收脱离的进程，使用 `--foreground`，并用你平台的后台执行机制启动该命令。

如果从浏览器无法访问该 URL（远程/容器化环境中常见），绑定一个非回环主机：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

使用 `--url-host` 控制返回的 URL JSON 中打印的主机名。

## 循环

1. **确认服务器存活**，然后**写 HTML** 到 `screen_dir` 中的一个新文件：
   - **必须：在引用 URL 或推送屏幕之前确认服务器存活。** 检查 `$STATE_DIR/server-info` 存在且 `$STATE_DIR/server-stopped` 不存在。如果它已停止，用**相同的 `--project-dir`** 通过 `start-server.sh` 重启——它会复用相同端口，因此用户打开的标签页会自动重连（服务器宕机期间它会显示一个"已暂停"遮罩），你不需要发送新 URL。服务器在闲置 4 小时后自动退出（可用 `--idle-timeout-minutes` 配置）。
   - 使用语义化文件名：`platform.html`、`visual-style.html`、`layout.html`
   - **永远不要复用文件名** —— 每个屏幕都用一个新文件
   - 使用你的文件创建工具——**永远不要用 cat/heredoc**（会把噪音灌进终端）
   - 服务器自动提供最新的文件

2. **告诉用户预期内容并结束你的回合：**
   - 提醒他们 URL（每一步都提醒，不只是第一次）
   - 对屏幕上的内容做简短文字摘要（例如"正在展示首页的 3 种布局选项"）
   - 请他们在终端回复："看一下并告诉我你的想法。如果想要可以点击选择一个选项。"

3. **在你的下一轮** —— 用户在终端回复之后：
   - 读取 `$STATE_DIR/events`（如果存在）——它包含用户的浏览器交互（点击、选择），以 JSON 行记录
   - 与用户的终端文本合并，得到完整图景
   - 终端消息是主要反馈；`state_dir/events` 提供结构化的交互数据

4. **迭代或推进** —— 如果反馈改变了当前屏幕，写一个新文件（例如 `layout-v2.html`）。只有在当前步骤被验证后才进入下一个问题。

5. **回到终端时卸载内容** —— 当下一步不需要浏览器时（例如澄清问题、取舍讨论），推送一个等待屏幕来清除过时内容：

   ```html
   <!-- filename: waiting.html (or waiting-2.html, etc.) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

   这可以防止用户在对话已经推进时还盯着已解决的选项看。当下一个视觉问题出现时，照常推送新的内容文件。

6. 重复直到完成。

## 编写内容片段

只写放进页面内部的内容。服务器会自动把它包进框架模板（头部、主题 CSS、连接状态和全部交互基础设施）。

**最小示例：**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

就这样。不需要 `<html>`、不需要 CSS、不需要 `<script>` 标签。服务器提供所有这些。

## 可用的 CSS 类

框架模板为你的内容提供以下 CSS 类：

### 选项（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

**多选：** 在容器上添加 `data-multiselect`，让用户可以选择多个选项。每次点击切换该项的选中样式。

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select/deselect multiple -->
</div>
```

### 卡片（可视化设计）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### 模型稿容器

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### 分屏视图（并排）

```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

### 优点/缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### 模拟元素（线框图构件）

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### 排版和小节

- `h2` —— 页面标题
- `h3` —— 小节标题
- `.subtitle` —— 标题下方的次要文本
- `.section` —— 带下边距的内容块
- `.label` —— 小号大写标签文本

## 浏览器事件格式

当用户在浏览器中点击选项时，他们的交互会被记录到 `$STATE_DIR/events`（每行一个 JSON 对象）。当你推送新屏幕时该文件会自动清空。

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

完整的事件流展示了用户的探索路径——他们可能在定案前点击多个选项。最后一个 `choice` 事件通常是最终选择，但点击的模式可以揭示犹豫或偏好，值得追问。

如果 `$STATE_DIR/events` 不存在，说明用户没有与浏览器交互——只使用他们的终端文本。

## 设计技巧

- **保真度随问题伸缩** —— 布局问题用线框图，打磨问题用精细稿
- **在每个页面上说明问题** —— 写"哪种布局感觉更专业？"而不只是"选一个"
- **推进前先迭代** —— 如果反馈改变了当前屏幕，写一个新版本
- 每个屏幕**最多 2-4 个选项**
- **重要时使用真实内容** —— 对于摄影作品集，使用真实图片（Unsplash）。占位内容会掩盖设计问题。
- **保持模型稿简单** —— 聚焦布局和结构，而不是像素级完美的设计

## 文件命名

- 使用语义化名称：`platform.html`、`visual-style.html`、`layout.html`
- 永远不要复用文件名——每个屏幕必须是新文件
- 迭代版本：追加版本后缀，如 `layout-v2.html`、`layout-v3.html`
- 服务器按修改时间提供最新文件

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

如果会话使用了 `--project-dir`，模型稿文件会保留在 `.brainstorm/` 中供日后参考。只有 `/tmp` 会话会在停止时被删除。

## 参考

- 框架模板（CSS 参考）：`scripts/frame-template.html`
- 辅助脚本（客户端）：`scripts/helper.js`
