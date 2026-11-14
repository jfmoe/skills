# fund-return-risk

| 项 | 值 |
|---|---|
| `api_id` | `fund-return-risk` |
| 服务端登记名 | 基金收益风险指标 |
| 领域 | fund |
| 资料完整度 | 完整（请求/响应、7 指标周期差异与空值语义均线上实测，2026-11-05） |

## 1. 功能与适用场景

一次返回**基金收益/风险指标长表**：一行 = 一只基金 × 一个指标 × 一个周期 × 一个计算日，含指标值、同类排名与二级分类。

7 个指标：`ReturnSum`（区间累计收益）、`MaxDD`（最大回撤）、`Sharpe`（夏普比率）、`Calmar`（卡玛比率）、`Info`（信息比率）、`AnnualReturn`（年化收益）、`AnnualRisk`（年化波动率）。

适用：用户问「这只基金近一年收益多少、同类排第几」「近三年最大回撤多大、夏普多少」「几只基金的卡玛/信息比率对比」「成立以来年化收益与波动率」。

## 2. 不适用场景与易混接口

- 与 `index-return-risk` 的区别：那个主体是**指数**，本接口主体是**基金**。
- 与 `fund-drawdown` 的区别：那个返回**逐日回撤序列**（可画曲线）；本接口只给 `MaxDD` 的多周期**幅度值**，不含回撤起止日。
- 与 `fund-nav` / `fund-nav-trend` 的区别：那两个是**净值/走势**；本接口是统计后的指标值，不返回净值。
- 与 `fund-period-return` / `fund-stage-performance` 的区别：那两个是**单指标/固定区间收益**；本接口是多指标、多周期、带排名的长表。
- 与下方 7 个单指标接口（`fund-return-sum`/`fund-max-dd`/`fund-sharpe`/`fund-calmar`/`fund-info-ratio`/`fund-annual-return`/`fund-annual-risk`）的区别：本接口**一次覆盖全部 7 个指标**且走 dataservice 通道；那 7 个按单指标拆分、当前**暂停保留**，不要混用入参口径。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `innerCodes` | integer[]（兼容单值） | 与 `secuCodes` 二选一 | 基金**内码**，正整数；**禁止 `0`**（`0` 在 DS 表示全市场，会拉 20 万+ 行）；别名 `fundObject` |
| `secuCodes` | string[]（兼容单值） | 与 `innerCodes` 二选一 | **6 位基金代码**（字符串、保留前导 0，如 `"510050"`）；服务端内部转内码，零命中 404、多命中 409；别名 `secuCode` |
| `indices` | string[]（兼容单值） | 否 | 指标标识，**只认英文代码**（见 3.1）；不传 = 7 个全返；显式空列表或未知代码 → 400 |
| `indexCycle` | integer[]（兼容单值） | 否 | 周期编码（见 3.2）；不传 = 不按周期过滤；显式空列表或表外编码 → 400 |
| `beginDate` | string | 否 | `yyyy-MM-dd`，严格日历校验；**只过滤结果行 `endDate`**，不是回看窗口起点 |
| `endDate` | string | 否 | `yyyy-MM-dd`，同上；`endDate < beginDate` → 400 |

合并去重后内码总数 **0 → 400**、**> 200 → 400**；**不暴露分页参数**。

### 3.1 `indices` 值=含义速查表（本节为唯一权威，传**英文代码**）

| 代码 | 中文名 | 说明 |
|---|---|---|
| `ReturnSum` | 区间累计收益 | 11 个周期（含 7 天） |
| `MaxDD` | 最大回撤 | 10 个周期（无 7 天） |
| `Sharpe` | 夏普比率 | 10 个周期（无 7 天） |
| `Calmar` | 卡玛比率 | **8 个周期**（无 1 天/7 天/998） |
| `Info` | 信息比率 | 10 个周期（无 7 天） |
| `AnnualReturn` | 年化收益 | 11 个周期（含 7 天）；1/3/6/7/12/998 周期值可为 `null` |
| `AnnualRisk` | 年化波动率 | 10 个周期（无 7 天） |

> **默认值**：不传 `indices` = 7 个指标全部返回（等价于显式列出上表 7 个代码）；显式空列表 → 400。

> ⚠ 大小写敏感：传 `"sharpe"` 或中文名都会 400 `PARAM_INVALID`（不是静默 0 行）。

### 3.2 `indexCycle` 编码值=含义速查表（本节为唯一权威）

| 编码 | 含义 | 编码 | 含义 |
|---:|---|---:|---|
| `1` | 一个月 | `36` | 三年 |
| `3` | 三个月 | `60` | 五年 |
| `6` | 六个月 | `120` | 十年 |
| `7` | 七天 | `998` | 今年以来 |
| `12` | 一年 | `999` | 成立以来 |
| `24` | 两年 |  |  |

> **默认值**：不传 `indexCycle` = 不按周期过滤（返回各指标的全部周期档）；显式空列表 → 400。

> ⚠ 7 天只有 `ReturnSum`/`AnnualReturn` 有；`Calmar` **没有** 1、7、998。请求了某指标不存在的周期不会报错，只是该组合无行。

## 4. 调用示例

