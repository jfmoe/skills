# index-constituents

| 项 | 值 |
|---|---|
| `api_id` | `index-constituents` |
| 服务端登记名 | 指数成分股 |
| 领域 | index |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询**指数成分股明细**：一行 = 一个指数 × 一只成分股，给出权重、行情、成交、股本与市值、所属行业、纳入日期。

适用：用户问「沪深300有哪些成分股」「某个指数里各股权重和涨跌」「某只成分股占指数多少、市值多大」。

## 2. 不适用场景与易混接口

- 要**行业聚合分布**（各行业占多少权重）用 `index-industry-dist`，本接口是**逐股清单**。
- 要**指数自身行情**（指数点位/涨跌/成交）用 `index-daily-quote`（逐日）或 `index-range-quote`（区间）。
- 要**跟踪该指数的基金清单**用 `fund-index-related`。
- ⚠ `indexObject` 取**聚源代码**（`000300.SH`）或**聚源内码**；与 `index-daily-quote` / `index-range-quote` 的 6 位净码口径不同，**不要混用**。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `indexObject` | string[]（兼容单字符串） | **是** | 指数代码列表：聚源代码（`["000300.SH"]`）或聚源内码（`["3145"]`）均可；缺失 / 空白列表 → 400 |
| `endDate` | string | 否 | `YYYY-MM-DD` 截止日期；空 = 当日；格式非法 → 400 |

> ⚠ **没有指标选择入参**：每行同时返回权重/行情/成交/股本市值/行业，展示时按需取用，不要找「选指标」的参数。

## 4. 调用示例

```bash
# 截止当日
pixi run etf-htbr invoke index-constituents '{"indexObject":["000300.SH"]}'
# 指定截止日
pixi run etf-htbr invoke index-constituents '{"indexObject":["000300.SH"],"endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.records[]`，**21 个字段**（DS 列名小写原样）：

| 字段 | 含义 |
|---|---|
| `indexobject` | 指数内码 |
| `indexcode` / `indexname` | 指数代码 / 指数简称 |
| `gilcode` | 指数聚源代码 |
| `stockobject` | 股票内码 |
| `stockcode` / `stockname` | 股票代码 / 股票简称 |
| `stockgilcode` | 股票聚源代码 |
| `weight` | 权重（**%**） |
| `closeprice` | 收盘价（**元**） |
| `change` | 涨跌（**元**） |
| `changerate` | 涨跌幅（**%**） |
| `indexcontrib` | 指数贡献点（**点**，可为负） |
| `volume` | 成交量（**万股**） |
| `amount` | 成交额（**万元**） |
| `totalshare` | 总股本（**亿股**） |
| `totalmarketval` | 总市值（**亿元**） |
| `freefloatshare` | 自由流通股本（**亿股**） |
| `freefloatval` | 自由流通市值（**亿元**） |
| `secondindustry` | 证监会行业 |
| `inclusiondate` | 纳入日期（`yyyy-MM-dd`） |

## 6. 数据口径

- 单位全部在服务端换算完毕：权重/涨跌幅 **%**、成交量 **万股**、成交额 **万元**、股本 **亿股**、市值 **亿元**；**直接展示，不要二次换算**。
- `change` 与 `changerate` 同时给出，前者是价格变动（元）、后者是百分比，**不要互推**。
- `indexcontrib` 是单只成分股对指数点数的贡献，下跌股为负值。
- `secondindustry` 是**证监会行业**（如「计算机、通信和其他电子设备制造业」），非申万/中信口径。
- `inclusiondate` 为该股**纳入指数**的生效日期，缺值表示上游无纳入记录。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `indexObject` 缺失或全为空白；`endDate` 非 `yyyy-MM-dd` |
| 200 + `NO_DATA`（`recordCount=0`） | 指数无法解析、截止日无数据。**不是错误**，不要报「接口失败」 |
| 单字段为 `null` | 该股该口径上游无值（如无自由流通股本），展示为「—」，**不要当成 0** |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- 单次返回所请求指数的成分股全集；跨日对比需多次调用并自行标注截止日。
- 不要用返回条数反推指数成分股总数（上游可能截断），需要总数时以权威指数编制信息为准。

## 9. 相关工作流

无。
