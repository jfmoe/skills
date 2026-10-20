#!/bin/bash
# Maintain Claude Code accounts. Each account authenticates either with a token file
# (CLAUDE_CODE_OAUTH_TOKEN) or with a keychain login made by /login.
# Never prints token contents; reports only whether a token file is filled.
set -euo pipefail

ACCOUNTS_DIR="$HOME/.config/claude-accounts"
LOADER="$ACCOUNTS_DIR/accounts.zsh"
SHARED_HOME="$HOME/.claude"
# Items an account config dir links back to ~/.claude, when ~/.claude has them.
SHARED_ITEMS="CLAUDE.md settings.json hooks skills plugins statusline.sh projects agents commands output-styles keybindings.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  cat <<'EOF'
Usage: accounts.sh <command> [args]
  init                            Install the zsh loader and report shell setup
  list                            Show every account and its state
  add [NAME] [--token|--login] [--no-open]
                                  Create or repair account NAME (default: next sequence number).
                                  A new account needs a mode; an existing one keeps its mode
                                  unless another is given. Opens an unfilled token file.
  drop-keychain NAME              Delete the keychain login of account NAME
  rebind NAME [--token|--login] [--no-open]
                                  Prepare account NAME for a different Claude account: clear its
                                  credentials and identity state, keep MCP servers
  remove NAME [--purge]           Delete the account file; --purge also trashes the config dir
                                  and deletes the keychain login (not allowed for main)
NAME is "main" (~/.claude, command claude) or lowercase [a-z0-9-] (~/.claude-NAME, command claude-NAME).
New accounts are numbered: main counts as 1, so the first added account is 2.
Modes: token = ACCOUNTS_DIR/NAME.token holds a `claude setup-token` token;
       login = ACCOUNTS_DIR/NAME.login marks a keychain login made by /login.
EOF
}

die() { echo "error: $*" >&2; exit 1; }

check_name() {
  [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || die "invalid account name: $1"
}

config_dir() { [ "$1" = main ] && echo "$SHARED_HOME" || echo "$HOME/.claude-$1"; }
command_name() { [ "$1" = main ] && echo claude || echo "claude-$1"; }
account_file() { echo "$ACCOUNTS_DIR/$1.$2"; }
# Claude Code keeps global state beside the config dir only for the default dir.
state_file() { [ "$1" = main ] && echo "$HOME/.claude.json" || echo "$(config_dir "$1")/.claude.json"; }
trash_path() { echo "$HOME/.Trash/claude-$1-$(date +%Y%m%d%H%M%S)"; }

account_mode() {
  if [ -f "$(account_file "$1" token)" ]; then
    echo token
  elif [ -f "$(account_file "$1" login)" ]; then
    echo login
  else
    echo none
  fi
}

# Claude Code names the entry after sha256(CLAUDE_CONFIG_DIR) when the variable is set.
keychain_service() {
  if [ "$1" = main ]; then
    echo "Claude Code-credentials"
  else
    echo "Claude Code-credentials-$(printf %s "$(config_dir "$1")" | shasum -a 256 | cut -c1-8)"
  fi
}

token_state() {
  local file
  file="$(account_file "$1" token)"
  if [ ! -f "$file" ]; then
    echo missing
  elif grep -v '^[[:space:]]*#' "$file" | tr -d '[:space:]' | grep -q .; then
    echo filled
  else
    echo empty
  fi
}

keychain_state() {
  if security find-generic-password -s "$(keychain_service "$1")" >/dev/null 2>&1; then
    echo present
  else
    echo absent
  fi
}

missing_links() {
  local name="$1" dir item missing=""
  [ "$name" = main ] && return 0
  dir="$(config_dir "$name")"
  for item in $SHARED_ITEMS; do
    [ -e "$SHARED_HOME/$item" ] || continue
    [ "$(readlink "$dir/$item" 2>/dev/null)" = "$SHARED_HOME/$item" ] || missing="$missing $item"
  done
  echo "${missing# }"
}

ensure_accounts_dir() {
  mkdir -p "$ACCOUNTS_DIR"
  chmod 700 "$ACCOUNTS_DIR"
}

# Parses NAME, --token/--login, --no-open, --purge into ARG_NAME, ARG_MODE, ARG_OPEN, ARG_PURGE.
parse_args() {
  ARG_NAME="" ARG_MODE="" ARG_OPEN=1 ARG_PURGE=0
  local arg
  for arg in "$@"; do
    case "$arg" in
      --token) ARG_MODE=token ;;
      --login) ARG_MODE=login ;;
      --no-open) ARG_OPEN=0 ;;
      --purge) ARG_PURGE=1 ;;
      -*) die "unknown option: $arg" ;;
      *) ARG_NAME="$arg" ;;
    esac
  done
}

