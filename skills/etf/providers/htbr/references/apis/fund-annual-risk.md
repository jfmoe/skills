# fund-annual-risk

| 项 | 值 |
|---|---|
| `api_id` | `fund-annual-risk` |
| 服务端登记名 | 基金年化风险 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金的**年化风险（年化波动率）**（多周期）。

适用：用户问「年化风险多大」「波动率多少」。

## 2. 不适用场景与易混接口

- **这是波动率，不是回撤** —— 回撤走 `fund-max-dd`。
- 要**年化收益**用 `fund-annual-return` —— 一个风险、一个收益，**不要互换**。
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
pixi run etf-htbr invoke fund-annual-risk '{"fundCode":"510300.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.records[]`：

| 字段 | 含义 |
|---|---|
| `endDate` | 指标计算日 |
| `indexCycle` / `indexCycleName` | 周期编号 / 周期名 |
| `dataValue` | 年化风险（**%**） |

## 6. 数据口径

- 源表存的是**周 σ（小数）**，服务端已按 `周σ × √250 × 100` 换算后输出，
  即 `dataValue = 28.63` 表示**年化风险 28.63%**。展示直接加 `%`，**不要再 ×100、也不要再乘 √250**。
- 本接口**不返回** `dataValueRanking` / `rankingRatio`。
- `endDate` 可能落后最新净值日，引用时注明「截至」。
- 指标仅客观陈述，不构成投资建议。

## 7. 空数据与异常值语义

- 代码无命中 → `recordCount=0`、空 records，不报错；先核对 `.OF` 后缀与区间。
- 周期不足时该行缺失，如实说明。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/return-risk-indicators.md`
