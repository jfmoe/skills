---
name: claude-accounts
description: 维护本机 Claude Code 多账号切换（token 或钥匙串登录）：新增、删除、更换、检查、迁移账号。
disable-model-invocation: true
---

# Claude Code 多账号

## 方案

每个账号 = 一个配置目录 + 一个账号文件 + 一个启动命令：

| 账号名 | 启动命令 | 配置目录 | 账号文件（在 `~/.config/claude-accounts/` 下） |
| --- | --- | --- | --- |
| `main` | `claude` | `~/.claude` | `main.token` 或 `main.login` |
| `<name>` | `claude-<name>` | `~/.claude-<name>` | `<name>.token` 或 `<name>.login` |

新账号的名字按序号分配：`main` 算 1 号，`add` 不带名字时取已占用的最大序号加 1（`2`、`3`……）。只要账号文件或配置目录还在，这个序号就算被占用。迁移前就有的命名账号（如 `alt`）沿用原名。

- **加载器** `~/.config/claude-accounts/accounts.zsh`，由 `~/.zshrc` source。它为每个账号文件定义一个启动函数，先清掉继承来的 `CLAUDE_CONFIG_DIR`、`CLAUDE_CODE_OAUTH_TOKEN`，再设置本账号的值。没有账号文件的账号就没有启动函数，`main` 没有账号文件时，`claude` 还是原程序。新增或删除账号后，要开新终端或运行 `source ~/.zshrc` 才生效。
- **适用环境**：macOS，登录 shell 为 zsh。脚本只依赖系统自带工具；`rebind` 保留 MCP 配置需要 `jq`（macOS 15 起内置），缺少时会提示手动复制。在新电脑上先走「初始化或迁移」。
- **共享配置**：非 main 账号的配置目录用软链接指向 `~/.claude` 里的共享项（清单见 `scripts/accounts.sh` 的 `SHARED_ITEMS`）。账号状态不共享：`.claude.json`、历史和钥匙串条目都按配置目录各自独立。

### 认证方式

每个账号选一种认证方式，由用户决定：

| | token（`--token`） | 钥匙串登录（`--login`） |
| --- | --- | --- |
| 账号文件 | `<name>.token`，存 `claude setup-token` 生成的 token，权限 600 | `<name>.login`，只是标记，不存凭证 |
| 凭证存放 | 明文文件，启动时作为环境变量传入，子进程都能读到 | 钥匙串加密保存，按配置目录区分条目 |
| 有效期 | 一年，不会自动刷新，到期要手动续期 | 自动刷新 |
| 功能 | 只能调用模型，用不了 Remote Control 和 claude.ai connectors；`--bare` 模式不读它；状态栏查用量可能被拒绝 | 完整 |
| 适合 | 钥匙串不可用（如 SSH 会话），或不想用钥匙串 | 一般情况 |

token 账号的 token 文件为空时，会回退到同一配置目录下的钥匙串登录。

## 认证由用户手动完成

你负责准备账号文件、讲清步骤，并用 `accounts.sh list` 验收。获取凭证的每一步都由用户在自己的终端、浏览器和编辑器里手动完成：运行 `claude setup-token`、把 token 填进文件、启动账号命令、执行 `/login` 和 `/status`。凭证因此不会进入会话：

- 账号状态只用 `accounts.sh list` 判断，它只输出 `filled` / `empty` / `missing` 和 `present` / `absent`。token 文件只交给 `open -t` 打开。
- 让用户在**独立终端窗口**运行 `claude setup-token`。在会话里用 `!` 运行，会把 token 打印进对话记录。
- 用户把 token 贴进对话时，提醒对方这个 token 已经暴露，建议重新生成并改写文件。

## 操作

脚本在本 skill 目录下：`scripts/accounts.sh <command>`，不带参数运行会打印完整用法。下面每一节都是一条独立的分支。

### 初始化或迁移

1. 运行 `accounts.sh init`，它会安装或更新加载器，并报告 `~/.zshrc` 的状态。
2. 如果 `~/.zshrc` 还没有 source 加载器，就在文件末尾加上：
   ```zsh
   [ -r ~/.config/claude-accounts/accounts.zsh ] && source ~/.config/claude-accounts/accounts.zsh
   ```
   放在末尾，是为了让它定义的函数覆盖前面的同名定义。
3. 迁移哪些账号由用户决定，只处理用户点名的账号，每个账号都要让用户选认证方式。对 init 报告的每条旧 alias（如 `alias claude-alt='CLAUDE_CONFIG_DIR=… claude'`），先运行 `accounts.sh add <name> --token` 或 `--login`，再删掉这条 alias 及其说明注释。旧账号已经在钥匙串里登录过，选 `--login` 就不用再做别的。
4. 选了 `--token` 的账号，按「新增」第 3 步的 token 流程完成。

完成标准：`accounts.sh list` 列出所有点名的账号，`~/.zshrc` 里不再有 `claude` 相关的 alias。

### 新增

