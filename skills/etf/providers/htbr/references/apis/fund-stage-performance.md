# fund-stage-performance

| 项 | 值 |
|---|---|
| `api_id` | `fund-stage-performance` |
| 服务端登记名 | 阶段业绩表现 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金在**固定区间**上的业绩表现：区间收益率、**同类均值与同类排名**、业绩比较基准收益率。

适用：用户问「近一年收益多少」「同类排名第几」「跑赢基准了吗（区间口径）」。

## 2. 不适用场景与易混接口

- 与 `fund-return-sum` 的区别：本接口是**固定区间枚举**（近一周…成立来）且**带同类排名**；
  `fund-return-sum` 是**多周期累计**（3/6/12/24/36/60/120 月 + 今年来 + 成立来）。
  用户问「同类里排第几」优先本接口；问「近三年累计收益/收益分位」用 `fund-return-sum`。
- 逐月/逐季/逐年明细走 `fund-monthly-return` / `fund-quarterly-return` / `fund-yearly-return`。
- 要比指数走势用 `index-performance-trend`，本接口的 `benchGR` 是**业绩比较基准**不是指数。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `fundCode` | string | 是 | 6 位基金代码 |

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-stage-performance '{"fundCode":"510300"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.stages[]`，**每行一个固定区间**：

| 字段 | 含义 |
|---|---|
| `durationName` | 区间名：近一周 / 近一月 / 近三月 / 近六月 / 近一年 / 近两年 / 近三年 / 近五年 / 今年来 / 成立来 |
| `fundReturn` | 该基金区间收益率（**%**） |
| `fundReturnMean` | 同类均值（**%**） |
| `fundReturnRank` | 同类排名；**「成立来」恒为 `null`** |
| `benchGR` | 业绩比较基准收益率（**%**） |

## 6. 数据口径

- `fundReturn` / `fundReturnMean` / `benchGR` 均为**百分数**，直接加 `%`，**不要再 ×100**。
- 「成立来」区间无同类排名（`fundReturnRank` 为 `null`），展示为「—」，不要填 0。
- 历史业绩**仅客观陈述**，不代表未来表现。

## 7. 空数据与异常值语义

- 区间不足（如成立未满一年）时对应行可能缺失或为 `null`，如实说明该区间暂无数据。
- 代码不可解析 → 404 `FUND_NOT_FOUND`。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

无。
