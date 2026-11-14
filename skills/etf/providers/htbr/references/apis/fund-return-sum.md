# fund-return-sum

| 项 | 值 |
|---|---|
| `api_id` | `fund-return-sum` |
| 服务端登记名 | 基金区间累计收益 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金在**多个周期**上的**区间累计收益率**及其**排名分位**。

适用：用户问「近三年累计收益多少」「收益在同类里排什么位置」。

## 2. 不适用场景与易混接口

- 要**固定区间枚举 + 同类均值/排名**（近一周…成立来）用 `fund-stage-performance`，本接口周期集不同。
- 逐月/逐季/逐年明细用 `fund-monthly/quarterly/yearly-return`。
- 本接口与另外 6 个风险指标（`fund-max-dd` / `fund-sharpe` / `fund-calmar` / `fund-info-ratio` / `fund-annual-return` / `fund-annual-risk`）
  **共享同一套入参口径**，见 `references/workflows/return-risk-indicators.md`。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `fundCode` | string | 是 | **带市场后缀的 GilCode，一律用 `.OF`**（含场内 ETF：`510300.OF` 可用） |
| `beginDate` | string | **是（实务上必须传）** | `yyyy-MM-dd`，**只过滤计算日**，不是统计窗口 |
| `endDate` | string | **是（实务上必须传）** | `yyyy-MM-dd` |

> ⚠ `.SH` / `.SZ` 曾观察到静默返回 `recordCount=0`。先核对原始代码与精确映射，不得因空结果自行替换为 `.OF`；代码转换见 `references/workflows/fund-code-resolution.md`。
> ⚠ 不传日期或区间过宽会导致接口长时间不返回（实测 >240s 超时）；**默认按「近一年到今天」传**。
> 完整口径（含为什么日期不影响周期）见 workflow。

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-return-sum '{"fundCode":"510300.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.records[]`，**同基金多周期多行**：

| 字段 | 含义 |
|---|---|
| `endDate` | 指标计算日 |
| `indexCycle` / `indexCycleName` | 周期编号 / 周期名 |
| `dataValue` | 区间累计收益（**%**） |
| `dataValueRanking` | 「名次/总数」文本；**部分周期为 `null`** |
| `rankingRatio` | 分位（**%**，**越低越靠前**）；部分周期为 `null` |

## 6. 数据口径

- `dataValue` 是**百分数**，直接加 `%`，不要再 ×100。
- 本接口与 `fund-max-dd` 是仅有的两个返回 `dataValueRanking` / `rankingRatio` 的接口。
- `endDate` 是**指标计算日**，可能落后最新净值日数天，引用时按 `endDate` 注明「截至」。
- 指标仅客观陈述，**不构成投资建议**。

## 7. 空数据与异常值语义

- 代码无命中 → `recordCount=0`、空 records，**不报错**；先核对 `.OF` 后缀与区间。
- 传入与计算日无交集的区间（如 2020 年）同样返回空，属正常语义不是故障。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/return-risk-indicators.md` —— **必读**，7 个指标共享的入参口径与周期集。
