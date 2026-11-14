# index-basic-info

| 项 | 值 |
|---|---|
| `api_id` | `index-basic-info` |
| 服务端登记名 | 指数基本资料 |
| 领域 | index |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

查询**指数静态基本资料**：一行 = 一只指数，给出代码/名称、指数类型、基期与基点、发布日期与发布机构、成份证券类型与数量、调整周期、加权方式、指数简介。

适用：用户问「沪深300 是哪家机构发布的」「某指数的基期基点和编制方法」「这个指数有多少只成分股、多久调整一次」「某指数的简介/编制方案」。

## 2. 不适用场景与易混接口

- 要**指数行情**（点位、涨跌、成交）用 `index-daily-quote`（逐日）或 `index-range-quote`（区间），本接口没有任何行情字段。
- 要**逐只成分股清单与权重**用 `index-constituents`。
- 要**成分股的行业聚合分布**用 `index-industry-dist`。
- 要**跟踪该指数的基金清单**用 `fund-index-related`。
- ⚠ **本接口只收内码**：`indexObject` 的元素必须是 `index-resolve` 返回的 `innerCode`（纯数字，如 `3145`）。只有名称、聚源代码（`000300.SH`）、多段代码（`000001.ESCI.CZC`）或 6 位净码（`000300`）时，先按 `references/workflows/index-code-resolution.md` 调 `index-resolve` 取内码；直接把代码传进本接口会 **400**（与 `fund-manager-*` 要先 `fund-manager-resolve`、`fund-*` 要先 `fund-resolve` 是同一套编排）。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `indexObject` | string[]（兼容单字符串） | **是** | 指数**内码**列表（纯数字正整数，如 `3145`），按入参顺序去重；空白元素剔除；缺失 / 全空白 / 元素非内码 → 400（聚源代码 `000300.SH`、多段代码 `000001.ESCI.CZC`、6 位净码 `000300`、中文名一律 400，错误信息会提示先调 `index-resolve`） |

> - **没有其它参数**：DS 报表请求面只有 `IndexObject` 一项，没有日期、没有指标选择入参。
> - 一次可传多只指数，返回多行（一行/指数）。
> - 无枚举型入参。本接口**不做代码解析**，内码由调用方先经 `index-resolve` 取得。

## 4. 调用示例

```bash
# ① 只有名称或代码：先解析出内码（四路入参择一：indexName / secuCode / gilCode / innerCode）
pixi run etf-htbr invoke index-resolve '{"gilCode":"000300.SH"}'
#    → $.data.candidates[0].innerCode = "3145"

# ② 用内码调本接口（多只指数同理，数组里放内码；也兼容单字符串写法）
pixi run etf-htbr invoke index-basic-info '{"indexObject":["3145"]}'
pixi run etf-htbr invoke index-basic-info '{"indexObject":["3145","4978"]}'
```

> 直接传 `{"indexObject":["000300.SH"]}` / `["000001.ESCI.CZC"]` / `["000300"]` 会 400，不是「查无数据」。

## 5. 返回数据路径与关键字段

读 `$.data.records[]`，**15 个字段**（DS 列名小写原样）：

| 字段 | 含义 |
|---|---|
| `gilcode` | 聚源代码（如 `000300.SH`） |
| `indexobject` | 指数内码 |
| `indexcode` / `indexname` | 指数代码 / 指数名称 |
| `indexengname` | 指数英文名称 |
| `indextype` | 指数类型（**中文描述**） |
| `basedate` | 指数基期（`yyyy-MM-dd`） |
| `basepoint` | 指数基点 |
| `pubdate` | 发布日期（`yyyy-MM-dd`） |
| `puborgname` | 发布机构 |
| `componenttype` | 成份证券类型（**中文描述**） |
| `componentnum` | 成份证券数量 |
| `componentadperiod` | 成份证券调整周期（**中文描述**） |
| `wamethod` | 加权方式（**中文描述**） |
| `indexbriefintro` | 指数简介 |

## 6. 数据口径

- **类型类字段已是中文描述**：`indextype` / `componenttype` / `componentadperiod` / `wamethod` 由上游按系统常量表译好（如「规模指数」「股票」「每半年」「自由流通市值加权」），**直接展示，不要拿代码值反查，也不要自行翻译**。
- `basedate` / `pubdate` 是**日期**（`yyyy-MM-dd` 字符串），不是报告期；`basepoint` 是基期点位（如 1000、100），与当前点位无关。
- 一行 = 一只指数，**按 `indexcode` 升序**返回；同一内码重复传入不会重复出行。
- 指数名称取自证券主表（含港股主表），英文名可能为空。
- `componentnum` 是**上游成分表当前在册成分数**（含中债/上清所/港股成分表），与 `index-constituents` 返回的行数不一定相等（后者是某个截止日的截面，可能被上游截断）；需要权威成分清单时以编制机构公告为准。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `indexObject` 缺失 / 全为空白；元素**不是内码**（聚源代码 `000300.SH`、多段代码 `000001.ESCI.CZC`、6 位净码 `000300`、中文名）—— 先调 `index-resolve` 取 `innerCode` 再试 |
| 200 + `NO_DATA`（`recordCount=0`） | 该内码在指数基本资料表里无记录（上市公司/基金代码常见此种）。**不是错误**，不要报「接口失败」 |
| 503 `DEGRADED` | 数据服务暂时不可用（**不是**「没有这只指数」）；稍后重试，不要把 503 说成查无数据 |
| 传多只指数只回部分行 | 只有**有基本资料记录**的指数才出行；不是漏数据 |
| `indexname` / `indexengname` 为 `null` | 该内码在沪深/港股证券主表里都查不到名称；其余字段仍可用 |
| `componentnum` 为空或缺省 | 上游在该指数的成分表里查不到在册成分（成分数据未收录）；展示为「—」，**不要当成 0**、也不要说「该指数没有成分股」 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- 一次传入的指数全部返回；无批量上限声明，但请按需传（一次一只到几十只为宜）。
- 静态资料，无历史时点口径：问「历史上的基期」与「当前成分数」都以最新为准。
- 只收指数**内码**：聚源代码/净码先经 `index-resolve` 转换；基金、股票内码混传只会得到空结果。

## 9. 相关工作流

- 只给指数中文名或只有一种代码 → 先走 `references/workflows/index-code-resolution.md`（`index-resolve`）拿 `innerCode`，再调本接口；`matchCount=0` 时请用户核对，不要补零/补后缀/猜测。
