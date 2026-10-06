# 分类与产品列表

普通响应为 `{code, message, data}`；列表的 `data` 包含 `totalRows` 与 `dataList`。

## `index-base` 命令选项

> 以下选项为 `index-base clas` 与 `index-base list-etf` 共用。使用 `clas` 时显式指定 `--type`（CLI 自身未设 required）；分页/排序选项主要对 `list-etf` 有意义。

| CLI 选项 | 说明 |
|---|---|
| `--type` | 产品类型枚举：`1`=指数；`2`=ETF；`3`=场外基金 |
| `--clas` | 指数分类代码（通过 `clas` 命令获取的 `code` 值） |
| `--key-word` | 按产品代码或名称做模糊匹配 |
| `--index-code` | 精确按指数代码筛选 |
| `--sort-key` | 排序字段名（取 `dataList` 元素中的数值字段名，如 `yield`、`netInflow`、`ast`） |
| `--sort-direction` | 排序方向：`asc`=升序；`desc`=降序 |
| `--page-no` | 页码（从 1 起），默认 `1` |
| `--page-size` | 每页条数，默认 `10` |

### 1. index-base clas — 指数分类字典

按 `--type` 返回该类型下的分类树（最多 3 级嵌套）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | String | 分类代码。可作为 `list-etf --clas` 的入参 |
| `name` | String | 分类中文名称，例如「跨境指数」「行业指数」 |
| `count` | Integer | 该分类（含子分类）下的产品数量 |
| `childList` | List | 子分类列表，结构同本表；无子分类时为 `null` |

---

### 2. index-base list-etf — 指数 / ETF / 场外列表

**顶层返回**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `totalRows` | Integer | 满足筛选条件的总记录数；用于前端计算总页数 |
| `dataList` | List | 当前页的产品列表，长度 ≤ `--page-size` |

## 分页与公司筛选

`--page-no` 从 1 开始，每次加 1；累计实际 `dataList` 条数，直到达到 `totalRows`。服务端可能少于请求的 `--page-size`，不能用页码乘页大小判断完整性。若未达总数却返回空页或重复页，报告结果不完整，停止无进展的翻页。

`--key-word` 仅匹配产品名称或代码。按管理人筛选时，先取得目标范围的完整列表，再按 `managementCompany` 精确或包含匹配；说明匹配口径。

```bash
etfirst --json index-base clas --type 2
etfirst --json index-base list-etf --type 2 --index-code 000300 --page-no 1 --page-size 100
```

`--clas` 使用分类字典返回的 `code`。跟踪同一指数的场外联接产品使用 `--type 3`。

