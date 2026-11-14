# etf-margin

| 项 | 值 |
|---|---|
| `api_id` | `etf-margin` |
| 服务端登记名 | ETF融资融券 |
| 领域 | etf |
| 资料完整度 | 完整（请求、响应、口径；上线与真实上游另验） |

## 1. 功能与适用场景

查询单只 ETF 的融资融券（两融）明细报表：融资买入额/偿还额/净买入额，融券卖出量/偿还量/净卖出量，期末融资余额、融券余额与融券余量，以及两融占流通市值比（融资、融券）。用户问「这只 ETF 融资融券」「融券余额/余量」「融券净卖出」「两融占流通市值比」时使用。

业务入口为 `POST /api/v1/business/etfMarginTrading`（兼容壳，内部转调统一链路）；Skill 使用统一入口 `POST /api/v1/business/etf-margin:invoke`。

## 2. 不适用场景与易混接口

- 与 `etf-capital-report` 的边界：本接口是**两融明细**（融资买入/偿还、融券卖出/偿还、融券余额/余量、占流通市值比）；`etf-capital-report` 是**资金报表**（份额、净申购、近N日融资净买入、最新规模）。问「融资余额」两者都有，问**融券**或**两融占比**只能用本接口；问「近N日融资净买入」「最新规模」用 `etf-capital-report`。
- 不提供场内资金流向（`etf-capital-flow`）或市场整体统计（`etf-capital-flow-stats`）。
- 不提供实时行情；区间由 `beginDate`/`endDate` 表达、粒度由 `indexCycle` 表达，不做全量历史分页；不要按接口名猜测参数。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `innerCode` | number 或数字字符串 | 是 | 正整数基金内码；零、负数、小数、布尔值、数组、对象、空值均不合法 |
| `beginDate` | string | 否 | 起始日期 `yyyy-MM-dd`；空 = 上游缺省（`endDate` 前推 1 年）；格式不符 400 |
| `endDate` | string | 否 | 结束日期 `yyyy-MM-dd`；空 = 上游缺省当日；格式不符 400 |
| `indexCycle` | number | 否 | 聚合周期，取值 **1~5**（含义见下方速查表）；空 = 上游缺省 **2（周）**；越界或非整数 400 |
| `unit` | number | 否 | 金额单位，取值 **1~7**（含义见下方速查表）；空 = 上游缺省 **3（万元）**；越界或非整数 400 |

**枚举取值速查**（唯一权威，构造请求前按此选值，不要猜）：

| 参数 | 值 → 含义 | 不传时 |
|---|---|---|
| `indexCycle` | `1`=日 · `2`=周 · `3`=月 · `4`=季 · `5`=年 | `2`（周） |
| `unit` | `1`=元 · `2`=千 · `3`=万 · `4`=百万 · `5`=千万 · `6`=亿 · `7`=十亿 | `3`（万元） |

`innerCode` 以外的四个参数均为**可选**，缺省时不向下游传（沿用上游默认语义），因此不传时行为与只有 `innerCode` 的老调用完全一致。`beginDate` 与 `endDate` 分别独立生效：只传其一时，另一端仍取上游缺省。

只有基金名称、证券代码或 GilCode 时，先按基金解析工作流调用 `fund-resolve`，唯一命中后取 `candidates[0].innerCode`；多候选等待用户确认，零候选核对输入。不得把证券代码直接当内码。

**周期性提醒**：`indexCycle` 缺省为 2（周），要日频明细必须显式传 `indexCycle=1`，否则返回的是按周聚合的行。

## 4. 调用示例

以下内码仅展示格式，实际必须用已确认的基金内码替换：

```bash
pixi run etf-htbr invoke etf-margin '{"innerCode":"12345"}'
pixi run etf-htbr invoke etf-margin '{"innerCode":"12345","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd","indexCycle":1,"unit":3}'
```

`beginDate`/`endDate` 是日期**占位**，实际调用须替换为具体日期（格式 `yyyy-MM-dd`），原样传 `yyyy-MM-dd` 会 400。示例里 `indexCycle:1`（日）、`unit:3`（万元）的取值含义见 §3 速查表。

数字形式 `{"innerCode":12345}` 也可接受。`<SKILL_DIR>` 必须替换为本技能实际目录，使用本包自己的客户端。

## 5. 返回数据路径与关键字段

