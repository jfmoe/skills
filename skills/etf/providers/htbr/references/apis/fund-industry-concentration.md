# fund-industry-concentration

| 项 | 值 |
|---|---|
| `api_id` | `fund-industry-concentration` |
| 服务端登记名 | 行业集中度 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金**前 1~5 大行业的累计占比**，用于判断持仓的行业集中 / 分散程度。

适用：用户问「这只基金行业集中不集中」「前五大行业占了多少」「重仓押在几个行业上」。

## 2. 不适用场景与易混接口

- **与 `fund-industry-dist` 的区别**：那个给**逐行业明细**（每行业一行、带行业名与占比）；本接口给**Top1~Top5 累计值**（一个报告期一行），不解出行业名称清单。
- **与 `fund-holding-detail` 的区别**：那个是逐**个股**持仓与占比变动。
- 两种口径（净值占比 / 市值占比）由 `proportionType` 区分，不是两个接口。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | integer[]（兼容单值） | **是** | 基金**内码**列表（如 `[2997]`），支持多只；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |
| `beginDate` | string | 否 | 报告期区间起，`YYYY-MM-DD`；格式非法 → 400 |
| `endDate` | string | 否 | 报告期区间止，`YYYY-MM-DD`；格式非法 → 400；与 `beginDate` 均空 = 由上游缺省 |
| `proportionType` | integer | 否 | 占比类别：`0` 持仓市值占**资产净值**比 / `1` 持仓市值占**资产市值**比；空 = 上游缺省 |
| `poscharacter` | integer | 否 | 持仓类型：`1` 重仓股票 / `2` 全部持股；空 = 上游缺省 |
| `industryType` | integer | 否 | 行业分类标准：`38` 申万一级 / `37` 中信一级 / `22` 证监会一级 / `6` 聚源行业(旧) / `16` MSCI / `17` 聚源全球分类B / `100` 恒生；空 = 上游缺省 |

> `fundObject` 要的是**内码**，不是 6 位代码、也不是带 `.OF` 的 GilCode。只有名称/代码时先用
> `fund-resolve` 解析，取 `candidates[].innerCode` 再调用本接口。

## 4. 调用示例

```bash
# 单只基金 + 申万一级 + 重仓股票 + 净值占比
pixi run etf-htbr invoke fund-industry-concentration '{"fundObject":[2997],"poscharacter":1,"industryType":38,"proportionType":0}'
# 多只基金、全部持股、看市值占比、限定报告期区间
pixi run etf-htbr invoke fund-industry-concentration '{"fundObject":[2997,2998],"poscharacter":2,"proportionType":1,"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 基金 × 报告期 |
| `records[].fundcode` / `records[].fundname` | 基金代码 / 简称 |
| `records[].fundobject` | 基金内码 |
| `records[].enddate` | 报告期（`YYYY-MM-DD`） |
| `records[].poscharacter` | 持仓类型**中文描述**（如「重仓股票」） |
| `records[].industrytype` | 行业分类标准**中文描述**（如「申万行业分类(一级)」） |
| `records[].proportiontype` | 占比类别**中文描述**（如「持仓市值占资产净值比」） |
| `records[].toponesumratio` | 最大重仓占比（**%**） |
| `records[].toptwosumratio` | 前二大累计占比（**%**） |
| `records[].topthreesumratio` | 前三大累计占比（**%**） |
| `records[].topfoursumratio` | 前四大累计占比（**%**） |
| `records[].topfivesumratio` | 前五大累计占比（**%**） |

## 6. 数据口径

- 五个 `topNsumratio` 是**累计值**，天然满足 `top1 ≤ top2 ≤ top3 ≤ top4 ≤ top5`（单调不减），不是各行业单独占比。
- **不足 5 个行业时**，低名次复用当前最大值（沿用上游口径），可能出现 Top4 = Top5 的相等值，属正常行为。
- 单位是**百分数**，上游已换算；平台不再 ×100、不做舍入，直接展示。
- `poscharacter` / `industrytype` / `proportiontype` 三列回显的是**中文描述**，不是入参枚举值；核对口径时以自己传入的参数为准。
- 只传 `fundObject` 时其余参数走上游缺省，返回的报告期序列与口径由上游默认值决定；要固定口径就把 `poscharacter` / `industryType` / `proportionType` 显式传全。
- 支持多只基金批量，按基金逐行返回，不做单基金限制。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 缺失/空/非内码，日期格式非法，三个枚举参数非整数 —— 补齐/纠正参数 |
| 200 + `NO_DATA` 注记 | 基金内码无法解析，或区间内无报告期 —— 如实说明无数据 |
| `topNsumratio` 序列出现相等值 | 行业数不足 5 个，非异常 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `fundObject` 必须是**基金内码**；名称/代码先走 `fund-resolve`。

## 9. 相关工作流

- 只有产品名称或代码、没有内码 → 先读 `workflows/fund-code-resolution.md`，用 `fund-resolve` 取 `innerCode`。
