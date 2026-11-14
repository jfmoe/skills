# fund-max-dd

| 项 | 值 |
|---|---|
| `api_id` | `fund-max-dd` |
| 服务端登记名 | 基金最大回撤 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金的**最大回撤幅度**（多周期）。

适用：用户问「最大回撤多少」「历史上最多亏了多少」。

## 2. 不适用场景与易混接口

- **只给回撤幅度，不给回撤起止日**。用户问「回撤最大的那段时间是什么时候」时，本接口答不了 ——
  需按 `references/workflows/return-risk-indicators.md` 的「自算回撤区间」一节用 `fund-nav-trend` 复算。
- 要**年化风险（波动率）**用 `fund-annual-risk`，那是另一个指标。
- 同族共享入参口径，见 workflow。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `fundCode` | string | 是 | **带市场后缀的 GilCode，一律用 `.OF`** |
| `beginDate` | string | **是（实务上必须传）** | 只过滤计算日（`yyyy-MM-dd`），不是统计窗口；格式非法 → 400 |
| `endDate` | string | **是（实务上必须传）** | `yyyy-MM-dd` |

> ⚠ 后缀 `.SH`/`.SZ` 静默返回 0 行；日期不传或区间过宽会超时。**默认按「近一年到今天」传**。

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-max-dd '{"fundCode":"510300.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.records[]`：

| 字段 | 含义 |
|---|---|
| `endDate` | 指标计算日 |
| `indexCycle` / `indexCycleName` | 周期编号 / 周期名 |
| `dataValue` | 最大回撤幅度（**%**，**实测为正数**） |
| `dataValueRanking` | 「名次/总数」文本；部分周期为 `null` |
| `rankingRatio` | 分位（**%**，越低越靠前）；部分周期为 `null` |

## 6. 数据口径

- ⚠ **`dataValue` 实测为正数**：`510300.OF` 近一年/三年/五年返回 `11.17 / 15.32 / 35.16`，
  与用复权净值链自算的 `-11.17% / -15.32% / -35.16%` 逐一对齐。
  **展示时写「最大回撤 35.16%」，不要加负号**（回撤本身就是下跌幅度，负数反而造成歧义）。
- `endDate` 可能落后最新净值日，引用时注明「截至」。
- 指标仅客观陈述，不构成投资建议。

## 7. 空数据与异常值语义

- 代码无命中 → `recordCount=0`、空 records，不报错；先核对 `.OF` 后缀与区间。
- 无回撤区间（如区间内单调上涨）时该周期可能缺行或为 0，如实说明。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/return-risk-indicators.md` —— 共享入参口径 **+ 回撤起止日自算法**。