cmd_init() {
  ensure_accounts_dir
  cp "$SCRIPT_DIR/loader.zsh" "$LOADER"
  echo "installed loader: $LOADER"
  if grep -qF "claude-accounts/accounts.zsh" "$HOME/.zshrc" 2>/dev/null; then
    echo "zshrc: sources loader"
  else
    echo "zshrc: does not source loader"
  fi
  local hits
  hits="$(grep -nE '^[[:space:]]*alias claude(-[a-z0-9-]+)?=' "$HOME/.zshrc" 2>/dev/null || true)"
  [ -n "$hits" ] && printf 'zshrc: legacy aliases\n%s\n' "$hits"
  return 0
}

link_shared() {
  local dir="$1" item src dst
  for item in $SHARED_ITEMS; do
    src="$SHARED_HOME/$item"
    dst="$dir/$item"
    [ -e "$src" ] || continue
    if [ -L "$dst" ]; then
      [ "$(readlink "$dst")" = "$src" ] || echo "skipped link $item: points to $(readlink "$dst")"
    elif [ -e "$dst" ]; then
      echo "skipped link $item: a real file or directory exists"
    else
      ln -s "$src" "$dst"
      echo "linked $item"
    fi
  done
}

write_account_file() {
  local name="$1" mode="$2" file
  file="$(account_file "$name" "$mode")"
  [ -f "$file" ] && return 0
  (
    umask 077
    if [ "$mode" = token ]; then
      cat >"$file" <<EOF
# 账号 $name 的 CLAUDE_CODE_OAUTH_TOKEN（启动命令：$(command_name "$name")）
# 1. 打开一个独立终端窗口（不要在 Claude 会话里用 ! 运行），执行：claude setup-token
# 2. 在弹出的浏览器里确认登录的是这个账号，然后授权
# 3. 把终端打印的 token 粘贴到下面单独一行，保存并关闭
# 以 # 开头的行会被忽略

EOF
    else
      cat >"$file" <<EOF
# 账号 $name 用钥匙串登录（启动命令：$(command_name "$name")）
# 这个文件只是标记，不存放凭证。登录方法：在新终端运行 $(command_name "$name")，然后在会话里执行 /login
EOF
    fi
  )
  echo "created $mode file: $file"
}

# Switches account NAME to MODE, keeping an existing file of that mode untouched.
set_mode() {
  local name="$1" mode="$2" other
  [ "$mode" = token ] && other=login || other=token
  if [ -f "$(account_file "$name" "$other")" ]; then
    rm "$(account_file "$name" "$other")"
    echo "deleted $other file of $name"
  fi
  write_account_file "$name" "$mode"
  chmod 600 "$(account_file "$name" "$mode")"
}

open_unfilled_token() {
  local name="$1"
  if [ "$ARG_OPEN" = 1 ] && [ "$(token_state "$name")" != filled ]; then
    open -t "$(account_file "$name" token)"
    echo "opened token file in the default text editor"
  fi
  return 0
}

report_account() {
  local name="$1" mode
  mode="$(account_mode "$name")"
  if [ "$mode" = token ]; then
    echo "account $name: command $(command_name "$name"), config $(config_dir "$name"), mode token, token $(token_state "$name")"
  else
    echo "account $name: command $(command_name "$name"), config $(config_dir "$name"), mode $mode, keychain $(keychain_state "$name")"
  fi
}

# Highest numeric suffix in use plus one: a number stays taken while its account
# file or config dir exists, so a new account never inherits leftover state.
next_number() {
  local max=1 path n
  for path in "$ACCOUNTS_DIR"/*.token "$ACCOUNTS_DIR"/*.login "$HOME"/.claude-*; do
    [ -e "$path" ] || continue
    n="$(basename "$path")"
    n="${n%.token}"
    n="${n%.login}"
    n="${n#.claude-}"
    [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -gt "$max" ] && max="$n"
  done
  echo $((max + 1))
}

# PIDs of running Claude Code processes (CLI or Desktop) whose config dir is the account's.
claude_pids_for() {
  local dir pid comm cfg
  dir="$(config_dir "$1")"
  ps -A -o pid=,comm= | while read -r pid comm; do
    [ "${comm##*/}" = claude ] || continue
    cfg="$(ps eww -p "$pid" -o command= 2>/dev/null | grep -oE 'CLAUDE_CONFIG_DIR=[^ ]+' | head -1 || true)"
    cfg="${cfg#CLAUDE_CONFIG_DIR=}"
    [ "${cfg:-$SHARED_HOME}" = "$dir" ] && echo "$pid"
  done
  return 0
}

cmd_add() {
  parse_args "$@"
  local name="${ARG_NAME:-$(next_number)}" mode
  check_name "$name"
  [ -f "$LOADER" ] || die "loader not installed; run: accounts.sh init"
  mode="${ARG_MODE:-$(account_mode "$name")}"
  [ "$mode" != none ] || die "account $name has no mode yet; pass --token or --login"
  ensure_accounts_dir
  if [ "$name" != main ]; then
    mkdir -p "$(config_dir "$name")"
    link_shared "$(config_dir "$name")"
  fi
  set_mode "$name" "$mode"
  [ "$mode" = token ] && open_unfilled_token "$name"
  report_account "$name"
}

