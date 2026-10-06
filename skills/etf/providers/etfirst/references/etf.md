# ETF 详情

```bash
etfirst --json etf-detail all --product-code 510300
```

### 4. etf-detail all — ETF 详情页聚合

**参数**：

| CLI 选项 | 说明 | 默认值 |
|---|---|---|
| `--product-code` | ETF 产品代码（必填），例 `510300` | — |
| `--index-code` | 跟踪指数代码；缺省时自动调跟踪指数接口获取 | — |
| `--start-date` / `--end-date` | 时间序列起止日 `yyyyMMdd` | 默认查询最近 30 天 |
| `--date-range` | 整数枚举（CLI 使用 `type=int`）；枚举含义未核实，优先显式传 `--start-date`／`--end-date`，不传 `1m` 等字符串 | — |
| `--net-inflow-type` | 净流入口径：`3`=本产品净流入；`2`=同指数下全部同类 ETF 合计净流入；`1`=子接口 `data` 返回 `null`（后端未实现） | `3` |

**返回顶层结构**：`{ productCode, indexCode, params, results, _errors }`；`results` 保存各子接口结果，`_errors` 保存失败子接口错误，`params` 保存调用参数

**`results` 包含的子接口 key**：`getMarketIndicatorData`、`queryTrackIndex`、`getEtfLinkInfo`、`getNetInflow`、`getProductWindRank`、`getManagerInfo`、`getRiskReturnCharacter`、`getHoldStock`、`getIndustryDistribution`、`getReturnTrendList`、`getRealTimeData`。各子接口返回结构详见下方字段说明。

#### getMarketIndicatorData — 市场指标
在[列表字段](list.md)的 `dataList` 元素全部字段之上（读取市场指标时查阅该表），额外提供下列「智选标签」字段（用于产品筛选高亮）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `smartSelect` | Integer | 是否雷达智选推荐：`1`=是，`0`=否 |
| `scaleBig` | Integer | 是否规模较大：`1`=是，`0`=否 |
| `trackErrorSmall` | Integer | 是否跟踪误差较小：`1`=是，`0`=否 |
| `premDisRtoLow` | Integer | 是否折价率较低：`1`=是，`0`=否 |
| `comRatioLow` | Integer | 是否综合费率较低：`1`=是，`0`=否 |

#### queryTrackIndex — 跟踪指数
返回 `HotIndexVo`（继承 `RealTimeModel`），含指数基本信息、估值、实时行情等字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| `indexCode` / `indexName` / `indexAbbr` | String | 指数代码 / 全称 / 简称 |
| `infoIndexCode` | String | 统一资讯（聚源）指数代码 |
| `indexWindCode` | String | 万得（Wind）指数代码 |
| `trackIndexType` | String | 跟踪指数类型标签（业务自定义文本） |
| `indexType` | Integer | 类型枚举：`1`=指数；`2`=ETF；`3`=场外 |
| `ibm` | String | 分类代码 |
| `type` | String | 分类名称 |
| `typeLv1` / `typeNameLv1` | String | 一级分类代码 / 中文名 |
| `typeLv2` / `typeNameLv2` | String | 二级分类 |
| `typeLv3` / `typeNameLv3` | String | 三级分类 |
| `typeNameLv4` | String | 四级分类名称 |
| `trackCode` | String | 追踪指数代码 |
| `setUpDate` | String | 成立日期 `yyyyMMdd` |
| `netInflow` | BigDecimal | 净流入金额，单位 `亿元` |
| `pe` | BigDecimal | 最新交易日市盈率（PE-TTM），倍 |
| `peAvg` | String | PE 分位平均值 |
| `pePercent` | BigDecimal | PE 历史分位（从 2016-01-04 起），单位 `%` |
| `peLevel` | String | PE 等级标识（业务自定义档位） |
| `pb` / `pbAvg` / `pbPercent` | BigDecimal | 最新交易日市净率 / PB 历史均值 / PB 历史分位，分位单位 `%` |
| `fed` / `fedAvg` / `fedPercent` | String | FED 比値 / 历史均値（从 2016-01-04 起）/ 历史分位（从 2016-01-04 起），分位单位 `%` |
| `lastYearPerChange` | String | 最新交易日起向前推 12 个自然月涨跌幅，单位 `%` |
| `yelid` | BigDecimal | 日涨跌幅，单位 `%`（注意字段拼写） |
| `rankLabel` | Integer | 同类排名（业务自定义档位） |
| `isLinkRelation` | Boolean | 是否直接跳转到关联详情 |
| `isRecommend` | Integer | 是否精选推荐：`1`=是 |
| `isSouthFund` | Integer | 是否南方基金产品：`1`=是 |
| `relateFund` | Object | 关联的本公司同类产品（含代码/简称等） |

