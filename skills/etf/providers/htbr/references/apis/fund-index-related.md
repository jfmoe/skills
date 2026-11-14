# fund-index-related

| 项 | 值 |
|---|---|
| `api_id` | `fund-index-related` |
| 服务端登记名 | 指数关联基金 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有；取数走 DataService 报表通道，入参为指数内码） |

## 1. 功能与适用场景

按**指数代码**查询**跟踪/关联该指数的基金清单**：基金代码与简称、成立日与发售方式、管理人、
近一年收益与超额收益、跟踪误差、信息比率、费率、最新规模、申购与赎回状态。

适用：用户问「沪深300 有哪些跟踪它的基金」「000001 指数关联了哪些基金、跟踪误差多大」。

## 2. 不适用场景与易混接口

- ⚠ 本接口 `indexCode` **只收指数内码**（纯数字正整数，如 `3145`），**不做任何代码解析**；只有名称、SecuCode 净码（如 `000300`、`ISEQ`）、含点代码或聚源代码（`000300.SH`）时，**先调 `index-resolve` 取 `innerCode`** 再传本接口（与 `index-basic-info` 同一编排口径），非内码一律 400。
  而 `index-constituents` 的 `indexObject[]` 收**聚源代码（带后缀）或内码**（`000300.SH`）——两者口径不同，**不要混用**。
- 要**指数成分股**（各股权重、市值、行业）用 `index-constituents`；本接口给的是**跟踪该指数的基金**。
- 要某只基金自己的档案/净值/区间走势，分别用 `fund-basic-info` / `fund-nav` / `fund-nav-trend`；
  本接口只给截面清单，不给单只基金的净值序列。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `indexCode` | string | 是 | 指数**内码**（纯数字正整数，如 `3145`）；缺失/空白/非内码 → 400 `PARAM_INVALID`，错误信息指路 `index-resolve` |

> 本接口**不解析代码**：内码原样下推报表参数 `IndexCodes`（DS 侧语义即指数 InnerCode）。
> 用户只给名称或某一种代码（SecuCode 净码 `000300`/`ISEQ`、含点代码 `000001.ESCI`、聚源代码 `000300.SH`）时，
> 先调 `index-resolve`（入参 `indexName` / `secuCode` / `gilCode` / `innerCode` 四选一）取回 `candidates[].innerCode` 再传本接口。
> 无缺省值，不传 `indexCode` 不会默认查询任何指数。

## 4. 调用示例

```bash
pixi run etf-htbr invoke index-resolve '{"secuCode":"000300"}'
# 取回 candidates[].innerCode（沪深300 为 3145）后：
pixi run etf-htbr invoke fund-index-related '{"indexCode":"3145"}'
```

**反例（会返回 400 `PARAM_INVALID`）**：`{"indexCode":"000300.SH"}` / `{"indexCode":"000300"}` / `{"indexCode":"ISEQ"}` —— 这些不是内码，须先 `index-resolve`。

## 5. 返回数据路径与关键字段

读 `$.data`，含 `indexCode` / `fundCount` / `funds[]`，`funds[]` 每行 **16 个字段**，字段名与 DS 报表列名
**全小写逐字一致**（第三方接口响应命名标准）：

| 字段 | 含义 |
|---|---|
| `fundobject` | 基金内码 |
| `fundcode` / `fundname` | 基金代码 / 基金简称 |
| `gilcode` | 基金 GilCode（**带 `.OF` 后缀**） |
| `rrinsingleyear` | 近一年收益率（**%**） |
| `chargerate` | 管理费率与托管费率之和（**%**） |
| `excessreturn` | 近一年超额收益率（**%**） |
| `datavalue` | 近一年跟踪误差（**%**） |
| `inforatio` | 近一年信息比率（无量纲） |
| `netassetsvalue` | 最新基金规模（**亿元**） |
| `investadvisorcode` / `investadvisorabbrname` | 基金管理公司代码 / 简称 |
| `applyingtype` / `redeemtype` | 申购状态 / 赎回状态（**中文文案**，见第 6 节） |
| `startdate` | 基金成立日（`yyyy-MM-dd`） |
| `floattype` | 发售方式代码 |

## 6. 数据口径

- 百分数字段（`rrinsingleyear`、`chargerate`、`excessreturn`、`datavalue`）**已是百分数**，直接加 `%`，**不要**再 ×100。
- `netassetsvalue` 单位已是**亿元**，**不要**再 ÷1e8。
- `applyingtype` / `redeemtype` 服务端返回**中文文案**（实测如 `可申购` / `可赎回`），直接展示。
- `fundCount` = 本次返回的 `funds[]` 条数；不传分页参数，命中多少返回多少，
  返回条数以线上实际为准，**不要**把 `fundCount` 当成该指数的全量关联基金数。
- 单行字段为 `null` 时表示该项无数据，展示为「—」。

## 7. 空数据与异常值语义

- **入参不是内码 → 400 `PARAM_INVALID`**（缺失/空白/净码/聚源代码/字母代码），错误信息会指路 `index-resolve`；不会静默返回 0 条。
- **内码合法但该指数确实无关联基金 → 200 + `fundCount=0` + `warnings` 含 `W202_NO_DATA`**，不是错误。
- 部分基金的绩效/规模字段可能为 `null`，展示为「—」，**不要当成 0，也不要报错**。
- 接口会原样回显传入的 `indexCode`，**回显不构成身份证明**（不校验该内码在指数域是否存在）。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达（见 `SKILL.md`「凭证缺失或失效」）。
- 调用间隔建议 ≥ 3 秒，不要并发批量打（会触发 429 `RATE_LIMITED`）。
- 取数依赖服务端 DataService 报表通道；该通道不可用时服务端返回 **503 `DEGRADED`**，
  不再返回任何演示数据，回答须如实告知该接口暂不可用。

## 9. 相关工作流

无。可作为指数视角的补充：先 `index-constituents` 看成分股，再本接口看跟踪基金。
