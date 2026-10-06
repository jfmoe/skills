# 场外联接基金详情

`results` 保存各子接口结果，`_errors` 保存失败子接口错误，`params` 保存调用参数。

### 5. otc-detail all — 场外详情页聚合

**参数**：

| CLI 选项 | 说明 | 默认值 |
|---|---|---|
| `--product-code` | 场外基金代码（必填） | — |
| `--index-code` | 跟踪指数代码；缺省时自动获取 | — |
| `--start-date` / `--end-date` | 时间序列起止日 `yyyyMMdd` | 默认查询最近 30 天 |
| `--date-range` | 收益走势日期范围（可选），见 [ETF 详情](etf.md)的 `--date-range` | — |

**返回顶层结构**：`{ productCode, indexCode, params, results, _errors }`

**`results` 包含的子接口 key**：`baseEtfLinkInfo`、`queryTrackIndex`、`scaleChange`、`getProductWindRank`、`linkFundHold`、`getManagerInfo`、`otherSubShare`、`getRiskReturnCharacter`、`getReturnTrendList`。各子接口返回结构详见下方字段说明。

#### baseEtfLinkInfo — 场外基金基本信息
读取该子接口时查阅[列表字段](list.md)的 `dataList` 元素。

#### scaleChange — 规模变化
| 字段 | 类型 | 说明 |
|---|---|---|
| `fundCode` | String | 基金代码 |
| `asset` | BigDecimal | 资产规模，单位 `亿元` |
| `share` | BigDecimal | 基金份额，单位 `份` |
| `assetChangeRatio` | BigDecimal | 较上一季度末资产规模变化率，单位 `%` |
| `shareChangeRatio` | BigDecimal | 较上一季度末份额变化率，单位 `%` |
| `date` | String | 数据日期 `yyyyMMdd`（一般按季度披露） |

#### linkFundHold — 联接基金持仓
| 字段 | 类型 | 说明 |
|---|---|---|
| `fundCode` | String | 基金代码 |
| `endDate` | String | 数据截止日 `yyyyMMdd` |
| `stockRate` | String | 权益（股票）投资占比，单位 `%` |
| `bondRate` | String | 固定收益（债券）投资占比，单位 `%` |
| `fundRate` | String | 基金投资占比，单位 `%` |
| `derivativesRate` | String | 金融衍生品投资占比，单位 `%` |
| `pmRate` | String | 贵金属投资占比，单位 `%` |
| `bbfaRate` | String | 买入返售金融资产占比，单位 `%` |
| `mmiRate` | String | 货币市场工具占比，单位 `%` |
| `currencyRate` | String | 银行存款和结算备付金占比，单位 `%` |
| `fpRate` | String | 理财产品投资占比，单位 `%` |
| `otherRate` | String | 其它资产占比，单位 `%` |
| `top10Fund` | List | 前 10 大重仓基金，元素含名称/代码/占比 `%` |
| `top10Stock` | List | 前 10 大重仓股票，元素含名称/代码/占比 `%` |
| `top5Bond` | List | 前 5 大重仓债券，元素含名称/代码/占比 `%` |

#### otherSubShare — 同基金其它份额
| 字段 | 类型 | 说明 |
|---|---|---|
| `fundName` | String | 基金全称 |
| `shortName` | String | 基金简称 |
| `fundCode` | String | 当前份额基金代码 |
| `shareType` | String | 份额类型，如 `"A"`、`"C"`、`"D"`、`"E"` |
| `fundMainCode` | String | 基金主代码（同一基金不同份额共享） |
| `foundDate` | String | 成立日期 `yyyyMMdd` |
| `confirmDays` | Integer | 交易确认时间（单位：天） |
| `fundStatus` | String | 基金运作状态枚举：`"0"`=运作中；`"10"`=已清盘；`"12"`=成立中（建仓期） |
| `holdPeriodFund` | String | 是否持有期基金：`"1"`=是；`"0"`=否 |
| `holdPeriod` | String | 持有期基金的持有期限（业务文本，如「30 天」「6 个月」） |

#### queryTrackIndex / getManagerInfo / getRiskReturnCharacter / getReturnTrendList
读取这些子接口时，查阅 [ETF 详情](etf.md)中的同名字段表。

---