**继承自 RealTimeModel 的实时行情字段**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `tradingDay` | String | 交易日 `yyyyMMdd` |
| `time` | String | 时刻 `HHmmssSSS` |
| `percentageChange` | String | 涨跌幅，单位 `%` |
| `prePercentChange` | String | 前一交易日涨跌幅，单位 `%` |
| `closePrice` | String | 当前点位/价格 |
| `preClosePrice` | String | 前一交易日收盘点位 |
| `nowPrice` | String | 当前价 |
| `openPrice` | String | 开盘价 |
| `highPrice` | String | 最高价 |
| `lowPrice` | String | 最低价 |
| `turnover` | String | 成交金额，上游声明元；原始行情数值缩放须核实 |
| `volume` | String | 成交量，单位 `手` |
| `iopv` | String | 净值估算（IOPV） |
| `premDisRto` | String | 溢折率，单位 `%` |

#### getEtfLinkInfo — ETF 联接信息
| 字段 | 类型 | 说明 |
|---|---|---|
| `etfFundCode` | String | 场内 ETF 基金代码 |
| `etfFundName` | String | 场内 ETF 名称 |
| `etfLinkFundCode` | String | 对应的 ETF 联接基金代码（场外申赎） |
| `etfLinkFundName` | String | ETF 联接基金名称 |
| `yieldSinceLaunch` | String | 联接基金成立以来收益率，单位 `%` |
| `productScale` | String | 产品规模，单位 `亿元` |
| `scaleDate` | String | 规模数据日期 `yyyyMMdd` |

#### getNetInflow — 净流入
返回 `List<NetInflowModel>`（`type=1` 时 `data` 为 `null`），按 `tradingDay` 升序。

| 字段 | 类型 | 说明 |
|---|---|---|
| `tradingDay` | String | 交易日 `yyyyMMdd` |
| `productCode` | String | 产品代码，仅 `type=3` 返回 |
| `indexCode` | String | 对应指数代码，仅 `type=2` 返回 |
| `netInflow` | BigDecimal | 单日净流入，单位 `亿元`。正=净流入，负=净流出 |

#### getProductWindRank — Wind 排名
返回 `List<Map<String, Object>>`，字段随产品类型动态变化，典型字段包括：基金代码、近 1M/3M/6M/1Y/3Y 收益率（单位 `%`）、同类排名（同类型基金中的名次）、分位（单位 `%`）等。

#### getManagerInfo — 基金经理
| 字段 | 类型 | 说明 |
|---|---|---|
| `managerId` | long | 经理 ID |
| `managerName` | String | 经理姓名 |
| `managerHeaderUrl` | String | 经理头像图片 URL |
| `workYears` | String | 从业年限（年），截至当前系统日期动态计算 |
| `managerLabel` | String | 经理标签（如「金牛」「明星」等业务标签） |

#### getRiskReturnCharacter — 风险收益特征
按统计区间分行返回：

