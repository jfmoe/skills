# etf-capital-report

| 项 | 值 |
|---|---|
| `api_id` | `etf-capital-report` |
| 服务端登记名 | ETF资金 |
| 领域 | etf |
| 资料完整度 | 完整（请求、响应、口径；上线与真实上游另验） |

## 1. 功能与适用场景

查询单只 ETF 资金报表：净值、收盘价、场内份额、净申购份额、融资净买入额及余额、近3/5/20/60日融资净买入、最新规模（单位净值×场内份额）。用户问「这只 ETF 资金情况」「融资净买入和余额」「近几日融资净买入」「最新规模」时使用。溢价率不在本接口输出，问折溢价改走 `fund-daily-quote`。

业务入口为 `POST /api/v1/business/etfFundCapitalReport`（兼容壳，内部转调统一链路）；Skill 使用统一入口 `POST /api/v1/business/etf-capital-report:invoke`。

## 2. 不适用场景与易混接口

- 不提供场内资金流向（`etf-capital-flow`）或市场整体资金流向统计（`etf-capital-flow-stats`），不能用本报表替代。
- 不提供实时行情；区间由 `beginDate`/`endDate` 表达，不做全量历史分页；不要按接口名猜测参数。
- 近N日融资净买入不是净申购，也不是全部交易资金净流入。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `innerCode` | number 或数字字符串 | 是 | 正整数基金内码；零、负数、小数、布尔值、数组、对象、空值均不合法 |
| `beginDate` | string | 否 | 开始日期 `yyyy-MM-dd`；空 = 上游缺省（`endDate` 前推 **6 个月**）；格式不符 400 |
| `endDate` | string | 否 | 截止日期 `yyyy-MM-dd`；空 = 上游缺省当日；格式不符 400 |
| `unit` | number | 否 | 金额单位，取值 **1~7**（含义见下方速查表）；空 = 上游缺省 **3（万元）**；越界或非整数 400 |

**枚举取值速查**（唯一权威，构造请求前按此选值，不要猜）：

| 参数 | 值 → 含义 | 不传时 |
|---|---|---|
| `unit` | `1`=元 · `2`=千 · `3`=万 · `4`=百万 · `5`=千万 · `6`=亿 · `7`=十亿 | `3`（万元） |

`innerCode` 以外的三个参数均为**可选**，缺省时不向下游传（沿用上游默认语义），不传时行为与只有 `innerCode` 的老调用完全一致。不传 `fundCode`（基金代码走 `innerCode` 解析），也不接受分页参数。

只有基金名称、证券代码或 GilCode 时，先按基金解析工作流调用 `fund-resolve`，唯一命中后取 `candidates[0].innerCode`；多候选等待用户确认，零候选核对输入。不得把证券代码直接当内码。

## 4. 调用示例

以下内码仅展示格式，实际必须用已确认的基金内码替换：

```bash
pixi run etf-htbr invoke etf-capital-report '{"innerCode":"12345","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd","unit":3}'
```

`beginDate`/`endDate` 是日期**占位**，实际调用须替换为具体日期（格式 `yyyy-MM-dd`），原样传 `yyyy-MM-dd` 会 400。示例里 `unit:3`（万元）的取值含义见 §3 速查表。

数字形式 `{"innerCode":12345}` 也可接受。`<SKILL_DIR>` 必须替换为本技能实际目录，使用本包自己的客户端。

## 5. 返回数据路径与关键字段

读 `$.data`：`innerCode` 为整数基金内码，`recordCount` 为本次记录条数，`records[]` 为记录数组。每条记录行字段与 DS 报表列名逐字一致（全小写），共 16 字段：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundobject` | integer | 基金内码 |
| `fundcode` | string | 基金代码，保留前导零 |
| `fundname` | string | 基金简称 |
| `chiname` | string | 基金全称 |
| `tradingday` | string | 交易日期 |
| `unitnv` | number | 单位净值（元/份） |
| `closepricelist` | number | 收盘价（元/份） |
| `exchangeshares` | number | 场内份额（万份） |
| `marketscale` | number | 最新规模（万元） |
| `netsubscriptionshares` | number | 净申购份额（份） |
| `financenetbuyvalue` | number | 融资净买入额（万元） |
| `financebalancevalue` | number | 融资余额（万元） |
| `near3daynetbuy` | number | 近3日融资净买入（万元） |
| `near5daynetbuy` | number | 近5日融资净买入（万元） |
| `near20daynetbuy` | number | 近20日融资净买入（万元） |
| `near60daynetbuy` | number | 近60日融资净买入（万元） |

## 6. 数据口径

- 上游为 dataservice 报表 `RAGAPI.ETFFundCapitalReport`，固定 `JSON2`、`Compress=false`，不传分页参数；`FundObject=[innerCode字符串]` 由服务端转换，`BeginDate`/`EndDate`/`Unit` 由客户端可选传入（缺省不下推，取上游默认：截止日=当日、开始日=截止日前推 6 个月、单位=3 万元）。这些固定项不是客户端入参；返回条数以线上实际为准。
- 缺少日期参数时上游默认窗口仅 6 个月（本接口业务口径），要更早的交易日必须显式传 `beginDate`；「近N日融资净买入」是上游按交易日回溯算好的列，不受 `beginDate` 影响。
- 保留原报表单位和数值，**不得换算单位**；不得臆断金额为元/万元、份额为份/万份。单位未明确时如实标注「单位以原报表为准，未明确」。
- 上游报表的溢价率列**不再下发**（`premiumrate` 已从返回中移除），问折溢价请改走场内基金日行情接口（`fund-daily-quote` 的折溢价率字段）；近N日字段均为融资净买入。
- `marketscale` 为服务端派生字段（`unitnv` × `exchangeshares`），任一因子为空时该字段为 null，按缺失口径展示「—」，不得自行补算或换算单位。
- 日期按 `tradingday` 原样读取，不补造日期或推定排序；取「最新」一条必须显式比较 `tradingday` 取最大（如 `max(records, key=lambda r: r["tradingday"])`），禁止按数组位置（`records[-1]` / `records[0]`）取值——实测 `records` 为倒序（最新在前），`records[-1]` 会拿到窗口最早一条。跨标的分析须对齐交易日期和原报表口径，不外推预测。

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

权威契约见仓库 `docs/htbr-ai-skill/02-接口契约.md`（接口登记：附录 B.2 50 池 #28 行 + 本文件）。验收包括数值/数字字符串内码、非法入参、可选参数（`beginDate`/`endDate`/`unit`）缺省不下推与越界 400、固定上游参数、16 字段（含 `marketscale` 派生值及空值口径）、无记录及上游失败不伪造、不换算单位，以及解析后续调。源包文档检查不等于真实接口联调、注册放行或发布成功；交付镜像仅允许经 `sync_kit.py` 同步，缺失时不得手工复制。
