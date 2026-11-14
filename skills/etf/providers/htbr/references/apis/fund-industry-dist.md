# fund-industry-dist

| 项 | 值 |
|---|---|
| `api_id` | `fund-industry-dist` |
| 服务端登记名 | 基金行业分布 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询基金持仓的**逐行业分布**：按行业分类标准返回各行业的市值占净值比，支持**全部持股**与**重仓股票**两种口径。

适用：用户问「这只基金都配在哪些行业」「各行业占比多少」「重仓股集中在哪个行业」。

## 2. 不适用场景与易混接口

- **与 `fund-industry-concentration` 的区别**：那个给 **Top1~5 累计占比**（一个报告期一行）；本接口给**逐行业明细**（每行业一行、带行业名）。
- **与 `fund-holding-detail` 的区别**：那个是逐**个股**持仓与占比变动；本接口是**行业**聚合。
- 两种持仓口径（重仓 / 全部持股）由同一个 `api_id` 的 `poscharacter` 区分，**不要**当作两个接口。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `fundObject` | integer[]（兼容单值） | **是** | 基金**内码**列表（如 `[579499]`），支持多只；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |
| `poscharacter` | string | 否 | 持仓类型：`1` 重仓股票 / `2` 全部持股；空 = 上游缺省 |
| `industryType` | string | 否 | 行业分类标准（如 `38` 申万一级）；空 = 上游缺省；未知值由上游返回空集 |
| `beginDate` | string | 否 | 报告期区间起，`YYYY-MM-DD`；格式非法 → 400 |
| `endDate` | string | 否 | 报告期区间止，`YYYY-MM-DD`；格式非法 → 400；与 `beginDate` 均空 = 由上游缺省 |

> `fundObject` 要的是**内码**，不是 6 位代码、也不是带 `.OF` 的 GilCode。只有名称/代码时先用
> `fund-resolve` 解析，取 `candidates[].innerCode` 再调用本接口。

## 4. 调用示例

```bash
# 单只基金 + 重仓股票 + 申万一级
pixi run etf-htbr invoke fund-industry-dist '{"fundObject":[579499],"poscharacter":"1","industryType":"38"}'
# 多只基金、全部持股、限定报告期区间
pixi run etf-htbr invoke fund-industry-dist '{"fundObject":[579499,2997],"poscharacter":"2","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 基金 × 报告期 × 行业 |
| `records[].fundobject` | 基金内码 |
| `records[].fundcode` / `records[].fundname` | 基金代码 / 简称 |
| `records[].poscharacter` | 持仓类型**中文描述**（如「重仓股票」） |
| `records[].reportdate` | 报告期（`YYYY-MM-DD`） |
| `records[].industrytype` | 行业分类标准**中文描述**（如「申万一级行业分类」） |
| `records[].industryname` | 行业名称 |
| `records[].ratioinnv` | 行业市值占基金净值比（**%**） |

## 6. 数据口径

- **逐行业明细**：每个「基金 × 报告期 × 行业」一行，不做 TopN 收敛，也不返回行业市值绝对值。
- 单位是**百分数**，上游已换算；平台不再 ×100、不做舍入，直接展示。
- `poscharacter` / `industrytype` 两列回显的是**中文描述**，不是入参枚举值；核对口径时以自己传入的参数为准。
- 只传 `fundObject` 时其余参数走上游缺省，返回的报告期序列与口径由上游默认值决定；要固定口径就把 `poscharacter` / `industryType` 显式传全。
- 同一报告期同一行业标准下，各行业 `ratioinnv` 合计应 ≈ 100%（允许 ±0.5pp 舍入差）。
- 支持多只基金批量，按基金逐行返回，不做单基金限制。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `fundObject` 缺失/空/非内码，日期格式非法 —— 补齐/纠正参数 |
| 200 + `NO_DATA` 注记 | 基金内码无法解析，或区间内无报告期 —— 如实说明无数据 |
| `ratioinnv = 0` | 该报告期该行业无持仓或占比为 0，不是缺数据 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `fundObject` 必须是**基金内码**；名称/代码先走 `fund-resolve`。

## 9. 相关工作流

- 只有产品名称或代码、没有内码 → 先读 `workflows/fund-code-resolution.md`，用 `fund-resolve` 取 `innerCode`。
