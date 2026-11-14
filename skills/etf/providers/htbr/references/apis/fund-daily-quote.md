# fund-daily-quote

| 项 | 值 |
|---|---|
| `api_id` | `fund-daily-quote` |
| 服务端登记名 | 基金盘中行情 |
| 领域 | fund |
| 资料完整度 | 完整（请求、响应、口径；上线与真实上游另验） |

## 1. 功能与适用场景

查询单只场内基金（ETF/LOF）的逐日行情：前收盘/开/高/低/收盘价、均价、涨跌额与涨跌幅、振幅、成交额、成交量、换手率、贴水率、折溢价率、是否停牌、交易日。默认返回最近 1 年逐日（可传 `beginDate`/`endDate` 收窄到单日或指定区间）。用户问「这只基金今天收盘多少」「涨跌多少」「成交额多大」「停牌了吗」「折溢价多少」时使用。

业务入口为 `POST /api/v1/business/fundIntradayDailyQuote`（兼容壳，内部转调统一链路）；Skill 使用统一入口 `POST /api/v1/business/fund-daily-quote:invoke`。

## 2. 不适用场景与易混接口

- 与 `fund-nav` 的边界：本接口是**场内交易行情**（二级市场撮合价），`fund-nav` 是**基金净值**（申赎口径）。问「净值」不得用本接口，问「市价/收盘价」不得用 `fund-nav`；两者数值不同、来源不同。
- 不提供盘中 tick/分时数据；区间由 `beginDate`/`endDate` 表达，不做全量历史分页（上游无分页入参）；不要按接口名猜测参数。
- 与 etf 系报表（`etf-capital-report` / `etf-margin` 等）入参口径不同：本接口直接传 `secuCode`，**无需先 resolve 取内码**。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `secuCode` | string | 是 | 6 位场内基金代码（保留前导零）；空值、空白、非字符串数字（如 `12345`）不合法 |
| `beginDate` | string | 否 | 起始交易日 `yyyy-MM-dd`；空 = 上游缺省（`endDate` 前推 1 年）；格式不符 400 |
| `endDate` | string | 否 | 结束交易日 `yyyy-MM-dd`；空 = 上游缺省当日；格式不符 400 |
| `adjustingMethod` | number | 否 | 复权方式，取值 **2 或 3**（含义见下方速查表）；空 = 上游缺省 **3（不复权）**；传 1 或其它值 400 |

**枚举取值速查**（唯一权威，构造请求前按此选值，不要猜）：

| 参数 | 值 → 含义 | 不传时 |
|---|---|---|
| `adjustingMethod` | `2`=后复权 · `3`=不复权（`1` 前复权**不支持**，传了 400） | `3`（不复权） |

`secuCode` 以外的三个参数均为**可选**，缺省时不向下游传（沿用上游默认语义），不传时行为与只有 `secuCode` 的老调用完全一致。

**要单日快照必须自己收窄区间**：不传日期时上游默认返回**最近 1 年逐日**行情，`quotes[]` 会有多行；问「今天收盘多少」应把 `beginDate` 与 `endDate` 传为同一个日期（格式 `yyyy-MM-dd`），或取 `quotes[]` 中 `tradingday` 最大的一行并说明口径。

用户给的是基金名称或 GilCode 时，先按基金解析工作流调用 `fund-resolve`，唯一命中后取场内 `secuCode`；多候选等待用户确认，零候选核对输入。不得把 `.OF` 场外代码当 `secuCode` 传入。

## 4. 调用示例

以下代码仅展示格式，实际必须用已确认的场内代码替换：

```bash
pixi run etf-htbr invoke fund-daily-quote '{"secuCode":"159915"}'
pixi run etf-htbr invoke fund-daily-quote '{"secuCode":"159915","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd","adjustingMethod":3}'
```

`beginDate`/`endDate` 是日期**占位**，实际调用须替换为具体日期（格式 `yyyy-MM-dd`），原样传 `yyyy-MM-dd` 会 400。示例里 `adjustingMethod:3`（不复权）的取值含义见 §3 速查表。

`<SKILL_DIR>` 必须替换为本技能实际目录，使用本包自己的客户端。

## 5. 返回数据路径与关键字段