1. 把「认证方式」表格里的对比讲给用户，让对方选 token 还是钥匙串登录。
2. 运行 `accounts.sh add --token` 或 `accounts.sh add --login`（不带名字，按序号分配）。它会建好配置目录和共享链接，并生成账号文件。token 方式会生成带填写说明的 token 文件，并用默认文本编辑器打开。
3. 告诉用户新账号的启动命令，以及对应的步骤：
   - **token**：在独立终端运行 `claude setup-token`，在浏览器里确认登录的是新账号，然后授权；把 token 粘贴进已打开的文件，保存；开一个新终端运行新命令，用 `/status` 确认账号正确。
   - **钥匙串登录**：开一个新终端运行新命令，在会话里执行 `/login`，在浏览器里登录新账号；再用 `/status` 确认账号正确。
4. 用户说完成后运行 `accounts.sh list`：token 账号的 TOKEN 列应该是 `filled`；钥匙串账号的 KEYCHAIN 列应该是 `present`。
5. 如果 token 账号的 KEYCHAIN 列是 `present`，问用户要不要运行 `accounts.sh drop-keychain <name>` 删掉钥匙串登录，彻底不用钥匙串。

完成标准：`list` 的结果符合第 4 步，并且用户已经用 `/status` 确认了账号。

### 切换认证方式

同一个 Claude 账号，在 token 和钥匙串登录之间切换：运行 `accounts.sh add <name> --token` 或 `--login`，脚本会删掉另一种方式的账号文件。

- **改成 token**：按「新增」第 3 步之后的流程填 token，再按第 5 步问要不要删掉钥匙串登录。
- **改成钥匙串登录**：如果 KEYCHAIN 列是 `absent`，让用户在这个账号的会话里执行 `/login`。

如果换的是另一个 Claude 账号，走「更换账号」。

### 续期 token

同一个 Claude 账号的 token 过期或需要换新时：运行 `open -t ~/.config/claude-accounts/<name>.token`，让用户按文件里的说明重新生成 token，替换掉原来那一行；替换后要重启这个账号的会话才会用上新 token。新 token 如果属于另一个 Claude 账号，走「更换账号」。

### 更换账号

启动命令和配置目录不变，改成登录另一个 Claude 账号时，必须先清掉上一个账号的凭证和身份状态，否则会串号：token 为空时会回退到旧账号的钥匙串登录，`.claude.json` 及其备份里还留着旧账号的 `oauthAccount`、`userID`。

1. 向用户列出影响并得到确认，同时问新账号要不要换一种认证方式：
   - 会删除：钥匙串登录、配置目录里的 `.credentials.json`、旧 token 或登录标记；
   - 会移到废纸篓：状态文件（`main` 是 `~/.claude.json`，其他账号是 `<配置目录>/.claude.json`）和 `<配置目录>/backups/`；
   - 会清掉：状态栏按目录缓存的用量；
   - 新的状态文件只保留 `mcpServers`，项目信任、新手引导这些状态都会重置；
   - 历史、会话记录、file-history 保留。如果用户想连这些一起清掉，就改用「删除」里的 `--purge`，再 `add` 一个新序号；
   - 对 `main` 更换账号，还会重置桌面 App 本地会话的状态，因为 App 也用 `~/.claude.json`。
2. 运行 `accounts.sh rebind <name>`。不加参数沿用原来的认证方式，加 `--token` 或 `--login` 就改用另一种。只要还有会话在用这个配置目录，脚本就会报出这些进程的 PID 并拒绝执行，包括 `main` 对应的桌面 App。在这个账号自己的会话里也执行不了，要让用户先退出这些会话，再从普通终端或其他账号的会话里运行。
3. 按「新增」第 3 步之后的流程，让用户用新账号完成 token 填写或 `/login`，并验证。

完成标准：`list` 里这个账号的状态符合「新增」第 4 步，token 账号的 KEYCHAIN 为 `absent`，并且用户已经用 `/status` 确认显示的是新账号。

### 删除

- `accounts.sh remove <name>`：只删账号文件，启动命令在新终端里消失；配置目录和钥匙串登录都保留，以后还能用同一个名字 `add` 回来。对 `main` 执行时，`claude` 变回原程序，用 `~/.claude` 的钥匙串登录；如果钥匙串里也没有登录，就要先 `/login`。
- `accounts.sh remove <name> --purge`：会把配置目录移到废纸篓（里面有这个账号的历史、会话状态和 `.claude.json`），并删除钥匙串登录。执行前要向用户列出这些影响并得到确认。脚本不允许对 `main` 用 `--purge`。

完成标准：`accounts.sh list` 里这个账号的状态和所选的删除方式一致。

### 检查与修复

运行 `accounts.sh list`。MISSING_LINKS 列出的是 `~/.claude` 里有、但账号目录没链接的共享项，用 `accounts.sh add <name> --no-open` 补上，账号会保持原来的认证方式。`~/.claude` 里新增了需要共享的配置时，先把它加进 `SHARED_ITEMS`，再对每个账号这样补一遍。如果脚本报 `skipped link`，说明账号目录里已经有一个真实文件，要先跟用户确认保留哪一份再处理。MODE 为 `none` 的行是只剩配置目录的账号，比如没有加 `--purge` 删除的账号。
