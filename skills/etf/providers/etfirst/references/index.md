# 指数详情

```bash
etfirst --json index-detail all --index-code 000300 --index-type 1
```

### 3. index-detail all — 指数详情页聚合

**参数**：

| CLI 选项 | 说明 | 默认值 |
|---|---|---|
| `--index-code` | 指数代码（必填），例 `000300` | — |
| `--index-type` | 指数大类：`1`=宽基指数；`2`=行业指数 | `2` |
| `--start-date` | 时间序列起始日 `yyyyMMdd` | 默认查询最近 30 天|
| `--end-date` | 时间序列结束日 `yyyyMMdd` | 当前日期 |
| `--net-inflow-type` | 净流入口径：`major`=指数主力净流入；`etf`=追踪该指数的全部 ETF 合计净流入（单位见下文） | `major` |

**返回顶层结构**：`{ indexCode, params, results, _errors }`

| 字段 | 说明 |
|---|---|
| `indexCode` | 本次请求的指数代码 |
| `params` | 本次请求所用参数的快照（便于复现） |
| `results` | 所有子接口的结果字典（key 见下表） |
| `_errors` | 失败子接口的错误信息：`key`=子接口名，`value`=错误描述。子接口并行调用，单点失败不影响其它结果 |

**`results` 包含的子接口 key**：`queryRiskReturnRatio`、`queryIndustryDistribution`、`queryChangeRateByIndexCode`、`queryIndexArchive`、`list`、`queryCompanyWeight`、`queryNetInflow`、`queryIndexDetail`、`getRealTimeData`。各子接口返回结构详见下方字段说明。

#### queryRiskReturnRatio — 风险收益比
| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | Integer | 统计区间枚举：`12`=返1 年；`36`=返3 年；`60`=返5 年 |
| `tradingday` | String | 数据所属交易日 `yyyyMMdd` |
| `volatility` | String | 区间波动率，单位 `%`（年化） |
| `volatilityRank` | String | 同类排名百分位，单位 `%`（越低=越平稳） |
| `sharpeRatio` | String | 区间夏普比率（无量纲，越大=风险调整后收益越好） |
| `sharpeRatioRank` | String | 同类排名百分位，单位 `%`（越低=越优） |
| `maxDrawdown` | String | 区间最大回撤，单位 `%`（一般为负数） |
| `maxDrawdownRank` | String | 同类排名百分位，单位 `%`（越低=回撤越小） |

#### queryIndustryDistribution / queryCompanyWeight — 成分与行业

实测 `queryIndustryDistribution` 包含 `companyWeightList` 与 `endDate`，`queryCompanyWeight` 包含三级行业列表与 `tradingday`。上游将两组字段混在同一表中，读取时以实际子项归属为准；成分列表样本只有 10 行，不能当作指数全部成分。日期样本为最近快照，不随历史起止范围回放。

以下表解释字段含义，不保证它们同时位于同一个子项。

| 字段 | 类型 | 说明 |
|---|---|---|
| `firstWeightList` | List | 一级行业权重列表，元素结构见 **CompanyTypeWeight** |
| `secondWeightList` | List | 二级行业权重列表 |
| `thirdWeightList` | List | 三级行业权重列表 |
| `companyWeightList` | List | 成分股权重列表，元素结构见 **CompanyWeight** |
| `tradingday` | String | 交易日 `yyyyMMdd` |
| `endDate` | String | 数据截止日 `yyyyMMdd` |

**CompanyTypeWeight**（行业权重）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `industryName` | String | 行业中文名 |
| `weight` | String | 占比，单位 `%` |

**CompanyWeight**（成分股权重）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `stockName` | String | 股票名称 |
| `industryName` | String | 所属行业 |
| `weight` | String | 占指数权重，单位 `%` |
| `changeVsPrevious` | String | 较上次指数调仓时的权重变化，单位 `%` |

