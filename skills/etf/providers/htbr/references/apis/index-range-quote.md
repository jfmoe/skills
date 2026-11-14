# index-range-quote

| 项 | 值 |
|---|---|
| `api_id` | `index-range-quote` |
| 服务端登记名 | 指数区间行情 |
| 领域 | index |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回**指数在给定区间内的行情聚合**（每指数一行）：区间开高低收、区间最高/最低收盘、区间涨跌与涨跌幅、区间成交量额与日均量额。

适用：用户问「沪深300 这个月涨了多少」「这段时间最高到过多少点」「区间日均成交额多少」。

## 2. 不适用场景与易混接口

- **与 `index-daily-quote` 的区别**：那个给**逐日明细**；本接口给**区间聚合**（一行/指数）。
- 与 `index-performance-trend` 的区别：那个给**累计收益率曲线**；本接口给行情聚合（点数口径）。
- ⚠ **实时行情不支持**：请求中带实时行情字段会直接 **400**（本期后置）。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `indexCodes` | string[] | **是** | 聚源指数代码，**≤ 50 只**；空 / 全无效 → 400 |
| `beginDate` | string | 否 | `YYYY-MM-DD`；与 `endDate` **均空 → 近 1 个月同日** |
| `endDate` | string | 否 | `YYYY-MM-DD`；空 = 不限 |

> 实时行情入参（`liveQuoteData`）**本期不开放**，传入即 400。

## 4. 调用示例

```bash
# 不传日期 = 近 1 个月
pixi run etf-htbr invoke index-range-quote '{"indexCodes":["000300.SH"]}'
# 显式区间
pixi run etf-htbr invoke index-range-quote '{"indexCodes":["000300.SH"],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（**每指数一行**，`records[]` 按 `indexCode` 升序）：

| 字段 | 含义 |
|---|---|
| `gilcode` / `indexObject` | 聚源代码 / 指数内码 |
| `indexCode` / `indexName` | 指数代码 / 简称 |
| `beginDate` / `endDate` | 区间**首个 / 最后一个行情日**（实际值，非请求值） |
| `tradeDays` | 区间交易日天数 |
| `openPriceBT` | 区间开盘（首日开盘，**点**） |
| `highPriceBT` / `lowPriceBT` | 区间最高 / 最低价（**点**） |
| `closePriceBT` | 区间收盘（末日收盘，**点**） |
| `highestClosePriceBT` / `lowestClosePriceBT` | 区间最高 / 最低**收盘**价（**点**） |
| `rangePCTBT` | 区间涨跌（**点差，不是百分比**） |
| `changePCTBT` | 区间涨跌幅（**%**） |
| `turnoverVolumeBT` | 区间成交量（**万股**） |
| `turnoverValueBT` | 区间成交额（**亿元**） |
| `turnoverVolumePerDayBT` | 区间日均成交量（**万股**） |
| `turnoverValuePerDayBT` | 区间日均成交额（**亿元**） |

## 6. 数据口径

- ⚠ **`rangePCTBT` 是点差不是百分比**（字段名有历史歧义）：4000 收 vs 3900 昨收 → `100.00`。
  百分比看 `changePCTBT`（= 区间涨跌 ÷ 首日昨收 × 100）。**这两个字段绝不能混用。**
- `rangePCTBT` = 末日收盘 − **首日昨收**；首日昨收可能对应 **早于 `beginDate` 一个交易日**的收盘，属正常。
- `beginDate` / `endDate` 返回的是**实际有行情的首末日**，可能窄于请求区间。
- 覆盖 10 类指数，同一指数**只出一行**（不会因多表命中而重复）。
- **中债 / 上清所类指数**不提供开高低、成交量额与日均值，对应字段为 `null`。
- ⚠ **境外指数的区间成交量未按万股换算**（原样输出），单位存疑；引用时注明「单位待确认」。
- 日均值 = 区间量额 ÷ `tradeDays`。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `indexCodes` 为空/超 50 只，或传了实时行情字段 |
| 200 + `NO_DATA` | 区间内无任何行情，如实说明 |
| `openPriceBT` 等为 `null` | 该指数类型不提供该项（中债 / 上清所） |
| `tradeDays` 小于区间自然日数 | 正常，按交易日计 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **单次最多 50 只指数**。
- 实时行情（当日未收盘的实时数据）本期不支持，只能查历史区间。
- ⚠ **只剥最后一段后缀**：`000300.SH` → `000300`、`000001.ESCI.CZC` → `000001.ESCI`（中间的点属于代码本体，保留），再按 `SecuMain.SecuCode` 匹配。
- ⚠ **本身含点的 `secuCode` 不能直传**：如 `000001.ESCI` 会被再剥一段变成 `000001`，静默返回上证指数行情；这类指数请传 GilCode（`000001.ESCI.CZC`）或纯数字净码，见 `01a-Q事项挂账台账.md` Q-IDX-01。

## 9. 相关工作流

无。
