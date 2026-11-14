# fund-fin-indicator

| 项 | 值 |
|---|---|
| `api_id` | `fund-fin-indicator` |
| 服务端登记名 | 基金财务指标 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回基金**定期报告口径的财务指标**：本期利润、加权份额利润、期末资产净值、份额净值，以及 REITs 专项字段（经营现金流净额、本期收入、期末份额公允价值参考净值）。

适用：用户问「这只基金这期利润多少」「期末净值多少」「REITs 的经营现金流多少」。

## 2. 不适用场景与易混接口

- **与 `fund-nav-change` 的区别**：那个是净值变动表的**金额科目**；本接口是**财务指标**。
- 与 `fund-asset-size` 的区别：那个是份额与规模序列。
- 与 `fund-nav` 的区别：那个是**逐日单位净值**；本接口的 `nvpershare` 是**报告期末份额净值**。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | integer[] | 是（**空 → 400**） | 基金**内码**列表；不保留隐式缺省 |
| `reportType` | integer[] | 否 | `17` 一季 / `61` 二季 / `23` 三季 / `63` 四季；空/缺省 = 全部 |
| `beginDate` | string | 否 | 起始日（含），`yyyy-MM-dd`；空 = `endDate` **往前 1 年**；格式非法 → 400 |
| `endDate` | string | 否 | 截止日（含），`yyyy-MM-dd`；空 = 今天；格式非法 → 400 |
| `currency` | string | 否 | 币种代码，默认 `CNY` |
| `exchangeRate` | integer | 否 | `1` 最新汇率（该币种最近一条）/ `2` 历史汇率（报告期日及之前最近一条，回溯），默认 `1`；`currency=CNY` 时忽略 |
| `unit` | integer | 否 | `1` 元（默认）/ `2` 千元 / `3` 万元 / `4` 百万元 / `5` 千万元 / `6` 亿元 / `7` 十亿元；非法值兜底万元。**只影响金额字段**（`totalprofit` / `netincome` / `netassetsvalue` / `netoperatecashflow` / `totalrevenue`），不影响 4 个份额类字段 |

## 4. 调用示例

```bash
# 最近一年、按亿元展示
pixi run etf-htbr invoke fund-fin-indicator '{"fundObject":[2516],"unit":6}'
# 只看一季报
pixi run etf-htbr invoke fund-fin-indicator '{"fundObject":[2516],"reportType":[17]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（`records[]` 按 `fundcode` 升序、`enddate` 降序）：

| 字段 | 含义 |
|---|---|
| `fundobject` / `fundcode` / `fundname` / `chiname` | 内码 / 代码 / 简称 / 全称 |
| `enddate` | 报告日期（季度末日） |
| `reporttype` | 第一 / 第二 / 第三 / 第四季度报告 |
| `totalprofit` | 本期利润 |
| `totalprofitpershare` | 加权平均基金份额本期利润 |
| `netincome` | 本期利润扣减公允价值变动损益后的净额 |
| `netincomepershare` | 加权平均份额本期利润扣减公允价值变动净额（**派生字段**） |
| `netassetsvalue` | 期末基金资产净值 |
| `nvpershare` | 期末基金份额资产净值 |
| `netoperatecashflow` | 本期经营活动现金流量净额（**REITs**） |
| `totalrevenue` | 本期收入（**REITs**） |
| `indicativefv` | 期末份额公允价值参考净值（**REITs**，元） |

## 6. 数据口径

- 全部数值字段保留 **4 位小数**。金额字段（`totalprofit` / `netincome` / `netassetsvalue` / `netoperatecashflow` / `totalrevenue`）**已按 `unit` 换算**（`unit=6` 即亿元）；展示直接使用，不要再除。
- **4 个份额/单位类字段不受 `unit` 影响**：`totalprofitpershare` / `netincomepershare` / `nvpershare` / `indicativefv` 恒为每股（每份）原值，`unit=6` 时也**不**除以 1e8。
- **报告期只有四个季度末日**（03-31 / 06-30 / 09-30 / 12-31），非季末记录不返回。
- ⚠ `reportType=61` 的文案是「**第二季度报告**」，即使业务上习惯称"中报"，**回答时沿用该文案**。
- `currency≠CNY` 时按汇率换算（含上述 4 个份额类字段）：`exchangeRate=1` 取该币种**最新一条**汇率（各报告期共用）；`exchangeRate=2` 取**报告期日及之前最近一条**（周末/节假日回溯，非精确匹配）。**汇率行缺失时换算字段为 `null`**（不是 0，也不报错）。
- `totalprofit=0` 时派生字段 `netincomepershare` 为 `null`（避免除零）。
- REITs 三字段对**非 REITs 基金通常为 `null`**，这是语义本身，不是缺数据。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 为空/缺省，或 `currency`/`exchangeRate`/`unit` 非法 |
| 200 + 空列表 | 该内码无财务数据（或币种查不到），如实说明 |
| `netincomepershare = null` | 分母为 0（本期利润为 0），不是缺数据 |
| `indicativefv` / `netoperatecashflow` / `totalrevenue` = `null` | 非 REITs 基金，或该期无此项；如实说明 |
| 金额为 `null` | 汇率缺失或源值为空，展示为「—」 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **必须先拿到基金内码**；只有代码时先解析为 `InnerCode`。

## 9. 相关工作流

无。
