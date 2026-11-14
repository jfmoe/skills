# fund-nav

| 项 | 值 |
|---|---|
| `api_id` | `fund-nav` |
| 服务端登记名 | 净值表现 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回基金的**逐日净值序列**：单位净值、累计净值、复权因子与复权净值、日增长率，货币基金另含 7 日年化与每万份收益。
支持自定义区间与统计周期。取数走**线上 DS 报表通道**（dataservice），服务端透传上游结果。

适用：用户问「最新净值多少」「累计净值多少」「某段时间每天的净值」「换算复权净值」「货币基金 7 日年化多少」。

## 2. 不适用场景与易混接口

- **要看走势曲线 / 区间涨了多少**：用 `fund-nav-trend`（首日归零的走势线），本接口给的是**绝对净值序列**。
- **要净值变动的财务科目**（期初/期末、经营/份额交易/分配利润）：用 `fund-nav-change`，入参也是基金内码。
- **要看场内交易价格**（收盘价、涨跌幅、成交额）：用 `fund-daily-quote`，那是**行情不是净值**。
- **要区间累计收益 / 最大回撤 / 夏普等聚合指标**：用 `fund-return-sum` / `fund-max-dd` / `fund-sharpe`，本接口不返回聚合值。
- ⚠ **入参口径特殊**：本接口要 `fundObject`（**基金内码**列表），不是其它接口常用的 `fundCode`（6 位代码或带 `.OF` 的 GilCode）。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | array\<integer\> | **是** | 基金**内码**列表。容忍数组 / 逗号分隔字符串 / 单个标量，服务端去重；空 / 缺失 / 元素非正整数 → 400。⚠ **不是 6 位代码、不是 GilCode** |
| `beginDate` | string | 否 | 区间起点 `yyyy-MM-dd`，严格日历校验；不传 = 不下推，缺省由上游决定 |
| `endDate` | string | 否 | 区间终点 `yyyy-MM-dd`，严格日历校验；不传 = 不下推；早于 `beginDate` → 400 |
| `statisticalPeriod` | integer | 否 | 统计周期，取值见下方速查表；非整数 → 400 |

**`statisticalPeriod` 值=含义速查表（本节为唯一权威）**：

| 值 | 含义 |
|---|---|
| `0` | 日 |
| `1` | 周 |
| `2` | 月 |
| 不传 | **不下推**（上游缺省，服务端不注入默认值） |

其余整数原样下推，服务端不设白名单。空值一律不下推，服务端不额外下发分页或指标选择参数。

> 参数名大小写：调用方按本节**小驼峰**传参（服务端同时接受 `FundObject` 这类大驼峰写法）；服务端下推上游的报文键为报表 `@JsonProperty` 原值 `FundObject` / `BeginDate` / `EndDate` / `StatisticalPeriod`，调用方无需关心。

## 4. 调用示例

```bash
# 指定内码，取上游缺省区间
pixi run etf-htbr invoke fund-nav '{"fundObject":[<基金内码>]}'
# 指定区间
pixi run etf-htbr invoke fund-nav '{"fundObject":[<基金内码>],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 按月取样
pixi run etf-htbr invoke fund-nav '{"fundObject":[<基金内码>],"statisticalPeriod":2}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `fundObject` | 请求内码回显（去重后） |
| `beginDate` / `endDate` | 请求日期回显（未传为 `null`） |
| `statisticalPeriod` | 实际下推的统计周期（未传为 `null`） |
| `recordCount` | 净值行数 |
| `records[]` | 逐日净值行，字段见下表 |

`records[]` 每行 **11 字段**，键为上游报表列名**全小写**（不要按小驼峰取值）：

| 字段 | 含义 |
|---|---|
| `fundobject` | 基金内码 |
| `fundcode` | 基金代码 |
| `fundname` | 基金简称 |
| `enddate` | 截止日期（`yyyy-MM-dd` 字符串，不是时间戳） |
| `unitnv` | 单位净值（**元**） |
| `accumulatedunitnv` | 单位累计净值（**元**） |
| `growthratefactor` | 复权因子（可缺省，未命中为 `null`） |
| `unitnvrestored` | 复权单位净值（**元**，可缺省） |
| `nvdailygrowthrate` | 单位基金净值增长率（**%**） |
| `annualizedrrinsingleweek` | 最近 7 日折算年收益率（**%**，货币基金，可缺省） |
| `dailyyieldpertenthousand` | 每万份基金单位当日收益（**元**，货币基金，可缺省） |

> 与旧版的差异：入参由 `fundCode` 改为 `fundObject`；数据路径由 `$.data.navs[]` 改为 `$.data.records[]`；字段名由小驼峰（`unitNav`/`accUnitNav`/`dailyGrowthRate`）改为**全小写**（`unitnv`/`accumulatedunitnv`/`nvdailygrowthrate`）。

## 6. 数据口径

- **服务端只透传**：转型组展开、交易日历过滤、日涨跌幅重算、复权与货币基金补列、舍入与排序都在上游完成；服务端不复刻、不二次舍入、不重排，`records[]` 顺序以上游返回为准。
- 净值单位**元**，`nvdailygrowthrate` / `annualizedrrinsingleweek` 为**百分数**，展示直接加 `%`，**不要再 ×100**。
- `null` 原样保留，**不补 0、不过滤**；4 个可缺省列（`growthratefactor` / `unitnvrestored` / `annualizedrrinsingleweek` / `dailyyieldpertenthousand`）未命中即 `null`，展示为「—」。
- 上游对**每只基金首个净值行**保留原始日增长率、**第 2 行起**按相邻净值比重新计算 —— 该逻辑已在上游完成，读取时无需自行重算。
- 转型基金的历史净值已在上游按转型链展开，**不需要**调用方再按转型代码拼接。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 空 / 缺失 / 含非整数；日期非 `yyyy-MM-dd` 或日历非法；`endDate` 早于 `beginDate`；`statisticalPeriod` 非整数 |
| 200 + `recordCount=0` + `records: []` + `W202_NO_DATA` | 内码无对应基金、或区间内无净值：**正常语义**，如实说明，不要当成取数失败 |
| 503 `DEGRADED` | 上游取数运行时失败（超时 / 拒连 / 业务失败）；服务端不返回任何内置或示例数据 |
| 某个净值为 `null` | 该日期对应数据缺失（如复权列未覆盖），展示为「—」，不要当成 0 |
| 404 `FUND_NOT_FOUND` | **不会出现**：本接口按内码取数，不做代码解析；误传 6 位代码只会得到 0 行或 400 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **必须先拿到基金内码**：本接口不吃 6 位代码或 GilCode。若手上只有代码，先解析成 `InnerCode` 再调用。
- 区间不设硬顶，但整只基金全历史逐日返回可能很大；只取最近一段就显式传 `beginDate`。
- 读取 `records[]` 时用第 5 节的**全小写**字段名；不要沿用旧版小驼峰字段名。

## 9. 相关工作流

无（但基金内码解析是前置步骤，见第 8 节）。
