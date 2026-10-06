# 认证与配置

所有业务接口需要认证。先运行 `etfirst config` 检查配置；已有凭据时直接查询，不必重复索取密钥。

```bash
etfirst auth login --api-key <KEY>
etfirst config
etfirst auth logout
etfirst auth logout --purge-key
```

CLI 0.4.2 将 API Key 保存在 `~/.cli_anything/etfapp/config.json`，会话保存在同目录的 `session.json`。`ETFAPP_CLI_CONFIG`、`ETFAPP_CLI_SESSION` 可覆盖路径；`--session-file` 可覆盖会话路径。CLI 不自动读取项目 `.env`，也没有直接读取 API Key 环境变量的入口。

登录默认持久化密钥，用于会话失效后自动续期；升级或清除会话不会清除密钥。普通 `logout` 保留密钥，`logout --purge-key` 同时清除。密钥不放进技能、版本库或输出中。

`config` 的 `api_key_saved` 表示已保存密钥，`config_file`、`session_file` 给出实际路径。0.4.2 的 `logged_in` 根据本地 user 字段计算，可能在可正常查询时仍为 false；以实际业务调用成功作为认证可用的依据。

| 错误码 | 含义 | 处理 |
|---|---|---|
| `C0100` | 缺少密钥 | 检查登录参数 |
| `C0101` | 密钥无效 | 核对密钥 |
| `C0102` | 密钥被禁用 | 联系管理员 |
| `C0104` | 密钥过期 | 获取新密钥 |
| `A0302` / `A0303` | 会话失效 | 已保存密钥时由 CLI 自动续期；失败后重新登录 |
