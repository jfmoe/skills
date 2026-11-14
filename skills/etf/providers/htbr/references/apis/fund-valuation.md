# fund-valuation

| 项 | 值 |
|---|---|
| `api_id` | `fund-valuation` |
| 服务端登记名 | 基金市值与估值 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有；dataservice 通道直连，上游单位口径以报表为准） |

## 1. 功能与适用场景

查询基金**持仓组合的整体市值与估值**指标：总市值（亿元）、流通市值（亿元）、PE(TTM)、PB、股息率，按报告期逐行输出，用于判断持仓风格与估值贵贱。

适用：用户问「这只基金持仓的 PE/PB 多少」「组合贵不贵」「股息率多少」「持仓总市值多大」。

业务入口为统一入口 `POST /api/v1/business/fund-valuation:invoke`（dataservice 通道直连第三方报表）。

## 2. 不适用场景与易混接口

- 这是**持仓组合层面的加权估值**，不是基金净值、也不是单只股票估值。
- 与 `fund-asset-size` 的区别：那个是**基金资产规模**（元），本接口是**持仓股票的市值与估值指标**。
- 不提供行业或个股维度（分别见 `fund-industry-dist`、`fund-holding-detail`）。
- ⚠ **入参是基金内码 `innerCode`**（单值），不是 6 位代码 / GilCode / 旧版 `fundObject` 列表；可先用 `fund-resolve` 把代码解析为内码。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `innerCode` | number 或数字字符串 | **是** | 正整数基金内码；零、负数、小数、布尔值、数组、对象、空值均不合法 |
| `beginDate` | string | 否 | 报告期下界，格式 `yyyy-MM-dd`（闭区间）；空 = 无下界（不下推）；传了且非该格式 → 400 |
| `endDate` | string | 否 | 报告期上界，格式 `yyyy-MM-dd`（闭区间）；空 = 无上界（不下推）；传了且非该格式 → 400 |

> 上游为 dataservice 报表 `RAGAPI.Research.Fund.FundMarketVAndValuationReport`；服务端把 `innerCode` 转换为报表的 `fundObject=[innerCode]` 单元素列表（与 `fund-daily-quote` / etf 系同款转换）。下推的 `fundObject` / `beginDate` / `endDate` 三个键与 DS 请求类 `@JsonProperty` 逐字一致（**全小写**，DS 侧大小写敏感，写成 `BeginDate` 会被静默忽略）。**入参不再支持旧 SQL 版的 `fundObject` 列表。**

## 4. 调用示例

```bash
# 指定报告期区间（两个日期均按 yyyy-MM-dd 传）
pixi run etf-htbr invoke fund-valuation '{"innerCode":"4848","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 全部报告期
pixi run etf-htbr invoke fund-valuation '{"innerCode":4848}'
```

`<SKILL_DIR>` 必须替换为本技能实际目录，使用本包自己的客户端。只有基金名称、证券代码或 GilCode 时，先按基金解析工作流调用 `fund-resolve` 取 `candidates[0].innerCode`；多候选等待用户确认。

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `innerCode` | 请求内码回显（整数） |
| `beginDate` / `endDate` | 请求区间回显（未传为 `null`） |
| `recordCount` | 记录数 |
| `records[]` | 报告期记录，行字段与 DS 报表列名逐字一致（全小写），共 10 字段 |

`records[]` 行字段：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundcode` | string | 基金代码 |
| `fundobject` | number | 基金内码 |
| `fundname` | string | 基金简称 |
| `reportdate` | string | 报告期 |
| `reporttype` | string | 报告类型 |
| `totalmv` | number | 总市值（**亿元**） |
| `negotiablemv` | number | 流通市值（**亿元**） |
| `pettm` | number | PE(TTM) |
| `pb` | number | PB |
| `dividendratio` | number | 股息率 |

> **行粒度 = 报告期**：同一基金每个报告期一行（上游按转型链主体分组出行，行身份列以 `fundobject`/`fundcode` 为准，不要用请求内码覆盖）。

## 6. 数据口径

- 上游为 dataservice 报表 `RAGAPI.Research.Fund.FundMarketVAndValuationReport`，固定 `JSON2`、`Compress=false`、`fundObject=[innerCode字符串]`。这些是服务端固定参数，不是客户端入参；返回条数以线上实际为准。
- 各指标为**持仓市值加权**：权重 = 个股市值 / 组内持仓市值合计；`reporttype` 为上游输出的报告类型描述。
- **单位**：`totalmv`/`negotiablemv` 为**亿元**（上游报表已换算，平台不二次换算）；`pettm`/`pb` 无量纲；`dividendratio` 为百分比口径原值，不再乘 100。展示时直接按亿元解读，不要再做万/元换算。
- `beginDate`/`endDate` 为闭区间，服务端只在传值时下推（空值不下推）。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `innerCode` 缺失/非正整数，或日期参数非 `yyyy-MM-dd` |
| 200 + `NO_DATA` 注记 | 上游成功但区间内无报告期记录（`recordCount=0`），如实说明 |
| 上游取数失败 | 服务端返回 **503 `DEGRADED`**（`error.detail` 含 apiId 与 reason），须如实告知该接口暂不可用，不得编造数据 |
| `pettm` / `pb` = `null` | 分母为 0 或取不到，**不是 0**，展示为「—」；**负值照常输出**（亏损股），不要改写 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **`innerCode` 是基金内码**（不是 6 位代码 / GilCode）；可先用 `fund-resolve` 解析。
- 单基金查询（单值入参，不支持旧版多基金数组）。

## 9. 相关工作流

- 需要从基金代码得到内码时，先读 `workflows/fund-code-resolution.md`。

## 10. 验证与交付边界

权威契约见仓库 `docs/htbr-ai-skill/02-接口契约.md`。验收包括数值/数字字符串内码、非法入参（含日期格式）、固定上游参数、10 字段全小写原样（不含 `stockcodeinteger`）、市值单位为亿元、无记录与上游失败不伪造，以及解析后续调。源包文档检查不等于真实接口联调、注册放行或发布成功；交付镜像仅允许经 `sync_kit.py` 同步，缺失时不得手工复制。
