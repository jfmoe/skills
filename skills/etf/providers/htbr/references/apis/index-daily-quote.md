# index-daily-quote

| 项 | 值 |
|---|---|
| `api_id` | `index-daily-quote` |
| 服务端登记名 | 指数日行情 |
| 领域 | index |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回**指数逐日行情**：开高低收、涨跌、涨跌幅、成交量额、指数市值。

适用：用户问「沪深300 今天收盘多少、涨了多少」「这个指数最近几天怎么走的」「指数市值多大」。

## 2. 不适用场景与易混接口

- **与 `index-range-quote` 的区别**：本接口给**逐日明细**（多行）；那个给**区间聚合**（一行/指数）。
- 与 `index-constituents` 的区别：那个是**成分股**；本接口是**指数自身的行情**。
- 与 `index-performance-trend` 的区别：那个给**累计收益率曲线**（用于与基金走势对比），本接口给 OHLC 行情。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `indexCodes` | string[] | **是** | 聚源指数代码（如 `["000300.SH","399006.SZ"]`），**≤ 50 只**；空 / 全为无效券 → 400 |
| `beginDate` | string | 否 | `YYYY-MM-DD`；与 `endDate` **均空 → 最近 7 个交易日** |
| `endDate` | string | 否 | `YYYY-MM-DD`；空 = 不限（与 `beginDate` 至少传一个） |

## 4. 调用示例

```bash
# 不传日期 = 最近 7 个交易日
pixi run etf-htbr invoke index-daily-quote '{"indexCodes":["000300.SH"]}'
# 显式区间
pixi run etf-htbr invoke index-daily-quote '{"indexCodes":["000300.SH"],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（`records[]` 按 `indexCode` 升序、`tradingDay` 降序）：

| 字段 | 含义 |
|---|---|
| `gilcode` | 聚源代码；无记录为 `null` |
| `indexObject` | 指数内码 |
| `indexCode` / `indexName` | 指数代码 / 简称 |
| `tradingDay` | 交易日 |
| `prevClosePrice` | 昨收盘（**点**） |
| `openPrice` / `highPrice` / `lowPrice` / `closePrice` | 开高低收（**点**） |
| `changeOfPrice` | 涨跌（**点**）= 收盘 − 昨收 |
| `changePCT` | 涨跌幅（**%**） |
| `turnoverVolume` | 成交量（**万股**） |
| `turnoverValue` | 成交额（**亿元**） |
| `negotiableMV` | 指数市值（**亿元**），仅部分指数类型提供 |

## 6. 数据口径

- 覆盖 **10 类指数**（A 股 / 境外 / 申万 / 中证 / 上清所 / 概念 / 自编 / 自编债券 / 自编基金 / 中债）；
  同一指数**只命中其中一张表**，不会重复出行。
- `changeOfPrice` 是**点差**（收盘 − 昨收），`changePCT` 才是百分比，**两者不可互换**。
- 成交量单位**万股**、成交额单位**亿元**，已换算；展示直接使用。
- ⚠ **境外指数（`QT_OSIndexQuote` 来源）的成交量未按万股换算**，原样输出，单位存疑。
  引用该字段时须注明「单位待确认」，不要与其它指数的成交量直接比较。
- **中债 / 上清所类指数**不提供开高低与成交量额，对应字段为 `null`（展示为「—」）。
- **概念指数**的昨收由前一交易日收盘回填；回填失败时昨收与涨跌为 `null`。
- 不传日期时默认取**最近 7 个交易日**（不是 7 个自然日）。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `indexCodes` 为空，或超过 50 只 |
| 200 + `NO_DATA` | 全部代码无效（如带 `.` 的未转换券），或区间内无行情 |
| `openPrice` 等为 `null` | 该指数类型不提供（中债 / 上清所） |
| `prevClosePrice` / `changeOfPrice` 为 `null` | 概念指数昨收回填失败 |
| `turnoverVolume` 单位异常 | 境外指数未换算，见第 6 节 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **单次最多 50 只指数**，超出报 400；更多请分批。
- `indexCodes` 需带交易所后缀（与 `index-performance-trend` 要的 6 位净码**不同**）。
- ⚠ **只剥最后一段后缀**：`000300.SH` → `000300`、`000001.ESCI.CZC` → `000001.ESCI`（中间的点属于代码本体，保留），再按 `SecuMain.SecuCode` 匹配。
- ⚠ **本身含点的 `secuCode` 不能直传**：如 `000001.ESCI` 会被再剥一段变成 `000001`，静默返回上证指数行情；这类指数请传 GilCode（`000001.ESCI.CZC`）或纯数字净码，见 `01a-Q事项挂账台账.md` Q-IDX-01。

## 9. 相关工作流

无。