cmd_drop_keychain() {
  local name="${1:-}"
  [ -n "$name" ] || die "drop-keychain needs NAME"
  check_name "$name"
  if [ "$(keychain_state "$name")" = absent ]; then
    echo "keychain login of $name: already absent"
  else
    security delete-generic-password -s "$(keychain_service "$name")" >/dev/null
    echo "deleted keychain login of $name"
  fi
}

cmd_rebind() {
  parse_args "$@"
  local name="$ARG_NAME" mode dir state pids trash
  [ -n "$name" ] || die "rebind needs NAME"
  check_name "$name"
  dir="$(config_dir "$name")"
  [ "$(account_mode "$name")" != none ] || [ -d "$dir" ] || die "no account named $name"
  mode="${ARG_MODE:-$(account_mode "$name")}"
  [ "$mode" != none ] || die "account $name has no mode yet; pass --token or --login"
  state="$(state_file "$name")"
  # A running session rewrites the state file with the old identity on its next save.
  pids="$(claude_pids_for "$name")"
  [ -z "$pids" ] || die "quit the Claude Code sessions using $dir first (PIDs: $(echo $pids))"

  trash="$(trash_path "$name")-rebind"
  if [ -f "$state" ]; then
    mkdir -p "$trash"
    mv "$state" "$trash/"
    echo "moved $state to $trash"
    # MCP servers are machine tooling, not account identity; carry them over.
    local old="$trash/$(basename "$state")"
    if ! command -v jq >/dev/null 2>&1; then
      grep -q '"mcpServers"' "$old" && echo "warning: jq not found; MCP servers not carried over, copy them from $old"
    elif jq -e '.mcpServers | length > 0' "$old" >/dev/null 2>&1; then
      (umask 077; jq '{mcpServers}' "$old" >"$state")
      echo "kept MCP servers: $(jq -r '.mcpServers | keys | join(", ")' "$state")"
    fi
  fi
  # Backups hold copies of the old state file, which Claude Code can restore from.
  if [ -d "$dir/backups" ]; then
    mkdir -p "$trash"
    mv "$dir/backups" "$trash/"
    echo "moved $dir/backups to $trash"
  fi
  if [ -f "$dir/.credentials.json" ]; then
    rm "$dir/.credentials.json"
    echo "deleted $dir/.credentials.json"
  fi
  cmd_drop_keychain "$name"
  # The shared statusline caches plan usage per config dir under this name.
  rm -f "/tmp/claude/statusline-usage-$(printf %s "$dir" | md5).json"
  rm -f "$(account_file "$name" token)" "$(account_file "$name" login)"
  set_mode "$name" "$mode"
  [ "$mode" = token ] && open_unfilled_token "$name"
  report_account "$name"
}

cmd_remove() {
  parse_args "$@"
  local name="$ARG_NAME" mode
  [ -n "$name" ] || die "remove needs NAME"
  check_name "$name"
  [ "$ARG_PURGE" = 1 ] && [ "$name" = main ] && die "--purge never touches ~/.claude"
  for mode in token login; do
    if [ -f "$(account_file "$name" "$mode")" ]; then
      rm "$(account_file "$name" "$mode")"
      echo "deleted $mode file of $name"
    fi
  done
  if [ "$ARG_PURGE" = 1 ]; then
    local dir trash
    dir="$(config_dir "$name")"
    if [ -d "$dir" ]; then
      trash="$(trash_path "$name")"
      mv "$dir" "$trash"
      echo "moved config dir to $trash"
    fi
    cmd_drop_keychain "$name"
  elif [ "$name" != main ]; then
    echo "kept config dir $(config_dir "$name") and keychain login ($(keychain_state "$name"))"
  fi
}

cmd_list() {
  local names="main" file dir name mode token
  for file in "$ACCOUNTS_DIR"/*.token "$ACCOUNTS_DIR"/*.login; do
    [ -f "$file" ] || continue
    name="$(basename "$file")"
    names="$names ${name%.*}"
  done
  for dir in "$HOME"/.claude-*/; do
    [ -d "$dir" ] || continue
    name="$(basename "$dir")"
    names="$names ${name#.claude-}"
  done
  names="$(printf '%s\n' $names | sort -u)"
  printf '%-12s %-18s %-6s %-8s %-9s %s\n' NAME COMMAND MODE TOKEN KEYCHAIN MISSING_LINKS
  for name in $names; do
    [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || continue
    mode="$(account_mode "$name")"
    [ "$mode" = token ] && token="$(token_state "$name")" || token=-
    printf '%-12s %-18s %-6s %-8s %-9s %s\n' "$name" "$(command_name "$name")" \
      "$mode" "$token" "$(keychain_state "$name")" "$(missing_links "$name")"
  done
}

case "${1:-}" in
  init) cmd_init ;;
  list) cmd_list ;;
  add) shift; cmd_add "$@" ;;
  drop-keychain) shift; cmd_drop_keychain "$@" ;;
  rebind) shift; cmd_rebind "$@" ;;
  remove) shift; cmd_remove "$@" ;;
  *) usage; exit 2 ;;
esac
