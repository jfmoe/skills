# fund-sharpe

| 项 | 值 |
|---|---|
| `api_id` | `fund-sharpe` |
| 服务端登记名 | 基金夏普比率 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金的**夏普比率**（多周期）。

适用：用户问「夏普比率多少」「风险调整后收益怎么样」。

## 2. 不适用场景与易混接口

- 同族的**卡玛比率**走 `fund-calmar`、**信息比率**走 `fund-info-ratio`，三个都是风险调整类指标但口径不同，**不要互相替代**。
- 要**波动率**用 `fund-annual-risk`；要**回撤**用 `fund-max-dd`。
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
pixi run etf-htbr invoke fund-sharpe '{"fundCode":"510300.OF","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.records[]`：

| 字段 | 含义 |
|---|---|
| `endDate` | 指标计算日 |
| `indexCycle` / `indexCycleName` | 周期编号 / 周期名 |
| `dataValue` | 夏普比率（**无量纲**） |

## 6. 数据口径

- `dataValue` **无量纲**（不是百分数），**不要加 `%`**。
- 本接口**不返回** `dataValueRanking` / `rankingRatio`（只有 `fund-return-sum` 与 `fund-max-dd` 返回）。
- `endDate` 可能落后最新净值日，引用时注明「截至」。
- 指标仅客观陈述，不构成投资建议。

## 7. 空数据与异常值语义

- 代码无命中 → `recordCount=0`、空 records，不报错；先核对 `.OF` 后缀与区间。
- 周期不足或无足够数据时该行缺失，如实说明。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/return-risk-indicators.md`