读 `$.data`：`innerCode` 为整数基金内码，`recordCount` 为本次记录条数，`records[]` 为记录数组。每条记录行字段与 DS 报表列名逐字一致（全小写），共 16 字段：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundobject` | string | 基金内码（原报表为字符列，原样返回） |
| `fundcode` | string | 基金代码，保留前导零 |
| `fundname` | string | 基金简称 |
| `chiname` | string | 基金名称 |
| `tradingday` | string | 交易日期 |
| `financebuyvalue` | number | 融资买入-买入额 |
| `financerefundvalue` | number | 融资买入-偿还额 |
| `financenetbuyvalue` | number | 融资买入-净买入额 |
| `securitysellvolume` | number | 融券卖出-卖出量 |
| `securityrefundvolume` | number | 融券卖出-偿还量 |
| `securitynetsellvolume` | number | 融券卖出-净卖出量 |
| `financevalue` | number | 期末余额（余量）-融资余额 |
| `securityvalue` | number | 期末余额（余量）-融券余额 |
| `securityvolume` | number | 期末余额（余量）-融券余量 |
| `negotiablemvoffinance` | number | 两融占流通市值比-融资余额 |
| `negotiablemvofsecurity` | number | 两融占流通市值比-融券余额 |

## 6. 数据口径

- 上游为 dataservice 报表 `RAGAPI.ETFMarginTrading`，固定 `JSON2`、`Compress=false`，不传分页参数；`FundObject=[innerCode字符串]` 由服务端转换，`BeginDate`/`EndDate`/`IndexCycle`/`Unit` 由客户端可选传入（缺省不下推，取上游默认：结束日=当日、起始日=结束日前推 1 年、周期=2 周、单位=3 万元）。这些固定项不是客户端入参；返回条数以线上实际为准。
- `indexCycle` 决定行的时间粒度：周期桶按**日历周期末日**归并（周=周日、月/季/年末日），组内 `tradingday` 取该周期内最后一个交易日；6 个流量字段周期内求和、5 个存量字段取组内最新交易日值。传入 `indexCycle=1` 才是逐日明细。
- 保留原报表单位和数值，**不得换算单位**；金额（value）与量（volume）类字段单位未明确时如实标注「单位以原报表为准，未明确」，不得臆断元/万元、份/万份。
- 融资类为金额、融券类为数量（余量），两组口径不同，不得混加或对比。
- `negotiablemvoffinance` / `negotiablemvofsecurity` 为占比口径，已是原报表数值，不再乘 100。
- 日期按 `tradingday` 原样读取，不补造日期或推定排序。跨标的分析须对齐交易日期和原报表口径，不外推预测。

## 7. 空数据与异常值语义

- 上游成功无记录：`records=[]`、`recordCount=0`，如实说明无数据，不补造。
- 缺失字段或源空值展示「—」，不当作 0，不自行推算。
- 非法 `innerCode` 返回 HTTP 400 `PARAM_INVALID`；`beginDate`/`endDate` 非 `yyyy-MM-dd`、`indexCycle` 不在 1~5、`unit` 不在 1~7 同样返回 400 `PARAM_INVALID`（不静默回退默认值）；上游失败沿服务端错误链返回失败，**不允许伪造成功记录或成功空数组**。
- 404 `API_NOT_FOUND` 表示未放行或不存在，如实告知，不借其他接口拼凑替代。

## 8. 前置条件与调用限制

需有效授权、已配置 API Key（`config.py status` 为 configured）、内网网关可达，遵循本 Skill 的凭证与限流规则，调用间隔建议 ≥3 秒。源包纳入不等于接口已上线，仍受服务端注册状态与当前 Key 的 scope 控制。

## 9. 相关工作流

见 `references/workflows/fund-code-resolution.md` 及 `references/apis/fund-resolve.md`。本接口目标字段是 `innerCode`，不要固定取 `secuCode` 或手工拼后缀。降级/演示解析结果不得作真实续调依据。

## 10. 验证与交付边界

权威契约见仓库 `docs/htbr-ai-skill/02-接口契约.md`（接口登记：附录 B.2 50 池 #24 行 + 本文件）。验收包括数值/数字字符串内码、非法入参、可选参数（`beginDate`/`endDate`/`indexCycle`/`unit`）缺省不下推与越界 400、固定上游参数、16 字段（含融资/融券口径区分、占比字段不乘 100）、无记录及上游失败不伪造、不换算单位，以及解析后续调。源包文档检查不等于真实接口联调、注册放行或发布成功；交付镜像仅允许经 `sync_kit.py` 同步，缺失时不得手工复制。
