# fund-company-funds

| 项 | 值 |
|---|---|
| `api_id` | `fund-company-funds` |
| 服务端登记名 | 基金公司旗下基金 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

按**基金公司**维度返回旗下**基金的最新业绩面**：逐行给出「公司 × 一只基金」，
含最新净值与净值日期、日涨跌幅、近一年涨跌幅、证监会基金分类；
货币基金额外给万份收益、七日年化、近一年涨跌幅三项。

适用：用户问「华泰柏瑞旗下有哪些基金」「某公司旗下产品现在都什么净值/涨了多少」
「这家公司的货币基金七日年化多少」「这家公司有多少只混合型产品」；
也能从**一只基金的内码**反查它所属公司的全部产品线（只传 `fundObject` 即可）。

## 2. 不适用场景与易混接口

- 入参是**公司内码**或**基金内码**，**都不是 6 位基金代码**；要看单只基金档案用 `fund-basic-info`。
- **与 `fund-basic-info` 的区别**：那个给单只基金的静态档案（类型/成立日/管理人/**最新规模**）；
  本接口给公司维度的**多只基金业绩行**，**不含规模、不含成立日**。
- **与 `fund-asset-size` 的区别**：那个给逐报告期规模与申赎序列；本接口无规模。
- **与 `fund-nav` 的区别**：那个给单只基金的逐日净值序列（可指定区间）；本接口只给**最新一日**净值。
- 按**经理**维度看产品用 `fund-manager-resolve` → `fund-manager-info`（在管基金数与代表作在后者）。
- 只有**公司名称**时先调 `company-resolve` 换出 `companyCode`（两者同一套编号）；
  基金名称 → 基金代码用 `fund-resolve`。本接口不做名称解析，见第 8 节。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `companyCode` | string[]（兼容单值；数字亦可） | 二选一 | 基金公司**内码**列表（如 `["42742"]` = 华泰柏瑞）；与 `fundObject` 至少传一个 |
| `fundObject` | string[]（兼容单值；数字亦可） | 二选一 | **基金内码**（InnerCode）列表（如 `["24292"]` = 000172）；**不是 6 位基金代码** |

> `companyCode` 要的是**公司内码**（例：`"42742"` = 华泰柏瑞基金管理有限公司），
> 不是公司名称、不是公司简称。只有名称时先调 `company-resolve`（传 `companyName`）
> 拿 `companyCode` 再调本接口；直接把名称塞进 `companyCode` 会被判非法值 400。
>
> **`fundObject` 要的是基金内码，不是基金代码**（上游按 `MF_FundArchives` 的 InnerCode
> 取行）。手上只有 6 位代码时，先调 `fund-resolve`（传 `secuCode`）取
> `candidates[].innerCode`，把内码传给本接口。
>
> **二选一必填**：`companyCode` 与 `fundObject` **至少传一个**，两个都不传 → 400
> `PARAM_INVALID`。
>
> ⚠ 两个都传时是**并集、不是交集**：上游先把每个 `fundObject` 换成其所属公司，
> 再与 `companyCode` 合并去重，最后返回这些公司**各自旗下的全部基金**——不是
> 「这家公司的这只基金」。所以「某只基金属于哪家公司、这家公司还有哪些产品」
> 只需传 `fundObject` 一个内码即可。

## 4. 调用示例

```bash
# 某公司旗下全部基金的最新业绩（42742 = 华泰柏瑞）
pixi run etf-htbr invoke fund-company-funds '{"companyCode":["42742"]}'

# 只给某只基金的内码（24292 = 000172 华泰柏瑞量化增强混合A）：
# 上游先把它换成公司 42742，再返回华泰柏瑞旗下全部基金（不是只剩这一只）
pixi run etf-htbr invoke fund-company-funds '{"fundObject":["24292"]}'

# 6 位代码 → 内码，先 resolve
pixi run etf-htbr invoke fund-resolve '{"secuCode":"000172"}'

# 两个都不传 → 400 PARAM_INVALID（二选一必填）
pixi run etf-htbr invoke fund-company-funds '{}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 公司 × 一只基金 |
| `records[].companycode` / `records[].companyname` | 基金管理人代码 / 名称 |
| `records[].investadvisorabbrname` | 基金管理人简称（如 `华泰柏瑞基金`） |
| `records[].fundcode` / `records[].fundname` | 基金代码（6 位净码）/ 基金**简称**（上游取 `SecuMain.ChiNameAbbr`，不是全称） |
| `records[].unitnv` | **最新单位净值** |
| `records[].enddate` | 最新净值日期（`YYYY-MM-DD`） |
| `records[].nvdailygrowthrate` | 日涨跌幅（**%**） |
| `records[].rrinsingleyear` | 近一年涨跌幅（**%**） |
| `records[].fundtypename` | 基金分类名称（证监会，如 `混合型` / `债券型`） |
| `records[].dailyprofit` | 货币基金**万份收益**（元）；非货币基金为 `null` |
| `records[].latestweeklyyield` | 货币基金**七日年化**（%）；非货币基金为 `null` |
| `records[].fundreturn` | 货币基金**近一年涨跌幅**（%）；非货币基金为 `null` |

## 6. 数据口径

- **涨跌幅一律是百分数**：`nvdailygrowthrate` / `rrinsingleyear` / `latestweeklyyield` / `fundreturn`
  原值即 %（如 `1.582278481` = 1.58%），**不要 ×100**。
- **`unitnv` 是单位净值**，不是累计净值；`enddate` 是全表同一净值日。
- **货币基金三项只对货币基金有值**：`dailyprofit` / `latestweeklyyield` / `fundreturn`
  对非货币基金**恒为 `null`**（债券型、混合型都是），展示为「—」，**不是 0**。
- **`fundcode` 是 6 位净码**，不带 `.OF` / `.SH` 后缀。
- **⚠ 单次最多 100 行**：上游报表默认页容量 100（命中行数可能远大于回传行数，
  如某公司命中 376 行、实际回传 100 行）。**`recordCount` 达 100 时不得断言
  该公司只有 100 只产品**，应说明「名单可能被截断」。
- 行序由上游决定，未额外排序。
- **二选一必填**：至少传 `companyCode` 或 `fundObject` 之一，两个都不传直接 400。
- **两个都传 = 并集**：`fundObject` 的各内码先各自换成所属公司，与 `companyCode`
  合并去重后按公司出数；**不是**交集过滤。
- **只回存续产品**：上游跳过 `MF_FundArchives.ExpireDate` 非空且 ≤ 当日的基金
  （已到期/清盘不返回），且要求该基金在 `MF_FundArchivesAttach` 有 `TypeCode=10`
  的档案记录——两者任一不满足就整只不出现，**这是「查不到某只基金」的常见原因**。
- **排序由上游给定**：`companyname` 升序 → `fundcode` 升序。
- **不含规模、成立日、基金状态**：这些字段本接口不提供，需要时用 `fund-basic-info`。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | 两个参数**都没传**（二选一必填），或传了**非数字**值 —— 补参数后重试 |
| 200 + `NO_DATA` 注记 | 公司内码 / 基金代码无法解析，或该公司无在册基金 —— 如实说明无数据 |
| `dailyprofit` 等三项为 `null` | 非货币基金，正常，展示「—」 |
| `recordCount` = 100 | 触达上游页容量，名单可能被截断（见第 6 节），不要当作全集 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `companyCode` 若传，必须是**公司内码**；只有公司名称时先调 `company-resolve` 解析，不要直接传名称。
- `fundObject` 若传，必须是**基金内码**；只有 6 位基金代码时先调 `fund-resolve` 取 `innerCode`。
- 两个参数**二选一必填**（至少一个）；缺省的那个不下推。
- 旧参数 `companyName` / `includeClosed` **已作废**（传了静默忽略，不再有「二选一」校验）。
- 单次回传上限 100 行，大公司名单需注意截断。

## 9. 相关工作流

- 单只基金的规模/经理/费率 → `fund-basic-info`、`fund-rate`。
- 按报告期看规模变化 → `fund-asset-size`；单只基金净值走势 → `fund-nav` / `fund-nav-trend`。
