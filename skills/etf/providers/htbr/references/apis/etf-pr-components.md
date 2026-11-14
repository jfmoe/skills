# etf-pr-components

| 项 | 值 |
|---|---|
| `api_id` | `etf-pr-components` |
| 服务端登记名 | ETF申购赎回成分股信息 |
| 领域 | etf |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回 ETF **最新申购赎回清单（PCF）**的**成分股明细**：成分代码/名称、收盘价、涨跌幅、市值占比与排名、成分申购数量、现金替代标志与比例、各类替代金额。

适用：用户问「这只 ETF 的申赎清单里有哪些股票」「某成分占多少权重」「现金替代比例多少」。

## 2. 不适用场景与易混接口

- **与 `etf-pr-list` 的区别**：那个是**申赎要素卡片**（一行一只 ETF，含成分股"数量"）；本接口是**成分股逐行明细**。
- **与 `index-constituents` 的区别**：那个是**指数**成分股（非申赎口径）；本接口是**ETF 申赎清单**成分股。
- 只返回**最新清单日**，不支持历史清单。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | string[] | **是** | ETF 聚源**内码**列表；空 → 400；含非数字 → 400 |

## 4. 调用示例

```bash
pixi run etf-htbr invoke etf-pr-components '{"fundObject":["668474"]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（每只 ETF 的**全部成分股**各一行）：

| 字段 | 含义 |
|---|---|
| `fundObject` / `fundCode` / `fundName` / `chiName` | 基金内码 / 代码 / 简称 / 全称 |
| `tradingDay` | 该基金**自身最新**清单交易日 |
| `serialNumber` | 组内序号（按市值占比降序、成分代码升序，从 1 起） |
| `secuInnerCode` | 成分股内码 |
| `constituentSecuCode` / `constituentSecuAbbr` | 成分股代码 / 名称 |
| `closePrice` | 收盘价（DS 前一交易日口径：A 股/科创板含清单日截断，港股/美股取清单日前最大行情日），4 位小数；无行情为 `null` |
| `changePct` | 涨跌幅（**%**），4 位小数 |
| `marketValueRatio` | 市值占比（**%**），4 位小数；无行情行按 0，仅整组总市值为 0 时 `null` |
| `stockAmount` | 成分申购数量（整数） |
| `cashSubstituteSignDescrip` | 现金替代标志 |
| `applyCashPremiumRate` | 申购现金替代溢价比例（**%**，已 ×100） |
| `redeemCashDiscountRate` | 赎回现金替代溢价比例（**%**，已 ×100） |
| `fixedSubstituteSum` | 固定替代金额（**元**） |
| `applySubstituteSum` | 申购替代金额（**元**） |
| `redeemSubstituteSum` | 赎回替代金额（**元**） |

## 6. 数据口径

- ⚠ **收盘价 / 涨跌幅取 DS「前一交易日」行情**（不是清单当日）。A 股 / 科创板另有截断口径：清单日晚于该成份对应行情表最大日时，取最大行情日的前一天；港股/美股取清单日前最大行情日。
- 行情来源按「行是否存在」整行选取：A 股 → 科创板（688xxx）→ 港股 → 美股；四级都取不到时 `closePrice` / `changePct` 为 `null`。
- `changePct = (close − prevClose) / prevClose × 100`；`prevClose` 为空或为 0 → `null`。
- `marketValueRatio`：行市值 = `closePrice × stockAmount`；**无有效收盘价的行市值按 0 计入**。若组内其他行有有效行情，该行占比为 **0.0000**；仅整组总市值为 0 时占比为 `null`（不会出现 NaN/Infinity），此时序号仍按成分代码升序正常赋 1..n。
- `applyCashPremiumRate` / `redeemCashDiscountRate` 已由小数换算为**百分数**，直接加 `%`。
- 每只基金取**自身最新清单日**，多只基金的 `tradingDay` 可不同。
- 数值舍入口径与上游一致（HALF_UP，4 位小数）。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 为空或含非数字 |
| 200 + 空列表 | 该内码无成分股数据（该基金不占行） |
| `closePrice = null` | 四级行情均无该成分的前一交易日记录 |
| `changePct = null` | 前收为空或为 0 |
| `marketValueRatio = null` | 整组总市值为 0（全部成分无有效收盘价）；个别成分无行情时占比为 0.0000 |
| `serialNumber` | 始终为组内 1..n；占比为 `null` 时按成分代码升序赋号 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **必须先拿到 ETF 内码**；只有代码时先解析为 `InnerCode`。
- 跨境 ETF 的多市场成分股会**全市场参与占比归一**（不分市场单独归一）。

## 9. 相关工作流

无。