```bash
# 单基金全 7 指标（2997 = 510050）
pixi run etf-htbr invoke fund-return-risk '{"innerCodes":[2997]}'

# 按代码 + 指定指标 + 周期并集（取值见 3.1 / 3.2 速查表）
pixi run etf-htbr invoke fund-return-risk '{"secuCodes":["510050"],"indices":["ReturnSum","Sharpe","Calmar"],"indexCycle":[1,3,120]}'

# 多基金对比（注意行数 = 基金数 × 指标数 × 周期数）
pixi run etf-htbr invoke fund-return-risk '{"innerCodes":[2997,2516],"indices":["AnnualReturn","AnnualRisk"]}'

# 区间按计算日过滤（只筛结果行 endDate）
pixi run etf-htbr invoke fund-return-risk '{"innerCodes":[2997],"indices":["Sharpe"],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`（`recordCount` + `records[]`，**长表**；保持 DS 返回顺序）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `secuCode` | string | 基金代码（6 位，保留前导 0） |
| `secuAbbr` | string | 基金简称 |
| `endDate` | string | **计算日**（`yyyy-MM-dd`，各基金取自己最新计算日） |
| `indexType` | string | 指标英文代码（与入参 `indices` 同一套） |
| `indexTypeName` | string | 指标中文名 |
| `indexCycle` | integer | 周期编码 |
| `indexCycleName` | string | 周期中文名（如「一个月」「成立以来」） |
| `dataValue` | number \| null | 指标值（量纲随指标，见 6） |
| `dataValueRanking` | string \| null | 排名字符串（形如 `"1668/5639"`，名次/样本数） |
| `dataValueRankingNum` | number \| null | 参与排名样本数 |
| `dataValueRankingAvg` | number \| null | 排名均值（**量纲与 `dataValue` 不同**，原值透出） |
| `rankingRatio` | number \| null | 排名分位/比率 |
| `secAssetCatName` | string \| null | 二级分类名称 |

## 6. 数据口径

- **长表不是宽表**：同一基金的 7 个指标 × 多个周期分散在多行；按 `indexType` + `indexCycle` 取用，不要跨周期直接比较。
- **计算日按基金各自最新**：`endDate` 不保证统一 T-1（全量实测存在 2026-10-27~11-04 多个日期）；`beginDate`/`endDate` 过滤的是结果行 `endDate`，不是「回看窗口」。
- **量纲随指标**：
  - `ReturnSum`/`AnnualReturn`/`MaxDD`/`AnnualRisk` 为**百分数**（展示加 `%`）；
  - `Sharpe`/`Calmar`/`Info` 为**倍数**（不加 `%`）。
  - `dataValueRankingAvg` 的量纲与 `dataValue` 不同（上游排名均值口径），平台**原值直出、不做换算**。
- **精度原样透出**：平台不做二次 round；`Sharpe` 等多数为 2 位小数，也存在 0.006 级值。
- **排名字段**：`dataValueRanking` 是字符串 `名次/样本数`，平台不拆成两列；排序方向按上游（名次越小越靠前）。
- 平台不重排、不透视返回顺序。

## 7. 空数据、`null`、异常值与哨兵值

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | 内码/代码全空；内码 0 或非正整数；`secuCodes` 非 6 位数字；合并 >200；`indices` 显式空/未知；`indexCycle` 显式空/表外；日期非法或 end<begin |
| 404 `FUND_NOT_FOUND` / 409 `FUND_AMBIGUOUS` | `secuCodes` 无法解析为唯一内码 |
| **200 + `recordCount=0`** + `W202_NO_DATA` | 参数无误但该基金/区间无记录——**不是错误**；样本 `22163`（000013）在 `Sharpe`/`Calmar`/`Info`/`AnnualRisk` 上 0 行属正常（其 `ReturnSum`/`MaxDD`/`AnnualReturn` 仍有 32 行）。这是**该基金未被本报表圈定**的结果，不是「货币型整体排除」规则（全量中仍有货币型基金返回 Sharpe 行），不得按品类硬编码 |
| 503 `DEGRADED` | DS 取数运行时失败（超时/网络异常/报表业务失败）；无降级数据，可稍后重试或告知用户数据暂不可用 |
| `dataValue = null` | `AnnualReturn` 在 1/3/6/7/12/998 周期可为空（样本 2997 有 6 行 null）；保留 null，展示「—」，**不补 0** |
| `dataValueRanking = null` | 该指标/周期未参与排名，展示「—」 |

## 8. 前置条件与调用限制

- 需已配置平台凭证、网关可达；服务端登记为 `AVAILABLE` 且 `X-Skill-Id: htbr-etf-skill`。
- 只有基金名称/代码时：可直接传 `secuCodes`（6 位代码），由服务端内部转内码；也可先按 `fund-resolve` 取内码再传 `innerCodes`（见 `workflows/fund-code-resolution.md`）。
- **批量上限**：单次合并内码 ≤ 200；**不暴露分页参数**。
- **行数与耗时**：行数 ≈ 基金数 × 指标数 × 周期档数（单基金 7 指标约 70 行）；不要传 `0`（全市场 20 万+ 行）。
- 不传 `indices`/`indexCycle` 会返回 7 指标 × 全周期，行数最多；批量对比时建议至少收窄 `indices`。

## 9. 相关工作流

- `workflows/fund-code-resolution.md`：只有基金名称或非目标代码时，先 `fund-resolve` 取内码。
- `workflows/return-risk-indicators.md`：描述的是 7 个**单指标线下接口**（`fundCode` 带 `.OF` 后缀）的入参口径，**不适用于本接口**；本接口用 `innerCodes`/`secuCodes`，不要按该 workflow 的 `fundCode` 形态调用。
