# 环境与认证

技能包内只有一个 `SKILL.md`；提供方文档和华宝客户端均在包内。ETFirst 是独立运行时依赖，凭据不随包分发。

## Fire 项目

- 南方：`pixi run etfirst --help`，认证与状态见[ETFirst 认证](../providers/etfirst/references/auth.md)。沿用已登录的本机配置，不重复登录或更改凭据位置。
- 华宝：`pixi run etf-fsfund list-apis`。任务使用已有 `python-dotenv` 从根目录 `.env` 加载 `HJ_APP_SECRET`；`.env` 保持 Git 忽略。查询本身无需修改 `.env`。

## 本机 Hermes

Hermes 专属技能位于 `${HERMES_HOME:-$HOME/.hermes}/skills/etf`。本机 Fire 项目在 `$HOME/Coder/fire`；可复用其运行时和凭据，无需复制密钥或在 Hermes 环境全局安装依赖。即使当前目录不在 Fire，也可执行：

```bash
fire_root="$HOME/Coder/fire"
etf_skill_root="${HERMES_HOME:-$HOME/.hermes}/skills/etf"
"$fire_root/.pixi/envs/default/bin/etfirst" --json index-base clas --type 2
"$fire_root/.pixi/envs/default/bin/python" -m dotenv -f "$fire_root/.env" run -- \
  "$fire_root/.pixi/envs/default/bin/python" \
  "$etf_skill_root/providers/fsfund/scripts/etf_index.py" list-apis
```

南方继续读取用户级 ETFirst 配置，华宝仅在子进程中加载 Fire `.env`。命令使用绝对路径，不依赖 gateway 的 PATH 或当前目录；只读取需要的配置，不打印文件内容。若 Fire 迁移或环境不存在，先定位新项目路径或按下一节配置运行时。技能更新后在 Hermes 新会话使用，已有会话可 `/reset`。

## 其他项目

南方使用 Python 3.8+ 与 ETFirst 0.4.2，包来自[官方版本下载](https://www.nffund.com/wxfiles/miniapp/openu/static/assets/etfirst/0.4.2/etfirst-0.4.2.tar.gz)。按目标项目依赖管理器安装，不默认全局安装；安装后运行 `etfirst --help` 并按包内认证指南登录。

华宝客户端建议使用 Python 3.10+，Fire 已在 Python 3.12 下验证。可直接设置 `HJ_APP_SECRET` 后调用脚本；使用 `.env` 时需要 `python-dotenv[cli]`，在项目根目录执行：

```bash
python -m dotenv -f .env run -- python <技能目录>/providers/fsfund/scripts/etf_index.py list-apis
```

| 环境变量 | 华宝含义 |
|---|---|
| `HJ_APP_SECRET` | 必填密钥，经 `hjAppSecret` 请求头发送 |
| `HJ_BASE_URL` | 默认 `https://app.fsfund.com/apps/cerdo/udsp-api/udsp/skill/v01/` |
| `HJ_SKILL_URL` | 默认 `fsfund-etf-index` |
| `HJ_META_CACHE_SEC` | 元数据缓存有效秒数，默认 3600 |

只需配置密钥，其余变量默认即可。验证顺序：`list-apis` → `schema INF_FUND_INFO` → 按 schema 查询一个已知基金，检查业务成功与返回记录。错误时保留状态和服务端说明，不回显密钥。南方的配置 JSON 与华宝 `.env` 是两套独立认证，不能互换。
