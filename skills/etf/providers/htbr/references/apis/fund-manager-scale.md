# fund-manager-scale

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-scale` |
| 服务端登记名 | 基金经理管理规模 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

按**基金经理**维度返回**管理规模时间序列**：逐报告期给出总管理规模、旗下基金数量、总规模排名，
以及股票型 / 混合型 / 债券型 / 货币型 / QDII / 其他六类各自的规模、数量、排名与**全市场同类均值**。

适用：用户问「某位经理现在管多少钱」「这几年管理规模怎么变的」「在同类经理里规模排第几」
「他的规模比同业平均高还是低」。

## 2. 不适用场景与易混接口

- **与 `fund-manager-info` 的区别**：那个给**档案**（学历、从业年限、在管规模单值、代表作）；
  本接口给**逐报告期规模序列 + 排名 + 全市场均值**。
- **与 `fund-asset-size` 的区别**：那个是**基金产品**的规模序列；本接口是**人**的规模序列（跨其旗下所有基金汇总）。
- **与 `fund-manager-tag` 的区别**：那个给能力/获奖/风格标签，不含规模数字。
- 六类规模由**同一个** `api_id` 的返回列区分，不要当作六个接口。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `personalCodes` | integer[]（兼容单值） | **是** | 基金经理**内码**列表（如 `[101019305]`），支持多位；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |
| `beginDate` | string | 否 | 报告期区间起，`YYYY-MM-DD`；格式非法 → 400 |
| `endDate` | string | 否 | 报告期区间止，`YYYY-MM-DD`；格式非法 → 400；与 `beginDate` 均空 = 由上游缺省区间 |

> `personalCodes` 要的是**经理内码**（long 型人员编号），不是姓名、也不是基金代码。
> 只有姓名时先用 `fund-manager-resolve` 解析出 `candidates[].personalCode` 再调用本接口。

## 4. 调用示例

```bash
# 单经理 + 指定报告期区间
pixi run etf-htbr invoke fund-manager-scale '{"personalCodes":[101019305],"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
# 多经理（对比规模与排名）、不传日期走上游缺省区间
pixi run etf-htbr invoke fund-manager-scale '{"personalCodes":[101019305,101014016]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 经理 × 报告期 |
| `records[].personalcode` / `records[].chinesename` | 经理内码 / 姓名 |
| `records[].reportdate` | 报告期（`YYYY-MM-DD`，季报日） |
| `records[].numberoffunds` | 旗下基金总数（只） |
| `records[].totalfundnv` | 总管理规模（**亿元**） |
| `records[].totalfundnvrank` | 总规模排名（`x/y` 文本，如 `3717/4336`） |
| `records[].totalfundnvavg` | 总规模**全市场同类均值**（亿元） |
| `records[].equityfundnv` / `.equityfundn` / `.equityfundnvrank` / `.equityfundnvavg` | 股票型：规模（亿元）/ 数量（只）/ 排名 / 同类均值（亿元） |
| `records[].hybridfundnv` / `.hybridfundn` / `.hybridfundnvrank` / `.hybridfundnvavg` | 混合型四字段 |
| `records[].bondfundnv` / `.bondfundn` / `.bondfundnvrank` / `.bondfundnvavg` | 债券型四字段 |
| `records[].monetaryfundnv` / `.monetaryfundn` / `.monetaryfundnvrank` / `.monetaryfundnvavg` | 货币型四字段 |
| `records[].qdiinv` / `.qdiin` / `.qdiifundnvrank` / `.qdiinvavg` | QDII 四字段（注意列名与其他类不同） |
| `records[].otherfundnv` / `.otherfundn` / `.otherfundnvrank` / `.otherfundnvavg` | 其他基金四字段 |

## 6. 数据口径

- **单位**：所有 `*nv` / `*nvavg` 均为**亿元**，上游已换算；平台不再换算、不做舍入，直接展示。
- **排名**：`*nvrank` 是源表 `x/y` 形态的**文本**（如 `3717/4336` = 第 3717 名 / 共 4336 人），原样展示，不要自行拆成百分位。
- **同类均值是全市场均值**：同一报告期内所有经理的 `*nvavg` 相同（分母为该期有记录的经理数），
  因此「经理规模 vs 均值」可直接横向比较；不要把它误读成该经理的历史平均。
- **一行 = 经理 × 报告期**：经理某报告期无记录时该期**不出行**（不补 0）；向上取报告期序列时注意可能存在空档。
- **空值**：经理无某类资产时，该类规模/数量/均值为 `null`、排名字段为**空字符串** `""` —— 展示为「无」或「—」，不要当 0 参与计算。
- 报告期为季报日（0331 / 0630 / 0930 / 1231）。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `personalCodes` 缺失/空/非内码，日期格式非法 —— 补齐/纠正参数 |
| 200 + `NO_DATA` 注记 | 经理内码无法解析，或区间内无报告期 —— 如实说明无数据 |
| `*nv = null` + `*nvrank = ""` | 该期没有该类资产，不是缺数据 |
| `totalfundnv = 0`（真 0，非 null） | 该期规模确为 0，与「无该类资产」的 `null` 语义不同，勿混用 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `personalCodes` 必须是**经理内码**；只有姓名先走 `fund-manager-resolve`。
- 支持多经理批量（一次传多个内码），按「经理 → 报告期」逐行返回。

## 9. 相关工作流

- 只有经理姓名、没有内码 → 先读 `workflows/manager-name-resolution.md`，用 `fund-manager-resolve` 取 `personalCode`。
- 还想看经理档案 / 标签 → `fund-manager-info` / `fund-manager-tag`。
