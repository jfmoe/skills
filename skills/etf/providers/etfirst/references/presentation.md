# 日期、单位与展示

## 时间来源

- 实时行情（涨跌幅、最新价、成交额、溢折率、指数点位）：取 `index-detail all` 或 `etf-detail all` 的 `getRealTimeData.tradingDay`（`yyyyMMdd`）与 `time`（`HHmmssSSS`），合成 `YYYY-MM-DD HH:mm:ss`。指数点位也可取 `queryIndexDetail.pointValueUpdateTime`。
- 只查询了 `list-etf` 却要展示实时行情时，补充对应产品的详情聚合以获取时间戳；列表的 `dataDate`、`yieldDate` 不能替代。时间戳缺失时明确说明，不能声称已核实为当日实时行情。
- 日频指标使用各自的日期字段；持仓、行业、规模变化等低频指标使用各自截止日期。不同指标可能来自不同日期。
- 行情在交易时段约每 5 秒刷新，非交易时段保留上次值；日频数据收盘后可能延迟，季度指标按披露周期更新。按返回日期说明时效，不从日期反推交易日历。

回复末尾添加“日期标注：”段落，使用业务名称逐项标注；同日期、同频率的指标可合并：

```text
日期标注：
- 最新价、涨跌幅：2026-06-15 15:00:03 实时行情
- 市盈率：数据日期 2026-06-12（日频）
- 持仓：数据截止 2026-03-31
```

## 单位

以具体接口字段定义为准，不能把所有金额统一视为元。列表的规模、净流入通常为亿元，成交额为元；持仓市值为元，指数档案市值为亿元。指数 `etf` 净流入单位存在上游文档冲突，见[指数详情](index.md)的 `queryNetInflow`。

百分比字段已乘以 100，例如 `yield=0.85` 表示 `+0.85%`，保持正负号。PE/PB 为倍数；ROE、股息率为百分比；FED 按其字段定义解释。夏普比率无量纲。具体排名可能是名次、档位或百分位，查对应字段表，不把所有排名都当百分比。

价格通常为元/份，行情成交量为手，持仓数量为股，基金份额为份。不同字段的单位不可互换。字符串数值中的空值或 `—` 保持缺失语义。

## 数值核验

已安装 CLI 0.4.2 对聚合 `results` 基本透传，没有统一价格或成交量缩放。样本中 `getRealTimeData.closePrice` 返回 ETF `510300` 为 `44320`，指数 `000922` 为 `54933409`，但同次指数综合详情的点位为 `5493.34`；原始数值不能直接按上游表的元/份或点输出。不得仅凭数量级自行除以 10000，也不能将所有行情字段使用同一缩放。

实测同只 510300 的列表 `price=4.4320` 与华宝同日收盘价 `4.432` 相符，详情原始 `closePrice=44320`。最新价格、成交额可优先读取列表中有定义的 `price`／`traval`，按既有规则补查同一产品的行情时间；说明抓取时刻差异，不能认定两次请求完全同步。成交量或 IOPV 若只有原始字段，先取得具体缩放依据。证据不足就报告该字段单位未核实，避免输出错误价格；日期字段的有效性不代表数值已标准化。只有确认原始单位后才做换算。

## 业务名称

**API 字段名 → 业务术语映射（Agent 向用户返回数据时必须使用业务术语，禁止使用 API 字段名）**：

| API 字段名 | 业务术语（用户可见） |
|---|---|
| `yield` | 涨跌幅 |
| `price` | 最新价 |
| `traval` | 成交额 |
| `premDisRto` | 溢折率 |
| `pe` / `pePercent` | 市盈率 / PE 分位 |
| `pb` / `pbPercent` | 市净率 / PB 分位 |
| `dp` | 股息率 |
| `roe` | 净资产收益率（ROE） |
| `ast` | 规模（保有规模 / AUM） |
| `netInflow` | 净流入 |
| `pointValue` | 指数点位 |
| `volatility` | 波动率 |
| `trackError` | 跟踪误差 |
| `mgrFee` / `trustFee` / `saleFee` | 管理费率 / 托管费率 / 销售服务费率 |
| `standardDeviation` | 波动率（风险特征版） |
| `sharpeRatio` | 夏普比率 |
| `maxDrawdown` | 最大回撤 |

## 日期字段索引

| 日期字段 | 所在接口 / 位置 | 说明 |
|---|---|---|
| `dataDate` | `index-base list-etf` 的 `dataList` 元素；`etf-detail all` 的 `getMarketIndicatorData` | 日频记录日期；不作为实时行情时间 |
| `yieldDate` | `index-base list-etf` 的 `dataList` 元素；`etf-detail all` 的 `getMarketIndicatorData` | 收益率日期；不作为实时行情时间 |
| `peDate` | `index-base list-etf` 的 `dataList` 元素；`etf-detail all` 的 `getMarketIndicatorData` | PE 数据日期 |
| `roeDate` | `index-base list-etf` 的 `dataList` 元素；`etf-detail all` 的 `getMarketIndicatorData` | ROE 数据日期（通常为上季度末，如 `"20260331"`） |
| `astDate` | `index-base list-etf` 的 `dataList` 元素；`etf-detail all` 的 `getMarketIndicatorData` | 规模（AUM）数据日期 |
| `tradingDay` / `tradingday` | 各子接口（注意：部分接口返回小写 `tradingday`，部分返回大写 `tradingDay`） | 交易日。`queryRiskReturnRatio` / `queryChangeRateByIndexCode` / `queryCompanyWeight` 用小写 `tradingday`；`queryNetInflow` / `getRealTimeData` 等用大写 `tradingDay` |
| `endDate` | `index-detail` 的 `queryIndustryDistribution`；`etf-detail` 的 `getRiskReturnCharacter` / `getHoldStock` / `getIndustryDistribution`；`otc-detail` 的 `linkFundHold` | 数据截止日 |
| `pointValueUpdateTime` | `index-detail all` 的 `queryIndexDetail` | 实时点位最后刷新时间，格式 `yyyy-MM-dd HH:mm:ss`。**注意：该字段可能仅在交易时段返回，非交易时段可能缺失** |
| `scaleDate` | `etf-detail all` 的 `getEtfLinkInfo` | ETF 联接基金规模数据日期 |
| `tradeDate` | `etf-detail all` 的 `getReturnTrendList`；`otc-detail all` 的 `getReturnTrendList` | 收益走势序列中的交易日 |
| `date` | `otc-detail all` 的 `scaleChange` | 规模变化数据日期 |
| `END_DATE` | `etf-detail all` / `otc-detail all` 的 `getProductWindRank` | Wind 排名数据截止日（大写命名） |