#### queryChangeRateByIndexCode — 涨跌幅
| 字段 | 类型 | 说明 |
|---|---|---|
| `indexCode` | String | 指数代码 |
| `tradingday` | String | 数据日期 `yyyyMMdd` |
| `lastOneWeekChangeRate` | String | 最新交易日起向前推 1 周（自然周）涨跌幅，单位 `%` |
| `lastOneMonthChangeRate` | String | 最新交易日起向前推 1 个自然月涨跌幅，单位 `%` |
| `lastThreeMonthChangeRate` | String | 最新交易日起向前推 3 个自然月涨跌幅，单位 `%` |
| `thisYearChangeRate` | String | 本年 1 月 1 日至最新交易日涨跌幅，单位 `%` |

#### queryIndexArchive — 指数档案（静态信息）
| 字段 | 类型 | 说明 |
|---|---|---|
| `indexCode` | String | 指数代码 |
| `indexName` | String | 指数中文全称 |
| `abbrIndexName` | String | 指数简称 |
| `institutionName` | String | 编制/发布机构（如「中证指数」「国证指数」） |
| `baseValue` | String | 基点数值（指数发布时的起始点位） |
| `baseDate` | String | 基日 `yyyyMMdd` |
| `constituentNumber` | String | 样本（成分）数量 |
| `indexProfile` | String | 指数简介（文本段落） |
| `publishDate` | String | 指数发布日期 `yyyyMMdd` |
| `totalMarketCap` | String | 指数总市值，单位 `亿元` |
| `totalFreeFloatMarketCap` | String | 指数自由流通市值合计，单位 `亿元` |
| `maxFreeFloatMarketCap` | String | 单一样本最大自由流通市值，单位 `亿元` |
| `minFreeFloatMarketCap` | String | 单一样本最小自由流通市值，单位 `亿元` |
| `averageFreeFloatMarketCap` | String | 样本自由流通市值均值，单位 `亿元` |
| `medianFreeFloatMarketCap` | String | 样本自由流通市值中位数，单位 `亿元` |

#### list — 历史估值序列
返回每个交易日的 PE/PB 与分位。实测传入两天的起止日期仍返回 2016 年以来的全序列，不能假定所有子结果都按参数裁剪；需要目标区间时检查并按 `JYR` 本地过滤。每条记录字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `JYR` | String | 交易日 `yyyyMMdd` |
| `ZSDM` | String | 指数代码 |
| `INDEXCODE` | String | 统一资讯指数代码 |
| `PE` | String | 市盈率，单位：倍 |
| `PEFW` | String | PE 历史分位（从 2016-01-04 起），单位 `%`（0~100） |
| `PB` | String | 市净率，单位：倍 |
| `PBFW` | String | PB 历史分位（从 2016-01-04 起），单位 `%`（0~100） |

#### queryNetInflow — 指数相关净流入数据
返回 `List<NetInflowVo.NetInflow>`，按 `tradingDay` 升序。调用口径由 `--net-inflow-type` 决定：`major`=指数主力净流入；`etf`=追踪该指数的全部 ETF 合计净流入。上游字段表标为亿元，但 CLI 参数说明将 `etf` 标为元，二者冲突。中证红利六只 ETF 在 20260810/11 的逐只亿元净流入合计为 -2.607533／3.110250，与该接口 -2.61／3.11 的两位小数结果一致，样本支持亿元口径。其他指数仍核对口径，不能依据 CLI 帮助按元换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| `indexCode` | String | 指数代码（同入参 `indexCode`） |
| `tradingDay` | String | 交易日 `yyyyMMdd` |
| `netInflowValue` | String | 单日净流入金额，单位 `亿元`。正=净流入，负=净流出 |

#### queryIndexDetail — 指数综合详情

