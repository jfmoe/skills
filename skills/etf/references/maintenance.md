# 维护说明

本技能把三家基金公司的数据接口整理进一个入口。上游会变：发新版本、增删接口、开放此前未开放的接口。这里规定怎样发现变化、核对并更新技能。

## 文件归属

| 位置 | 内容 | 怎么改 |
|---|---|---|
| `~/Coder/skills/skills/etf/` | 技能源文件，唯一可以编辑的副本 | 直接编辑后提交 |
| `~/Coder/skills/registry/upstream/etfirst/`、`fsfund-etf-index/`、`htbr-etf-skill/` | 各上游包的原样存档和 `meta.yaml`（来源地址、版本、SHA-256、取得日期、改动说明） | 上游更新时整体替换并更新 `meta.yaml` |
| 各项目的 `.agents/skills/etf/` 等安装目录 | 从源仓库同步来的副本 | 不手改，按 `manage-skills` 技能重新同步 |
| `providers/htbr/references/apis/`、`workflows/`、`api-catalog.md` | 华泰柏瑞上游文档原文 | 只由 `sync_upstream.py` 生成，不手改 |
| `providers/htbr/references/availability.json` | 华泰柏瑞逐接口实测状态 | 只由 `probe.py` 生成 |
| 其余文档（入口、各指南、来源比较、能力核验、配置） | 自己写的路由、边界和证据 | 手工维护 |

## 什么时候检查

- 每季度一次；
- 调用中发现接口新增、消失、字段或口径变化，或此前未开放的接口开始返回数据；
- 用户要求。

检查会访问上游网站，华泰柏瑞的逐接口实测约占当日 500 次额度中的 72 次。所在项目对取数另有确认要求时照办。

## 检查步骤

下载的上游包一律解压到新建的临时目录，只读其中的文档和代码，**不运行**包里的安装、配置或更新脚本。

### 南方 ETFirst

1. 上游按版本号发布，没有“最新版本”页面。用只取响应头的请求查看当前版本的 `SKILL.md`（地址见 `registry/upstream/etfirst/meta.yaml`）的大小与修改时间，并试探后续版本号是否存在。
2. 没有新版本且文件未变：结束。
3. 有新版本：下载新版 `SKILL.md` 存档，与旧存档比较，把命令、参数和字段的变化改进 `providers/etfirst/` 的参考文件；项目里固定的 ETFirst 包地址（Fire 是 `pixi.toml`）一并升级。
4. 用一只已知 ETF 跑一次 `etf-detail all`，确认子接口与字段表一致。会话过期且自动续期失败时，由用户本人执行 `etfirst auth login --api-key <KEY>` 重新登录。

### 华宝 UDSP

1. 重新下载上游包，与存档比较 SHA-256。
2. 先备份 `providers/fsfund/.cache/meta_registry.json`，再运行 `list-apis` 刷新元数据，比较接口清单及每个接口的入参、出参。
3. 都没有变化：结束。有变化：接口定义本身由服务端动态下发，客户端无需改；把新增或消失的接口、枚举和单位变化更新到华宝指南、来源比较和能力核验。包内脚本变化时与 `providers/fsfund/scripts/` 逐文件比较后合入。

### 华泰柏瑞

1. 重新下载上游包，与存档比较 SHA-256，读包内 `SKILL.md` 的版本号和 `CHANGELOG.md`。
2. 包没有变化时仍可只做第 3 步，用来发现此前未开放的接口是否已开放。
3. 把 `providers/htbr/probe/payloads.tsv` 里的日期换成最近一个月和最近的报告期；上游新增接口时按其文档补一行。然后运行（约 72 次调用，带 3 秒间隔，约 5 分钟）：

   ```bash
   cd ~/Coder/fire
   H=~/Coder/skills/skills/etf/providers/htbr
   pixi run python -m dotenv -f .env run -- python $H/scripts/probe.py $H/probe/payloads.tsv "$(mktemp -d)" $H/references/availability.json
   ```

   在源仓库的文件上运行，密钥由 Fire 的 `.env` 提供，不写在命令行里。密钥无效或额度用完时它立即停止且不改写 `availability.json`；单个接口超时或网络错误记为“未确定”，不影响其他接口。
4. 同步文档并看差异报告：

   ```bash
   python sync_upstream.py <解压后的 htbr-etf-skill 目录>
   ```

   只有实测返回 404 的接口被当作未开放、不同步文档；其他错误的接口保留文档并列在报告的 `undetermined` 里，查明原因后重测。报告还列出新增、变化、删除的接口文档，以及“有文档但没实测”“实测过但文档已删除”的接口。
5. 状态为 200 但记录数为 0 或 `null` 的接口，逐个看原始响应，区分“样本无数据”和“实际未开放”。
6. 按结果更新华泰柏瑞指南的“独有或更强的能力”和“未开放接口”两节、来源比较里的分工表、入口的选择表。

## 更新之后

1. 更新对应的 `registry/upstream/<上游>/`：替换存档，改 `meta.yaml` 的 `ref`、SHA-256、`fetched_at`，在 `notes` 里写这次改了什么。
2. 更新[能力核验](capabilities.md)开头的核验日期和受影响的条目。只写实际调用得到的结果，文章或上游文档的说法不当作已验证。
3. 在源仓库运行 `npx skills add ~/Coder/skills --list`，确认 `etf` 仍只登记为一个技能，然后提交。
4. 按 `manage-skills` 技能把 `etf` 同步到已安装的项目和代理；项目里有依赖技能内容的说明（Fire 的 `docs/agents/data-sources.md`）时一并核对。

## 约束

- 密钥只放在环境变量或项目的 `.env` 里，不写进技能文件、提交或对话。
- 不为了核对而做全市场、全历史下载；每个接口一个样本即可。
- 新接入第四个来源时，照华泰柏瑞的做法：存档上游包，写最小客户端，逐接口实测后才登记能力，并补进本文件。
