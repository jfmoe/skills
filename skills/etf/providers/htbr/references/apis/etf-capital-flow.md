# etf-capital-flow

| 项 | 值 |
|---|---|
| `api_id` | `etf-capital-flow` |
| 服务端登记名 | 场内基金资金流向 |
| 领域 | etf（场内基金） |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回**单只场内基金**的逐日资金流向：总流入 / 总流出 / 净流入，以及超大单、大单、中单、小单四档净买入额。

适用：用户问「510300 最近主力资金是流入还是流出」「大单买了多少」「散户在跑吗」。

## 2. 不适用场景与易混接口

- **与 `etf-capital-flow-stats` 的区别**：那个是**市场整体**资金流统计（跨基金汇总）；本接口是**单只基金**逐日明细。
- 与 `fund-daily-quote` 的区别：那个是行情（价格/成交），本接口是**资金分档**。
- 不提供分钟级 / 逐笔资金数据。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundCode` | string | **是** | 带市场后缀的 GilCode，**一律用 `.OF`**（含场内 ETF，如 `510300.OF`）；无法解析 → 404；非 ETF 且非场内基金 → 200 `NO_DATA` |
| `beginDate` | string | **是** | 起始日，格式 **`yyyyMMdd`**；缺失 → 400 |
| `endDate` | string | **是** | 截止日，格式 **`yyyyMMdd`**；缺失 → 400；`begin > end` → 200 `NO_DATA` |

> ⚠ **日期格式是 `yyyyMMdd`**，与其它接口的 `yyyy-MM-dd` **不同**，不要套用。

## 4. 调用示例

```bash
pixi run etf-htbr invoke etf-capital-flow '{"fundCode":"510300.OF","beginDate":"yyyyMMdd","endDate":"yyyyMMdd"}'
```

> ⚠ 后缀统一 `.OF`（场内 ETF 也是 `.OF`）；传 `.SH` / `.SZ` 解析不到 → 404 `FUND_NOT_FOUND`。

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `fundCode` / `beginDate` / `endDate` | 请求回显 |
| `recordCount` | 行数（= **有资金流的交易日数**） |
| `records[]` | 按 `tradingDay` **降序** |
| `records[].fundObject` | 内码 |
| `records[].fundCode` / `.fundName` | 基金代码 / 简称 |
| `records[].tradingDay` | 交易日（`yyyyMMdd`） |
| `records[].totalBuyValue` | 总流入额（**万元**，2 位小数） |
| `records[].totalSellValue` | 总流出额（**万元**） |
| `records[].totalValue` | **净流入总额**（万元）= 总流入 − 总流出 |
| `records[].hugeNetBuyValue` | 超大单净买入额（万元） |
| `records[].largeNetBuyValue` | 大单净买入额（万元） |
| `records[].mediumNetBuyValue` | 中单净买入额（万元） |
| `records[].smallNetBuyValue` | 小单净买入额（万元） |

## 6. 数据口径

- ⚠ **`totalValue` 是净额，不是"总成交额"**。该字段名沿用上游的历史命名歧义，回答时按「净流入」表述。
- 全部金额单位为**万元**，保留 2 位小数，展示不要再换算。
- 只输出**有资金流记录的交易日**（周末/节假日自然缺行），**不要**据此判断"数据缺失"。
- 某档当日无记录时输出 **`0.0`**，无法区分"真实为 0"与"无该档数据"；如用户追问，如实说明该局限。
- 四档对应关系：超大单 / 大单 / 中单 / 小单。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 404 `FUND_NOT_FOUND` | 基金代码无法解析 |
| 400 `PARAM_INVALID` | 缺 `beginDate` / `endDate`，或日期格式不是 `yyyyMMdd` |
| 200 + `NO_DATA` | 非 ETF / 非场内基金（被资格判定跳过），或 `begin > end`（空序列） |
| 区间内无任何资金流 | 200 + `NO_DATA`，如实说明该区间无数据 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- 仅支持**场内基金**（ETF 或有场内份额的基金）；场外基金查不到。

## 9. 相关工作流

无。
