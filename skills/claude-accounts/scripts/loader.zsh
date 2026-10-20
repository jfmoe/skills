# Managed by the claude-accounts skill; reinstall with `accounts.sh init` instead of editing.
# Defines one launcher per account file (<name>.token or <name>.login) in the accounts dir:
#   main   -> claude        (config dir ~/.claude)
#   <name> -> claude-<name> (config dir ~/.claude-<name>)
# A .token account passes its token; a .login account uses the keychain login of its config dir.

_claude_accounts_dir=$HOME/.config/claude-accounts

_claude_account_token() {
  local file=$_claude_accounts_dir/$1.token line
  [[ -r $file ]] || return 0
  while IFS= read -r line || [[ -n $line ]]; do
    line=${line//[[:space:]]/}
    [[ -z $line || $line == \#* ]] && continue
    print -r -- $line
    return 0
  done < $file
}

_claude_account_run() {
  local name=$1 token
  shift
  token=$(_claude_account_token $name)
  # Clear both variables so a launcher started inside another account's session
  # never inherits that account's config dir or token.
  local -a env_args=(-u CLAUDE_CONFIG_DIR -u CLAUDE_CODE_OAUTH_TOKEN)
  [[ $name != main ]] && env_args+=(CLAUDE_CONFIG_DIR=$HOME/.claude-$name)
  # A login account, or an empty token, falls back to the keychain login of the config dir.
  [[ -n $token ]] && env_args+=(CLAUDE_CODE_OAUTH_TOKEN=$token)
  env $env_args claude "$@"
}

() {
  local file name cmd
  for file in $_claude_accounts_dir/*.(token|login)(N); do
    name=${file:t:r}
    [[ $name =~ '^[a-z0-9]+(-[a-z0-9]+)*$' ]] || continue
    [[ $name == main ]] && cmd=claude || cmd=claude-$name
    unalias $cmd 2>/dev/null
    eval "$cmd() { _claude_account_run $name \"\$@\" }"
  done
}
