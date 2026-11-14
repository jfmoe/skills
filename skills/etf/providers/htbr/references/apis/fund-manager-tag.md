# fund-manager-tag

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-tag` |
| 服务端登记名 | 基金经理标签 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金经理的**标签**：能力标签（如明星基金经理、赚钱能力、回撤控制能力、价值成长风格）、获奖标签、年限合成行。

适用：用户问「这位经理什么风格」「获过什么奖」「管理多少年了（标签口径）」。

## 2. 不适用场景与易混接口

- 档案类信息（学历、在管规模、历任公司数）走 `fund-manager-info`，本接口只给标签体系。
- 入参是 `personalCodes`（**数组**，可批量），不是基金代码。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `personalCodes` | string[] | 是 | 人员编号数组，**上限 50** |

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-manager-tag '{"personalCodes":["101014016"]}'
```

## 5. 返回数据路径与关键字段

读 `$.data.tags[]`：

| 字段 | 含义 |
|---|---|
| `tagName` | 标签类型（如 明星基金经理 / 赚钱能力 / 回撤控制能力 / 价值成长风格） |
| `managerTagName` | 具体标签名，**含获奖标签**与「投资管理N.N年」「从业N.N年」**年限合成行** |
| `startDate` | 标签生效日期 |
| `tagCode` | 年限行的 `tagCode` 为 `9990` / `9991` |

## 6. 数据口径

- 年限合成行（`tagCode` = 9990/9991）是**标签体系派生**出来的表述，与 `fund-manager-info` 的 `experienceTime` 数值口径可能不完全一致，勿混用或互相校验。
- 标签是**客观事实陈述**，不得据此给出投资建议。

## 7. 空数据与异常值语义

- HTTP 200 + 空数组 = 该经理无标签记录，如实说明。
- 批量入参超过 50 会被拒绝，需分批。

## 8. 前置条件与调用限制

- **前置**：`fund-manager-resolve` 已产出 `personalCode`。
- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/manager-name-resolution.md`