**`dataList` 元素字段**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `prodCd` | String | 产品代码（一般 6 位），例 `"510300"` |
| `prodName` | String | 产品简称，例 `"沪深300ETF"` |
| `prodFullName` | String | 产品全称 |
| `indexCd` | String | 跟踪/对应指数代码，例 `"000300"` |
| `indexName` | String | 指数简称 |
| `clasCd` / `clasName` | String | 一级分类代码 / 中文名，与 `clas` 命令的 `code`/`name` 一致 |
| `level2ClasCd` / `level2ClasName` | String | 二级分类代码 / 中文名 |
| `level3ClasCd` / `level3ClasName` | String | 三级分类代码 / 中文名 |
| `yield` | BigDecimal | 涨跌幅，单位 `%`。正数=上涨，负数=下跌。例 `0.85` = +0.85%。为当日实时数据（5 秒刷新）； |
| `netInflow` | BigDecimal | 最新交易日净流入，单位 `亿元`。正=净流入，负=净流出 |
| `l1wNetInflow` | BigDecimal | 最新交易日起向前推 1 周（自然周）累计净流入，单位 `亿元` |
| `l1mNetInflow` | BigDecimal | 最新交易日起向前推 1 个自然月累计净流入，单位 `亿元` |
| `l3mNetInflow` | BigDecimal | 最新交易日起向前推 3 个自然月累计净流入，单位 `亿元` |
| `l1yNetInflow` | BigDecimal | 最新交易日起向前推 12 个自然月累计净流入，单位 `亿元` |
| `ytdNetInflow` | BigDecimal | 本年 1 月 1 日至最新交易日累计净流入，单位 `亿元` |
| `ast` | BigDecimal | 追踪同一指数的 ETF 合计保有规模（AUM），日频更新，单位 `亿元` |
| `pe` | BigDecimal | 最新交易日市盈率（PE-TTM），单位：倍 |
| `pePercent` | BigDecimal | PE 历史分位（从 2016-01-04 起），单位 `%`（0~100，越低代表估值越低） |
| `pb` | BigDecimal | 最新交易日市净率，单位：倍 |
| `pbPercent` | BigDecimal | PB 历史分位（从 2016-01-04 起），单位 `%`（0~100） |
| `dp` | BigDecimal | 股息率，单位 `%`（年化） |
| `roe` | BigDecimal | 净资产收益率 ROE，单位 `%` |
| `volatility` | BigDecimal | 波动率，单位 `%`（年化） |
| `premDisRto` | BigDecimal | 溢折率，单位 `%`。正=溢价，负=折价（仅 ETF 字段，`--type 2` 时返回） |
| `traval` | BigDecimal | 成交额，单位 `元`（仅 ETF 字段，`--type 2` 时返回）。为当日累计实时成交额（5 秒刷新）。|
| `price` | String | 最新价，单位 `元/份`（仅 ETF 字段，`--type 2` 时返回）。为当前实时成交价（5 秒刷新）。 |
| `trackError` | BigDecimal | 近 12 个自然月跟踪误差，单位 `%`（越小代表跟踪越紧） |
| `mgrFee` | BigDecimal | 管理费率，单位 `%`（年化） |
| `trustFee` | BigDecimal | 托管费率，单位 `%`（年化） |
| `saleFee` | BigDecimal | 销售服务费率，单位 `%`（年化） |
| `managementCompany` | String | 基金管理公司全称 |
| `isSouthETF` | Integer | 是否南方基金产品：`1`=是，`0`=否 |
| `fundManager` | String | 基金经理姓名；多人时以「、」分隔 |
| `standardDeviation` | String | 波动率（风险特征版），单位 `%`（年化） |
| `sharpeRatio` | String | 夏普比率（无量纲） |
| `maxDrawdown` | String | 最大回撤，单位 `%`（一般为负数） |
| `riskReturnDate` | String | 风险特征数据日期 `yyyyMMdd` |
| `peDate` | String | 估值日期（PE/PB/股息率等指标对应的交易日），格式 `yyyyMMdd` |
| `valuation` | String | 估值标准（如"PE-TTM"） |
| `roeDate` | String | ROE 数据日期 `yyyyMMdd` |
| `astDate` | String | ETF 规模数据日期 `yyyyMMdd` |
| `astChgRto` | BigDecimal | 规模变化率，单位 `%` |
| `otcAstDate` | String | 场外规模数据日期 `yyyyMMdd` |
| `etfLinkAst` | BigDecimal | 场外联接基金规模，单位 `亿元` |
| `dataDate` | String | 数据日期/净流入日期 `yyyyMMdd` |
| `establishDate` | String | 产品成立日期 `yyyyMMdd` |
| `yieldDate` | String | 收益率日期 `yyyyMMdd` |
| `l1dYield` | BigDecimal | 上一日涨幅，单位 `%` |
| `l1wYield` | BigDecimal | 周度涨幅，单位 `%` |
| `l1mYield` | BigDecimal | 月度涨幅，单位 `%` |
| `l3mYield` | BigDecimal | 近 3 月涨幅，单位 `%` |
| `l6mYield` | BigDecimal | 近半年涨幅，单位 `%` |
| `l1yYield` | BigDecimal | 年度涨幅，单位 `%` |
| `ytdYield` | BigDecimal | 今年以来涨幅，单位 `%` |
| `inceptionYield` | BigDecimal | 成立以来涨幅，单位 `%` |
| `nav` | BigDecimal | 基金净值，单位 `元/份` |
| `cumulativeNav` | BigDecimal | 累计净值，单位 `元/份` |
| `closePrice` | String | 上一日收盘点位/价格 |
| `nowPrice` | String | 最新价（实时），单位 `元/份` |
| `percentageChange` | String | 涨跌幅，单位 `%` |
| `compositeFee` | BigDecimal | 综合费率（管理+托管+销售），单位 `%`（年化） |
| `trackEtfCd` | String | 跟踪 ETF 代码（场外联接基金对应的场内 ETF 代码） |
| `trackEtfName` | String | 跟踪 ETF 名称 |
| `turnOver` | BigDecimal | 换手率，单位 `%` |
| `mergeScale` | String | 合并规模（场内+场外合并后文本） |

> **`--type` 对行情字段的影响**：
> - `type=1`（指数）：返回 `yield`（涨跌幅），不返回 ETF 专属字段（`price` / `traval` / `premDisRto`）。
> - `type=2`（ETF）：返回 `yield`（涨跌幅）、`price`（最新价）、`traval`（成交额）、`premDisRto`（溢折率）。
> - `type=3`（场外）：样本返回 `yield`，但没有 `price`／`traval`／`premDisRto`；场外收益字段不能视为盘中报价。

---
