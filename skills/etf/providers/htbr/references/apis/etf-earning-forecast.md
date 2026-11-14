# etf-earning-forecast

| 项 | 值 |
|---|---|
| `api_id` | `etf-earning-forecast` |
| 服务端登记名 | ETF基金指数盈利预测 |
| 领域 | etf |
| 资料完整度 | 完整（请求、响应、口径；上线与真实上游另验） |

## 1. 功能与适用场景

查询单只 ETF 跟踪指数的盈利预测报表：预测年度、截止日期、每股收益（期末股本摊薄）及其同比增长率、营业收入及其同比增长率、归母净利润及净利润同比增长率、是否预测值标记。用户问「这只 ETF 跟踪指数的盈利预测」「指数 EPS 预测」「营业收入/净利润预测」「预测年度多少」时使用。

业务入口为 `POST /api/v1/business/etfEarningForecast`（兼容壳，内部转调统一链路）；Skill 使用统一入口 `POST /api/v1/business/etf-earning-forecast:invoke`。

## 2. 不适用场景与易混接口

- 本接口出的是**指数层面**的盈利预测（含 `indexobject/indexcode/indexname/indexmarket`），不是基金自身财务指标，也不是成分股明细；要成分股用 `index-constituents`。
- 与 `etf-capital-report` 的边界：份额、净申购、近N日融资净买入、最新规模归 `etf-capital-report`。
- 与 `etf-margin` 的边界：两融明细归 `etf-margin`。
- 与 `etf-shares-change` 的边界：份额/规模期间变动归 `etf-shares-change`。
- 不提供基金自身估值（PE/PB）、业绩预告或分析师评级；不要按接口名猜测参数。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `innerCode` | number 或数字字符串 | 是 | 正整数基金内码；零、负数、小数、布尔值、数组、对象、空值均不合法 |
| `beginDate` | string | 否 | 开始日期 `yyyy-MM-dd`；空 = 上游缺省（`endDate` 前推 1 年）；格式不符 400 |
| `endDate` | string | 否 | 结束日期 `yyyy-MM-dd`；空 = 上游缺省当日；格式不符 400 |
| `unit` | number | 否 | 金额单位，取值 **1~7**（含义见下方速查表）；空 = 上游缺省 **3（万元）**；越界或非整数 400 |

**枚举取值速查**（唯一权威，构造请求前按此选值，不要猜）：

| 参数 | 值 → 含义 | 不传时 |
|---|---|---|
| `unit` | `1`=元 · `2`=千 · `3`=万 · `4`=百万 · `5`=千万 · `6`=亿 · `7`=十亿 | `3`（万元） |

`innerCode` 以外的三个参数均为**可选**，缺省时不向下游传（沿用上游默认语义），不传时行为与只有 `innerCode` 的老调用完全一致。按 `beginDate`/`endDate` 收窄可直接拿到指定披露区间内的预测版本。

只有基金名称、证券代码或 GilCode 时，先按基金解析工作流调用 `fund-resolve`，唯一命中后取 `candidates[0].innerCode`；多候选等待用户确认，零候选核对输入。不得把证券代码直接当内码。

## 4. 调用示例

以下内码仅展示格式，实际必须用已确认的基金内码替换：

```bash
pixi run etf-htbr invoke etf-earning-forecast '{"innerCode":"12345"}'
pixi run etf-htbr invoke etf-earning-forecast '{"innerCode":"12345","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd","unit":3}'
```

`beginDate`/`endDate` 是日期**占位**，实际调用须替换为具体日期（格式 `yyyy-MM-dd`），原样传 `yyyy-MM-dd` 会 400。示例里 `unit:3`（万元）的取值含义见 §3 速查表。

数字形式 `{"innerCode":12345}` 也可接受。`<SKILL_DIR>` 必须替换为本技能实际目录，使用本包自己的客户端。

## 5. 返回数据路径与关键字段

