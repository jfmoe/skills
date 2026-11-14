# 认证与配置

所有业务接口需要认证。先运行 `etfirst config` 检查配置；已有凭据时直接查询，不必重复索取密钥。

```bash
etfirst auth login --api-key <KEY>
etfirst config
etfirst auth logout
etfirst auth logout --purge-key
```

CLI 0.4.2 将 API Key 保存在 `~/.cli_anything/etfapp/config.json`，会话保存在同目录的 `session.json`。`ETFAPP_CLI_CONFIG`、`ETFAPP_CLI_SESSION` 可覆盖路径；`--session-file` 可覆盖会话路径。CLI 不自动读取项目 `.env`，也没有直接读取 API Key 环境变量的入口。

登录默认持久化密钥，用于会话失效后自动续期；升级或清除会话不会清除密钥。

0.4.2 的自动续期有缺陷：会话过期后本地仍留着旧的会话 cookie，CLI 看到 cookie 存在就不重新登录，于是报“Session 已过期或不存在，请重新登录”。已保存密钥时不需要用户重新输入密钥：运行 `etfirst auth logout`（只清会话，保留密钥），再重试原命令，CLI 会用保存的密钥自动登录。2026-11-14 实测有效。只有 `config` 显示 `api_key_saved` 为假，或重试后报密钥无效、过期时，才请用户执行 `etfirst auth login --api-key <KEY>`。普通 `logout` 保留密钥，`logout --purge-key` 同时清除。密钥不放进技能、版本库或输出中。

`config` 的 `api_key_saved` 表示已保存密钥，`config_file`、`session_file` 给出实际路径。0.4.2 的 `logged_in` 根据本地 user 字段计算，可能在可正常查询时仍为 false；以实际业务调用成功作为认证可用的依据。

| 错误码 | 含义 | 处理 |
|---|---|---|
| `C0100` | 缺少密钥 | 检查登录参数 |
| `C0101` | 密钥无效 | 核对密钥 |
| `C0102` | 密钥被禁用 | 联系管理员 |
| `C0104` | 密钥过期 | 获取新密钥 |
| `A0302` / `A0303`，或“Session 已过期或不存在” | 会话失效 | 已保存密钥时先 `etfirst auth logout` 再重试；仍失败才请用户重新登录 |
