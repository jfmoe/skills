# fund-drawdown

| 项 | 值 |
|---|---|
| `api_id` | `fund-drawdown` |
| 服务端登记名 | 基金动态回撤 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回基金在给定区间内的**逐日回撤序列**：每日复权净值相对区间内历史峰值的回撤幅度（**小数**，≤ 0）。

适用：用户问「这只基金这一年的回撤怎么走的」「哪段时间回撤最深」「画个回撤曲线」。

## 2. 不适用场景与易混接口

- ⚠ **与 `fund-max-dd` 的区别**：`fund-max-dd` 给的是**多周期静态指标**（近 1/3/5 年各一个数）；
  本接口给的是**逐日序列**。问「最大回撤多少」用 `fund-max-dd`；问「回撤怎么走的 / 哪段最深」用本接口。
- 同一基金同一区间下，本接口序列的最小值 **×100 ≈ `fund-max-dd` 的最大回撤（%）**（允许 ±0.01pp 口径差）。
- 不返回「截至当日的累计最大回撤」（DS `mmValue`）：需要时对序列做前缀最小值即可自行计算。
- 不提供指数 / ETF 的动态回撤；不做区间聚合统计。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundCode` | string | 是 | 聚源代码，**带后缀**（如 `000021.OF`），与 `fund-max-dd` 同口径 |
| `beginDate` | string | 否 | `YYYY-MM-DD`；区间**唯一起点**（起始日**前推一日**后纳入，DS getPreNDay 语义，故返回序列可能比 beginDate 早一个交易日）；空 = 按截止日全量回溯 |
| `endDate` | string | 否 | `YYYY-MM-DD`；空 = 最新交易日 |

> 参数面只有这三个。「近一年 / 近三月 / 今年」这类快捷区间**不在接口内**，需先换算成显式的
> `beginDate`/`endDate` 再调用。

## 4. 调用示例

```bash
# 显式区间
pixi run etf-htbr invoke fund-drawdown '{"fundCode":"000021.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 近一年：自行算出起止日（截止日按 yyyy-MM-dd 传）
pixi run etf-htbr invoke fund-drawdown '{"fundCode":"000021.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `fundCode` | 原样返回 |
| `recordCount` | 序列点数 |
| `records[]` | 逐日序列，按 `date` **升序** |
| `records[].indexCode` | 基金内码（整数） |
| `records[].indexName` | 基金简称 |
| `records[].date` | 交易日 `YYYY-MM-DD` |
| `records[].value` | 当日动态回撤，**小数，≤ 0**（`-0.0132` 即 −1.32%） |

## 6. 数据口径

- 回撤为**前缀峰值法**：当日净值创区间新高时 `value = 0`，之后按相对峰值的跌幅计算。
  **首行若为区间新高则必为 `0`**，这是正确行为。
- ⚠ `value` 是**小数不是百分数**：展示时 ×100 再加 `%`（`-0.0132` → `-1.32%`），
  **不要**直接加 `%`（那会读成 −0.0132%）。
- 截止日 = 不晚于 `endDate` 的**最大交易日**；`endDate` 为空取最新。
- 起始日 = `beginDate` **前推一日**，序列首行可能比 `beginDate` 早一个交易日（该日有净值时）。
- 逐日点数可能上千（5 年约 1210 点），**服务端不做截断**，展示时自行裁剪。
- 「截至当日的累计最大回撤」需要时对序列前缀取最小值（同样 ×100 后展示）。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 404 `FUND_NOT_FOUND` | 基金代码无法解析：如实告知，不要用近似代码替代 |
| 200 + `NO_DATA` 注记 | 区间内无行情：正常语义，如实说明该区间无数据 |
| 400 `PARAM_INVALID` | 参数非法（如日期不是 `YYYY-MM-DD`）：核对参数后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `fundCode` 必须带 `.OF` 后缀，与 `fund-max-dd` 等收益风险接口同口径。

## 9. 相关工作流

- `references/workflows/return-risk-indicators.md`（同族指标的后缀与日期口径）
