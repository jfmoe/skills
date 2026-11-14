# fund-holding-detail

| 项 | 值 |
|---|---|
| `api_id` | `fund-holding-detail` |
| 服务端登记名 | 基金持股明细 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

按报告期返回基金的**逐只股票持仓明细**：持股数、占净值比、市值、占流通股比、行业、概念、PE/PB、季度涨跌幅、占比变化。
取数走**线上 DS 报表通道**（dataservice），服务端透传上游结果，不复刻报告期展开、主体解析与占比换算逻辑。

适用：用户问「这只基金重仓了哪些股票」「某只股票占净值多少」「上季度加了还是减了」「持仓里有哪些概念股」。

## 2. 不适用场景与易混接口

- **与 `fund-industry-dist` 的区别**：那个是**行业聚合**；本接口是**个股明细**。
- **与 `fund-industry-concentration` 的区别**：那个是 Top1~5 的**集中度数值**。
- **与 `fund-manager-position-detail` 的区别**：那个主体是**基金经理**；本接口主体是单只基金。
- ⚠ **入参口径特殊**：本接口要 `fundObject`（**基金内码**列表），不是其它接口常用的 `fundCode`（带 `.OF` 的 GilCode）。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | array\<string\> | **是** | 基金**内码**列表。容忍数组 / 逗号分隔字符串 / 单个标量，服务端去重；空 / 缺失 / 元素非整数 → 400。⚠ **不是 GilCode** |
| `beginDate` | string | 否 | 区间起点 `yyyy-MM-dd`，严格日历校验；不传 = 不下推，缺省由上游决定 |
| `endDate` | string | 否 | 区间终点 `yyyy-MM-dd`，严格日历校验；不传 = 不下推，缺省由上游决定；早于 `beginDate` → 400 |
| `stockObject` | array\<string\> | 否 | 股票**内码**过滤列表；空 / 不传 = 不过滤 |
| `poscharacter` | integer | 否 | 持仓类型，取值见下方速查表；非整数 → 400 |

**`poscharacter` 值=含义速查表（本节为唯一权威）**：

| 值 | 含义 |
|---|---|
| `1` | 重仓股票 |
| `2` | 全部持股 |
| 不传 | **不下推**（上游缺省，服务端不注入默认值） |

其余整数原样下推，服务端不设白名单。空值一律不下推，服务端不额外下发分页或指标选择参数。

## 4. 调用示例

```bash
# 指定基金内码与报告期区间
pixi run etf-htbr invoke fund-holding-detail '{"fundObject":["<基金内码>"],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 切全部持股口径
pixi run etf-htbr invoke fund-holding-detail '{"fundObject":["<基金内码>"],"poscharacter":2}'
# 叠加股票内码过滤
pixi run etf-htbr invoke fund-holding-detail '{"fundObject":["<基金内码>"],"stockObject":["<股票内码>"]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `fundObject` | 请求内码回显（去重后） |
| `beginDate` / `endDate` | 请求日期回显（未传为 `null`） |
| `poscharacter` | 实际下推的持仓类型（未传为 `null`） |
| `recordCount` | 持仓行数 |
| `records[]` | 逐只股票持仓行，字段见下表 |

`records[]` 每行 **19 字段**，键为上游报表列名**全小写**（不要按小驼峰取值）：

| 字段 | 含义 |
|---|---|
| `fundcode` | 基金代码 |
| `enddate` | 报告期（`yyyy-MM-dd` 字符串） |
| `fundobject` | 基金内码 |
| `fundname` | 基金简称 |
| `stockobject` | 股票内码 |
| `stockcode` / `stockname` | 股票代码 / 简称 |
| `shareholding` | 持仓量（**万股**） |
| `proportionstock` | 持仓股占流通股比（**%**） |
| `marketvalue` | 市值（**万元**） |
| `ratioinmv` | 持仓市值占资产净值比（**%**） |
| `proportionchange` | 持仓市值占资产净值比变化（**%**） |
| `quarterchange` | 季度涨跌（**%**） |
| `pe` / `pb` | 市盈率 / 市净率 |
| `industryname` | 行业名称 |
| `conceptname` | 所属概念 |
| `reporttype` | 报告期类型 |
| `poscharacter` | 持仓类型 |

> 与线下 SQL 版的两处差异：行字段键名改为**全小写**；线下版自造的 `proportionMVOfEquity`（占股票市值比）**不在上游出参面内，不再返回**。

## 6. 数据口径

- **服务端只透传**：报告期展开、主体解析（场内负码 / 子基金换主基金 / 转型链）、QDII 分流、占比换算与舍入、排序都在上游完成；服务端不复刻、不二次舍入、不重排，`records[]` 顺序以上游返回为准。
- `shareholding` / `marketvalue` 已换算为**万股 / 万元**，各比例列为**百分数**，展示直接使用，不要再 ÷1e4 或 ×100。
- `null` 原样保留，**不补 0、不过滤**；`enddate` 是字符串不是时间戳。
- `stockcode` / `stockname` 由上游给出，不要与其它接口的证券代码口径跨表比对。
- 无数据不报错，见第 7 节。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 空 / 缺失 / 含非整数；日期非 `yyyy-MM-dd` 或日历非法；`endDate` 早于 `beginDate`；`poscharacter` 非整数 |
| 200 + `recordCount=0` + `records: []` + `W202_NO_DATA` | 上游明确空结果或区间内无持仓：**正常语义**，如实说明，不要当成取数失败 |
| 503 `DEGRADED` | 上游取数运行时失败（超时 / 拒连 / 业务失败）；服务端不返回任何内置或示例数据 |
| `pe` / `pb` / `industryname` / `conceptname` 等为 `null` | 该股票对应数据缺失，展示为「—」，不要当成 0 |
| 404 `FUND_NOT_FOUND` | **不会出现**：本接口按内码列表取数，不做基金代码解析；误传 GilCode 只会得到 0 行或 400 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **必须先拿到基金内码**：本接口不吃 GilCode。若手上只有 6 位代码或带后缀代码，先解析成 `InnerCode` 再调用。
- 列表参数为空 / 不传即不过滤；不要传空数组试图表达「查全部」以外的含义。
- 读取 `records[]` 时用第 5 节的**全小写**字段名；不要沿用旧版小驼峰字段名。

## 9. 相关工作流

无（但基金内码解析是前置步骤，见第 8 节）。