读 `$.data.quotes[]`（统一入口应答容器为 `quotes`；兼容路径返回裸列表，字段一致）。每条记录行字段与 DS 报表列名逐字一致（全小写），**全部为 string 类型**（原报表为字符列，原样返回，不转数字），共 19 字段：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundobject` | string | 基金内码 |
| `fundcode` | string | 基金代码，保留前导零 |
| `fundname` | string | 基金简称 |
| `tradingday` | string | 交易日期 |
| `ifsuspend` | string | 是否停牌 |
| `prevcloseprice` | string | 前收盘价（元） |
| `openprice` | string | 今开盘价（元） |
| `highprice` | string | 最高价（元） |
| `lowprice` | string | 最低价（元） |
| `closeprice` | string | 收盘价（元） |
| `avgprice` | string | 均价（元） |
| `changeofprice` | string | 涨跌额（元） |
| `changepct` | string | 涨跌幅（%） |
| `rangepct` | string | 振幅（%） |
| `turnovervalue` | string | 成交额（万元） |
| `turnovervolume` | string | 成交量（亿股） |
| `turnoverrate` | string | 换手率（%） |
| `discountratio` | string | 贴水率（%） |
| `premiumrate` | string | 折溢价率（%） |

## 6. 数据口径

- 上游为 dataservice 报表 `RAGAPI.FundsPerformanceHis`，`FundObject=[内码]`（由 `secuCode` 经 `fund-resolve` 解析后服务端转换）、`BeginDate`/`EndDate`/`AdjustingMethod` 由客户端可选传入（缺省不下推，取上游默认：结束日=当日、起始日=结束日前推 1 年、复权=3 不复权）；不传分页参数，不承诺任意区间或全量历史。
- 所有字段为字符串原样返回：**不得换算单位**（元/万元、股/亿股以字段含义标注为准），不得改写小写命名；展示数值时按需呈现，不臆断精度。
- `changepct` / `rangepct` / `turnoverrate` / `discountratio` / `premiumrate` 为百分比口径原报表数值，不再乘 100。
- 与 `fund-nav` 口径不同源（**场内交易行情 vs 基金净值**），同日数值不可互推、不可混排对比。
- 日期按 `tradingday` 原样读取，不补造日期或推定排序。

## 7. 空数据与异常值语义

- 上游成功无记录：`quotes=[]` 带 `NO_DATA` 注记，如实说明无数据，不补造。
- 上游取数失败（含 secuCode→内码解析链路故障）：服务端返回 **503 `DEGRADED`**（`error.detail` 带 apiId 与 reason），不再返回任何示例数据——此时**必须如实告知该接口暂不可用**，不得用旧数据或估算值代替作答。
- `secuCode` 无法映射到基金内码（零命中）：返回 HTTP 404 `FUND_NOT_FOUND`（detail 回填 `secuCode`），如实告知未找到该基金、请核对代码，不借其他接口拼凑替代。
- 同一 `secuCode` 映射到多个内码：返回 HTTP 409 `FUND_AMBIGUOUS`（detail 附 `innerCodes`），如实转告并等待用户澄清。
- 缺失字段或源空值展示「—」，不当作 0，不自行推算。
- `secuCode` 缺失或空白返回 HTTP 400 `PARAM_INVALID`；`beginDate`/`endDate` 非 `yyyy-MM-dd`、`adjustingMethod` 不是 2 或 3 同样返回 400 `PARAM_INVALID`（不静默回退默认值）；404 `API_NOT_FOUND` 表示未放行或不存在，如实告知，不借其他接口拼凑替代。

## 8. 前置条件与调用限制

需有效授权、已配置 API Key（`config.py status` 为 configured）、内网网关可达，遵循本 Skill 的凭证与限流规则，调用间隔建议 ≥3 秒。源包纳入不等于接口已上线，仍受服务端注册状态与当前 Key 的 scope 控制。

## 9. 相关工作流

见 `references/workflows/fund-code-resolution.md`（仅当用户给名称/GilCode 时需要先解析；直接给 6 位场内代码时无需解析）。降级/演示解析结果不得作真实续调依据。

## 10. 验证与交付边界

权威契约见仓库 `docs/htbr-ai-skill/02-接口契约.md`（接口登记：服务端 `08-fund-daily-quote-registry.sql`）。验收包括：`secuCode` 入参（含前导零）、非法入参、可选参数（`beginDate`/`endDate`/`adjustingMethod`）缺省不下推与越界 400、19 字段全小写字符串口径、上游失败时如实告知 503 而不编造数据、空记录不补造、不换算单位、不与 `fund-nav` 混源对比。源包文档完成不等于真实接口联调、注册放行或发布成功；交付镜像仅允许经 `sync_kit.py` 同步，缺失时不得手工复制。