下表包含上游声明字段。当前 000922 样本非空返回 PE/PB 及分位、股息率、ROE；没有 FED、FED 分位、ROE 分位或观点字段，使用前必须确认实际存在。
| 字段 | 类型 | 说明 |
|---|---|---|
| `indexCode` | String | 指数代码 |
| `indexName` | String | 指数名称 |
| `infoIndexCode` | String | 统一资讯指数代码 |
| `windIndexCode` | String | 万得（Wind）指数代码 |
| `type` | String | 指数类型枚举：`"01"`=宽基；`"05"`=行业；其余表示策略/主题等 |
| `sort` | Integer | 显示排序权重（小在前） |
| `opinionTitle` | String | 分析师观点标题 |
| `opinion` | String | 分析师观点正文 |
| `pe` | String | 最新交易日市盈率（PE-TTM），单位：倍 |
| `peAvg` | String | PE 历史均値（从 2016-01-04 起），单位：倍 |
| `pePercent` | String | PE 历史分位（从 2016-01-04 起），单位 `%` |
| `pb` / `pbAvg` / `pbPercent` | String | 同上，PB 维度；均値与分位同样从 2016-01-04 起计算 |
| `fed` | String | FED 溢价比値（股权风险溢价指标 = 1/PE − 无风险利率），数值越大代表股票相对债券越有性价比 |
| `fedAvg` | String | FED 历史均値（从 2016-01-04 起） |
| `fedPercent` | String | FED 历史分位（从 2016-01-04 起），单位 `%` |
| `lastYearPerChange` | String | 最新交易日起向前推 12 个自然月涨跌幅，单位 `%` |
| `pointValue` | String | 当前指数点位。**集成自实时行情**：仅交易时段每 5 秒更新，非交易时段保留上一次刷新的值（收盘后数据更新存在延迟） |
| `pointValueUpdateTime` | String | 点位最后一次刷新时间（与 `pointValue` 同步），格式 `yyyy-MM-dd HH:mm:ss` |
| `percentageChange` | String | 前一交易日涨跌幅，单位 `%` |
| `dividendYield` | String | 股息率，单位 `%` |
| `roe` | String | 净资产收益率 ROE，单位 `%` |
| `roePercent` | String | ROE 同类排名百分位，单位 `%` |
| `roeSpeed` | String | ROE 同比增速，单位 `%` |
| `etfScale` | String | 追踪本指数的 ETF 合计规模，单位 `亿元` |
| `otcScale` | String | 追踪本指数的场外基金合计规模，单位 `亿元` |
| `netInFlow` | String | 净流入金额，单位 `亿元` |
| `netInFlowPercent` | String | 净流入同类排名百分位，单位 `%` |
| `preClosePrice` | String | 前一交易日收点位 |
| `openPrice` | String | 今日开盘点位 |
| `traceEtfs` | List | 南方基金追踪本指数的 ETF 列表，元素含产品代码、简称等 |
| `videoUrl` | String | 关联视频 URL |
| `updateTime` | String | 数据更新时间 `yyyy-MM-dd HH:mm:ss` |

#### getRealTimeData — 实时行情（指数，type=1）
此字段表来自上游说明；返回值缩放与上游单位可能不一致，展示前按[数值核验](presentation.md)处理。后端子接口路径：`POST /etfapp/retail/product/getRealTimeData`，请求体 `{productCode=indexCode, type="1"}`。

| 字段 | 类型 | 说明 |
|---|---|---|
| `tradingDay` | String | 交易日 `yyyyMMdd` |
| `time` | String | 实时时刻 `HHmmssSSS`（时分秒毫秒） |
| `percentageChange` | String | 当日指数涨跌幅，单位 `%` |
| `prePercentChange` | String | 前一交易日涨跌幅，单位 `%` |
| `closePrice` | String | 当前点位（交易时段）或收盘点位（非交易时段） |
| `preClosePrice` | String | 前一交易日收盘点位 |
| `nowPrice` | String | 当前点位，实时同步（语义同 `closePrice`） |
| `openPrice` | String | 当日开盘点位 |
| `highPrice` | String | 当日最高点位 |
| `lowPrice` | String | 当日最低点位 |
| `turnover` | String | 指数成分股合计成交金额（当日累计），单位 `元` |
| `volume` | String | 指数成分股合计成交量（当日累计），单位 `手` |
| `iopv` | String | 指数不提供，一般为空 |
| `premDisRto` | String | 指数不提供，一般为空 |

> **时效性**：**交易时段**返回当日实时行情（5 秒刷新）；**非交易时段**返回上一个刷新值，收盘后数据更新存在延迟。⚠ Agent 无需自行判断当天是否为交易日，仅需如实标注 API 返回的数据日期；**禁止**从数据日期反推交易日历。

---
