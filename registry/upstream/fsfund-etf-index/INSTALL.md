# fsfund-etf-index Skill 安装指南

安装完成后，通过 **`scripts/etf_index.py`** 动态获取本 Skill 绑定的接口列表与出入参，再调用业务接口。

## 前提条件

- Python **3.8+**
- **`HJ_APP_SECRET`**（Header `hjAppSecret`）
- 可选 **`HJ_BASE_URL`**、**`HJ_SKILL_URL`**（默认 `fsfund-etf-index`）

## 目录结构

```text
fsfund-etf-index/
├── SKILL.md
├── INSTALL.md
├── scripts/
│   ├── etf_index.py      # 主 CLI：refresh-meta / list-apis / schema / call
│   ├── hj_client.py      # HTTP 客户端
│   ├── meta_registry.py  # 元数据解析与缓存
│   └── api_client.py     # 兼容：仅直接 call
└── .cache/               # 运行后生成 meta_registry.json
```

## 配置环境变量

**PowerShell：**

```powershell
$env:HJ_APP_SECRET = "您的密钥"
$env:HJ_BASE_URL = "https://app.fsfund.com/apps/cerdo/udsp-api/udsp/skill/v01/"
$env:HJ_SKILL_URL = "fsfund-etf-index"
```

**CMD：**

```cmd
set HJ_APP_SECRET=您的密钥
set HJ_BASE_URL=https://app.fsfund.com/apps/cerdo/udsp-api/udsp/skill/v01/
set HJ_SKILL_URL=fsfund-etf-index
set HJ_META_CACHE_SEC=3600
```

**bash / Linux / macOS：**

```bash
export HJ_APP_SECRET="您的密钥"
export HJ_BASE_URL="https://app.fsfund.com/apps/cerdo/udsp-api/udsp/skill/v01/"
export HJ_SKILL_URL="fsfund-etf-index"
```

## 验证安装

### 1. 拉取元数据

```bash
cd <skill-dir>
python scripts/etf_index.py refresh-meta
```

预期：生成 `.cache/meta_registry.json`，并打印接口数量。

底层调用：`POST …/get_udsp_2_api_out_in_param`，Body `{"skill_url":"fsfund-etf-index"}`。

### 2. 列出接口

```bash
python scripts/etf_index.py list-apis
python scripts/etf_index.py list-apis --json
```

预期：表格中 **PATH** 列为业务接口名（如 `INF_FUND_INFO`）。

### 3. 查看 schema

```bash
python scripts/etf_index.py schema INF_FUND_INFO
```

预期：入参表、必填组、出参表。

### 4. 业务调用

```bash
python scripts/etf_index.py call INF_FUND_INFO "{\"IS_ETF_FUND\":\"是\",\"TRACK_INDX_WINDCODE\":\"000300.SH\",\"currentPage\":\"1\"}"
```

## 元数据机制

| 项 | 说明 |
|----|------|
| 元数据接口 | `get_udsp_2_api_out_in_param` |
| 入参 | `skill_url` = `fsfund-etf-index`（可用 `HJ_SKILL_URL` 覆盖） |
| 缓存文件 | `.cache/meta_registry.json` |
| 缓存时长 | `HJ_META_CACHE_SEC`，默认 3600 秒 |
| PATH | 元数据 `get_udsp_2_api_url.result[].PATH`，即 `call` 时使用的接口名 |

平台新增/修改接口后，执行 **`refresh-meta`** 即可，无需更新 Skill 文档。

## 常见问题

| 现象 | 处理 |
|------|------|
| 缺少 `HJ_APP_SECRET` | 设置环境变量后重试 |
| `未找到接口` | 先 `list-apis`，使用 PATH 列名称 |
| 元数据过期 | `refresh-meta` 或设 `HJ_META_CACHE_SEC=0` |
| 中文乱码 | `PYTHONUTF8=1` 或 `chcp 65001` |

详见 [SKILL.md](SKILL.md)。

**安全提示**：勿将 `HJ_APP_SECRET` 提交到仓库或公开渠道。
