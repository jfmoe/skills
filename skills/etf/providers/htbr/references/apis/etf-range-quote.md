# etf-range-quote

| 项 | 值 |
|---|---|
| `api_id` | `etf-range-quote` |
| 服务端登记名 | 场内基金区间行情 |
| 领域 | fund（场内基金） |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回**场内基金在给定区间内的行情聚合**（每只基金一行）：区间开高低收、区间最高/最低收盘、
区间均价、区间涨跌与涨跌幅、区间振幅、区间成交量额与日均量额、区间换手率与日均换手率。

适用：用户问「这只 ETF 这半年涨了多少」「这段时间最高价到过多少」「区间日均成交额多少」
「这个月振幅多大」「区间换手率多少」。

## 2. 不适用场景与易混接口

- **与 `fund-daily-quote` 的区别**：那个给**逐日明细**（一行/交易日）；本接口给**区间聚合**（一行/基金）。
- **与 `fund-nav-trend` 的区别**：那个给**净值**走势（净值口径）；本接口给**场内成交价**聚合（价格口径）。
- **与 `index-range-quote` 的区别**：那个的标的是**指数**；本接口的标的是**场内基金**。
- 本接口**不给规模、份额、溢价率**；这些走 `etf-capital-report` 或 `fund-asset-size`。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | integer[]（兼容单值） | **是** | 基金**内码**列表（如 `[2997]`），可多只；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |
| `restorationStatus` | integer | 否 | 复权方式：`2` 后复权 / `3` 不复权；不传 = 上游缺省 `3`；传 `1` 或其它值 → 400 `PARAM_INVALID` |
| `beginDate` | string | 否 | `YYYY-MM-DD`；不传则由上游决定区间起点 |
| `endDate` | string | 否 | `YYYY-MM-DD`；不传则由上游决定区间终点 |

> `fundObject` 要的是**内码**，不是 6 位代码、也不是带 `.OF` 的 GilCode。只有名称/代码时先用
> `fund-resolve` 解析，取 `candidates[].innerCode` 再调用本接口。

## 4. 调用示例

```bash
# 单只基金，区间由上游缺省决定（不复权）
pixi run etf-htbr invoke etf-range-quote '{"fundObject":[2997]}'
# 显式区间 + 后复权
pixi run etf-htbr invoke etf-range-quote '{"fundObject":[2997],"restorationStatus":2,"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 多只基金同时对比
pixi run etf-htbr invoke etf-range-quote '{"fundObject":[2997,2998],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（`recordCount` + `records[]`，**每只基金一行**）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `fundobject` / `fundcode` / `fundname` | integer / string / string | 基金内码 / 代码（6 位净码）/ 简称 |
| `begindate` / `enddate` | string | 区间**首个 / 最后一个行情日**（`YYYY-MM-DD`，实际值非请求值） |
| `tradedays` | integer | 区间交易日天数（天） |
| `prevclosepricebt` | number | 区间前收盘价（元） |
| `openpricebt` / `highpricebt` / `lowpricebt` / `closepricebt` | number | 区间开盘 / 最高 / 最低 / 收盘价（元） |
| `hightclosepricebt` / `lowestclosepricebt` | number | 区间**收盘**最高 / 最低价（元） |
| `avgpricebt` | number | 区间均价（元） |
| `changeofpricebt` | number | 区间涨跌（**元**，价差） |
| `changepctbt` | number | 区间涨跌幅（**%**） |
| `rangepctbt` | number | 区间振幅（**%**） |
| `turnovervaluebt` / `turnovervalueperdaybt` | number | 区间成交额 / 日均成交额（**万元**） |
| `turnovervolumebt` / `turnovervolumeperdaybt` | number | 区间成交量 / 日均成交量（**万股**） |
| `turnoverdealsbt` | number | 区间成交笔数（笔） |
| `turnoverratebt` / `turnoverrateperdaybt` | number | 区间换手率 / 日均换手率（**%**） |

## 6. 数据口径

- **涨跌幅、振幅、换手率都是百分数**：`changepctbt` / `rangepctbt` / `turnoverratebt` /
  `turnoverrateperdaybt` 原值即 %（如 `-1.506` = −1.51%），**不要 ×100**。
- **涨跌与涨跌幅是两个字段**：`changeofpricebt` 是价差（元），`changepctbt` 是百分比（%）；
  `rangepctbt` 是**振幅**（区间最高 ÷ 最低的波动幅度），与涨跌幅不是一回事，**不可混用**。
- **`hightclosepricebt` 是区间收盘最高价**（上游既有拼写，不是「最高价」），
  与 `highpricebt`（区间最高价）不同；`lowestclosepricebt` 同理是收盘最低价。
- **单位**：成交额**万元**、成交量**万股**、价格为**元**、笔数为**笔**。注意与 `fund-daily-quote`
  的元 / 股口径不同，跨接口对比时先换算。
- **`begindate` / `enddate` 是实际有行情的首末日**，可能窄于请求区间；`tradedays` 按交易日计，
  小于区间自然日数属正常；日均值 = 区间量额 ÷ `tradedays`。
- **复权方式只影响价格序列**：`restorationStatus=2` 后复权 / `3` 不复权（缺省）。
- 行序由上游决定，未额外排序。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 缺失/空/非内码，`restorationStatus` 非 2/3，日期格式非 `YYYY-MM-DD` |
| 200 + `NO_DATA` 注记 | 基金代码无法解析或区间内无行情 —— 如实说明无数据，不补造 |
| 价格类字段为 `null` | 该基金区间内无对应行情（如长期停牌），展示「—」，不当作 0 |
| `tradedays` 小于区间自然日数 | 正常，按交易日计 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `fundObject` 必须是**基金内码**；名称/代码先用 `fund-resolve`。
- `restorationStatus` 只接受 `2` / `3`，其它值上游直接报错，本接口提前拦为 400。
- 不保证不传日期时上游使用固定区间——需要确定区间就显式传 `beginDate` / `endDate`。

## 9. 相关工作流

- 只有产品名称或代码、没有内码 → 先读 `workflows/fund-code-resolution.md`，用 `fund-resolve` 取 `innerCode`。
- 要看每天的行情 → `fund-daily-quote`；要看净值走势 → `fund-nav-trend`。
