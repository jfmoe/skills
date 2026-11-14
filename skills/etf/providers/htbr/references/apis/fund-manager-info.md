# fund-manager-info

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-info` |
| 服务端登记名 | 基金经理基本信息 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询**单个基金经理的档案**：学历、从业年限、在管规模与基金数、历任公司与基金数、当前公司、代表作、背景。

适用：用户问「这位经理什么背景」「从业多久」「管多少钱」。

## 2. 不适用场景与易混接口

- 入参是 **`personalCode`（人员编号）而不是基金代码**。用户只给姓名时必须先走 `fund-manager-resolve`。
- 要**标签/获奖/风格**用 `fund-manager-tag`；要**某只基金的历任经理**用 `fund-manager-history`。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `personalCode` | string | 是 | 人员编号，来自 `fund-manager-resolve` 的 `candidates[].personalCode` |

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-manager-info '{"personalCode":"101014016"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.manager`：

| 字段 | 含义 |
|---|---|
| `chineseName` | 姓名 |
| `education` | 学历 |
| `experienceTime` | 从业年限（**年**） |
| `totalFundNV` | 在管总规模（**亿元，原值即亿**） |
| `numberOfFunds` | 在管基金数 |
| `fundNum` | 历任基金数 |
| `companyNum` | 历任公司数 |
| `investAdvisorAbbrName` | 当前公司 |
| `secuCode` / `secuAbbr` | 代表作 |
| `background` | 背景 |
| `practiceDate` | 证券从业日期 |
| `gender` | 性别 |
| `goodatfundtype` | 擅长类型 |

## 6. 数据口径

- `experienceTime` 单位年，`totalFundNV` **原值即亿元**（不要再除 1e8，与 `fundSize` 的「元」口径不同，勿混用）。
- 仅客观陈述履历事实，**不评价**经理优劣。

## 7. 空数据与异常值语义

- 编号无命中时返回空 `data`，如实说明，不要换编号猜测。
- 字段为 `null` 表示该项无数据，展示为「—」。

## 8. 前置条件与调用限制

- **前置**：`fund-manager-resolve` 已产出 `personalCode`。
- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/manager-name-resolution.md`