| 字段 | 类型 | 说明 |
|---|---|---|
| `dateRange` | Integer | 统计区间枚举：`12`=近 1 年；`36`=近 3 年；`60`=近 5 年 |
| `endDate` | String | 数据截止日 `yyyyMMdd` |
| `standardDeviation` | BigDecimal | 区间波动率，单位 `%`（年化） |
| `rankStandardDeviation` | BigDecimal | 波动率同类排名百分位，单位 `%`（越低=越平稳） |
| `sharpeRatio` | BigDecimal | 夏普比率（无量纲，越大=风险调整后收益越优） |
| `rankSharpeRatio` | BigDecimal | 夏普比率同类排名百分位，单位 `%`（越低=越优） |
| `maximumBack` | BigDecimal | 最大回撤，单位 `%`（一般为负） |
| `rankMaximumBack` | BigDecimal | 最大回撤同类排名百分位，单位 `%`（越低=回撤越小） |

#### getHoldStock — 持仓股票
| 字段 | 类型 | 说明 |
|---|---|---|
| `holdName` | String | 持仓股票名称 |
| `holdWeight` | String | 占基金净值比，单位 `%` |
| `marketValue` | String | 持仓市值，单位 `元` |
| `holdAmount` | String | 持仓数量，单位 `股` |
| `endDate` | String | 持仓数据截止日 `yyyyMMdd`（季度披露） |
| `industryName` | String | 所属行业中文名 |
| `changeRatio` | String | 较上季度持仓权重变化，单位 `%` |

#### getIndustryDistribution — 行业分布
返回 `Map<分类层级名, List>`，每个 List 元素：

| 字段 | 类型 | 说明 |
|---|---|---|
| `industryName` | String | 行业中文名 |
| `industryRatio` | String | 该行业在基金中的占比，单位 `%` |
| `endDate` | String | 数据截止日 `yyyyMMdd` |

#### getReturnTrendList — 收益走势

返回 map 的键标识产品或指数；`closePrice` 随实体分别表示产品序列值或指数点位，不能统一当成未复权价格／单位净值。样本产品值与未复权单位净值不同，复权定义需另核实。`maxRetreat` 样本为正值，保持返回符号；`turnover` 样本单位与上游表“元”不一致，换算前核实。

返回 `Map<序列名, List>`，每条记录：

| 字段 | 类型 | 说明 |
|---|---|---|
| `tradeDate` | String | 交易日 `yyyyMMdd` |
| `closePrice` | String | 依序列键识别产品序列值或指数点位；复权定义需核对 |
| `dailyReturn` | String | 涨跌幅，单位 `%` |
| `yield` | String | 基准收益率，单位 `%` |
| `maxRetreat` | String | 区间回撤幅度；样本为正数，不强行改变符号 |
| `turnover` | String | 成交金额；收益走势子项的单位未核实，勿沿用行情子项单位 |

#### getRealTimeData — 实时行情（场内 ETF，type=2）
此字段表来自上游说明；返回值缩放与上游单位可能不一致，展示前按[数值核验](presentation.md)处理。后端子接口路径：`POST /etfapp/retail/product/getRealTimeData`，请求体 `{productCode, type="2"}`。通用字段见本文件 `queryTrackIndex` 下的 RealTimeModel 表，场内 ETF 的以下字段使用二级市场报价口径：

| 字段 | 类型 | 说明 |
|---|---|---|
| `closePrice` | String | 当前二级市场成交价（交易时段）或收盘价，单位 `元/份` |
| `preClosePrice` | String | 前一交易日收盘价，单位 `元/份` |
| `nowPrice` | String | 当前价（语义同 `closePrice`） |
| `openPrice` / `highPrice` / `lowPrice` | String | 当日开盘/最高/最低价，单位 `元/份` |
| `turnover` | String | 本 ETF 交易金额（当日累计），单位 `元` |
| `volume` | String | 本 ETF 成交量（当日累计），单位 `手` |
| `iopv` | String | ETF 净值估算（IOPV），单位 `元/份` |
| `premDisRto` | String | 溢折率 = (closePrice - iopv) / iopv，单位 `%`，后端自动按上述公式计算 |

> **时效性**：**交易时段**返回当日实时行情（5 秒刷新）；⚠ Agent 无需自行判断当天是否为交易日，仅需如实标注 API 返回的数据日期；**禁止**从数据日期反推交易日历。

---
