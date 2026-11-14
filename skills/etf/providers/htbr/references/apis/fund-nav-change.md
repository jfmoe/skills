# fund-nav-change

| 项 | 值 |
|---|---|
| `api_id` | `fund-nav-change` |
| 服务端登记名 | 基金净值变动表 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

返回基金的**净值变动表**（财报附表）：期初 / 期末基金净值、经营活动与份额交易产生的净值变动、申购款、赎回款、分配利润产生的变动。

适用：用户问「这只基金这期期末净值多少」「净值变动是经营活动带来的还是申赎带来的」。

## 2. 不适用场景与易混接口

- **与 `fund-fin-indicator` 的区别**：那个是财务**指标**（比率类）；本接口是净值变动表的**金额科目**。
- 与 `fund-asset-size` 的区别：那个是**份额与规模**（报告期序列）；本接口是**净值变动科目**。
- ⚠ **入参是基金内码**，不是带后缀的 GilCode。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | string[] | **是** | 基金**内码**列表（如 `["2516"]`）；**空数组或不传 → 400** |
| `beginDate` | string | 否 | 起始日（含），`yyyy-MM-dd`；空 = 不限 |
| `endDate` | string | 否 | 截止日（含），`yyyy-MM-dd`；空 = 不限 |

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-nav-change '{"fundObject":["2516"],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（`records[]` 按 `fundCode` 升序、`reportDate` 降序）：

| 字段 | 含义 |
|---|---|
| `fundObject` | 入参内码回显 |
| `fundCode` / `fundName` | 基金代码 / 简称 |
| `reportPeriod` | 报告期文案：`{年份}年报` / `{年份}中报` / `{年份}一季报` / `{年份}三季报`；无法识别时为 `null` |
| `reportDate` | 报告期日期（`yyyy-MM-dd`，即报告期末） |
| `beginFundNetValue` | 期初基金净值 |
| `operateFundNetChange` | 本期**经营活动**产生的基金净值变动数 |
| `shareTradeFundNetChange` | 本期**基金份额交易**产生的基金净值变动数 |
| `subscriptionAmount` | 其中：基金**申购款** |
| `redemptionAmount` | 基金**赎回款** |
| `distributeProfitNetChange` | 本期向份额持有人**分配利润**产生的净值变动数 |
| `endFundNetValue` | 期末基金净值 |

## 6. 数据口径

- 全部金额字段保留 **4 位小数**，单位与基金净值口径一致（元）。
- 报告期由「`EndDate` 年份 + 公告类型」拼成：年报（12-31）、中报（6-30）、一季报（3-31）、三季报（9-30）。
- 公告类型不在上述四类时，`reportPeriod` 为 `null` 但**该行仍保留**（不丢数据），展示时用 `reportDate` 代替。
- ⚠ 与上游存在 **±0.0001 的尾差**（上游为「向上舍入」，本服务为四舍五入）。做精确对账时须容忍这一级差异。
- 同一基金的多个报告期按 `reportDate` **降序**（时间序），不是字符串字典序。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 为空/缺省，或内码类型不合法 |
| 200 + 空列表 | 内码不存在，或该区间无符合条件记录：如实说明，不用其它接口拼凑 |
| `reportPeriod = null` | 公告类型不在四类内（行仍在）；用 `reportDate` 展示 |
| 某金额字段为 `null` | 源值为空，展示为「—」，不要当 0 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- **必须先拿到基金内码**；只有 6 位代码或带后缀代码时，先解析为 `InnerCode`。

## 9. 相关工作流

无。