读 `$.data`：`innerCode` 为整数基金内码，`recordCount` 为本次记录条数，`records[]` 为记录数组。每条记录行字段与 DS 报表列名逐字一致（全小写），共 15 字段：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundobject` | string | 基金内码（原报表为字符列，原样返回） |
| `fundcode` | string | 基金代码，保留前导零 |
| `indexobject` | number | 指数内码 |
| `indexcode` | string | 指数代码 |
| `indexname` | string | 指数简称 |
| `indexmarket` | string | 指数市场 |
| `enddate` | string | 截止日期 |
| `forecastyear` | number | 预测年度 |
| `feps` | number | 每股收益_期末股本摊薄(元/股) |
| `fepsyoy` | number | 每股收益同比增长率(%) |
| `foperatingincome` | number | 营业收入 |
| `foperatingincomeyoy` | number | 营业收入同比增长率(%) |
| `fnpparentcomowners` | number | 归母净利润 |
| `fnpparentcomownersyoy` | number | 净利润同比增长率(%) |
| `ifforecast` | string | 是否预测值 |

## 6. 数据口径

- 上游为 dataservice 报表 `RAGAPI.ETFEarningForecast`，固定 `JSON2`、`Compress=false`，不传分页参数；`FundObject=[innerCode字符串]` 由服务端转换，`BeginDate`/`EndDate`/`Unit` 由客户端可选传入（缺省不下推，取上游默认：结束日=当日、开始日=结束日前推 1 年、单位=3 万元）。这些固定项不是客户端入参；返回条数以线上实际为准。
- **预测数据非承诺值**：`ifforecast` 标记该行是否预测值；回答须注明「盈利预测数据，非实际业绩，不代表未来表现」。
- 保留原报表单位和数值，**不得换算单位**；`feps` 单位为元/股（上游已注明），其余金额字段单位未明确时如实标注「单位以原报表为准，未明确」，不得臆断元/万元/亿元。
- 同比增长率字段（`fepsyoy` / `foperatingincomeyoy` / `fnpparentcomownersyoy`）为百分比口径，已是原报表数值，不再乘 100。
- 同一预测年度可能因 `enddate` 不同出现多行（预测随披露更新），按 `enddate` 区分新旧，不自行合并、去重或外推。
- 日期按 `enddate` 原样读取，`forecastyear` 为预测归属年度，两者口径不同不得混用。跨标的分析须对齐预测年度与原报表口径。

## 7. 空数据与异常值语义

- 上游成功无记录：`records=[]`、`recordCount=0`，如实说明无数据，不补造。
- 缺失字段或源空值展示「—」，不当作 0，不自行推算。
- 非法 `innerCode` 返回 HTTP 400 `PARAM_INVALID`；`beginDate`/`endDate` 非 `yyyy-MM-dd`、`unit` 不在 1~7 同样返回 400 `PARAM_INVALID`（不静默回退默认值）；上游失败沿服务端错误链返回失败，**不允许伪造成功记录或成功空数组**。
- 404 `API_NOT_FOUND` 表示未放行或不存在，如实告知，不借其他接口拼凑替代。

## 8. 前置条件与调用限制

需有效授权、已配置 API Key（`config.py status` 为 configured）、内网网关可达，遵循本 Skill 的凭证与限流规则，调用间隔建议 ≥3 秒。源包纳入不等于接口已上线，仍受服务端注册状态与当前 Key 的 scope 控制。

## 9. 相关工作流

见 `references/workflows/fund-code-resolution.md` 及 `references/apis/fund-resolve.md`。本接口目标字段是 `innerCode`，不要固定取 `secuCode` 或手工拼后缀。降级/演示解析结果不得作真实续调依据。

## 10. 验证与交付边界

权威契约见仓库 `docs/htbr-ai-skill/02-接口契约.md`（接口登记：附录 B.2 50 池 #27 行 + 本文件）。验收包括数值/数字字符串内码、非法入参、可选参数（`beginDate`/`endDate`/`unit`）缺省不下推与越界 400、固定上游参数、15 字段（含指数身份字段、预测年度与截止日期口径区分、增长率不乘 100、`ifforecast` 原样透传）、无记录及上游失败不伪造、不换算单位，以及解析后续调。源包文档检查不等于真实接口联调、注册放行或发布成功；交付镜像仅允许经 `sync_kit.py` 同步，缺失时不得手工复制。
