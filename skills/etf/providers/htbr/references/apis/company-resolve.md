# company-resolve

| 项 | 值 |
|---|---|
| `api_id` | `company-resolve` |
| 服务端登记名 | 公司名称与编号解析 |
| 领域 | fund |
| 资料完整度 | 完整（请求、响应、口径） |
| 性质 | 内网前置解析，不替代目标业务取数 |

## 1. 功能与适用场景

将公司名称精确映射为企业编号，返回该编号及所属公司、上市公司代码，供后续公司维度接口取数。入口为 `POST /api/v1/business/company-resolve:invoke`，沿用统一认证与响应包装。

名称支持源表收录的四种写法：中文名称（`华泰柏瑞基金管理有限公司`）、中文简称（`华泰柏瑞基金`）、中文拼音简称（`HTBRJJ`）、英文名称。

适用：用户只给公司名、而目标接口要企业编号时，例如「华泰柏瑞旗下有哪些基金」——先本接口把 `华泰柏瑞基金` 解析成 `42742`，再把编号传给 `fund-company-funds`。

## 2. 不适用场景与易混接口

- 不是基金、指数或经理解析。基金产品名称与代码用 `fund-resolve`；指数名称与代码按目标指数接口文档核对；经理姓名走经理解析流程。
- 不提供公网检索、模糊搜索、补全、拼音转换或大小写改写；名称必须与源表某个名称字段完全一致。
- 不判断公司是否存续、是否仍有在管产品；解析命中只代表该名称在源表存在。
- 只出编号，不出该公司旗下基金清单；清单用 `fund-company-funds`。

## 3. 请求参数

单参数接口。不传、传空、传多个参数或携带额外字段均不合法；显式 null 也不合法。

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `companyName` | string | 必填 | trim 后非空，精确匹配下列四个名称字段之一：中文名称（ChiName）、中文简称（AbbrChiName）、中文拼音简称（NameChiSpelling）、英文名称（EngName） |

对象、数组、布尔值与数值不能转换为字符串接受；仅接受 JSON 字符串。

## 4. 调用示例

以下仅为请求格式示例，不保证库内存在该名称：

```bash
pixi run etf-htbr invoke company-resolve '{"companyName":"华泰柏瑞基金"}'
pixi run etf-htbr invoke company-resolve '{"companyName":"华泰柏瑞基金管理有限公司"}'
pixi run etf-htbr invoke company-resolve '{"companyName":"HTBRJJ"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `matchType` | 固定 `EXACT`，不是唯一命中的标志 |
| `matchCount` | 命中的公司数量，不是 SQL 行数 |
| `candidates[]` | 一家公司一条 |
| `candidates[].companyCode` | 企业编号，即 `fund-company-funds` 的入参 |
| `candidates[].parentCompany` | 所属公司编号，可为 `null` |
| `candidates[].listedCode` | 上市公司代码，非上市为 `null` |
| `candidates[].companyName` | 公司中文名称（ChiName），供多候选时消歧展示 |
| `candidates[].matchedNames` | 本次命中行的名称字段值去重列表，不承诺返回该公司的全部别名 |

## 6. 数据口径

- 唯一数据源为 `LC_InstiArchive`（机构档案），四个名称字段 `ChiName`、`AbbrChiName`、`NameChiSpelling`、`EngName` 全部参与等值匹配；同一公司的不同名称命中归并为一条候选，`matchedNames` 收集命中值。不承诺任意别名、曾用名或分支机构名称都收录。
- 先按四个字段的等值条件圈定候选行，再展开名称字段；百万级表上不为全表做名称展开。
- 只用绑定参数等值匹配，不加额外缓存，不改写大小写、全角半角或括号；是否区分文本大小写遵循数据库既有比较规则。
- `companyCode` 与 `fund-company-funds` 的 `companyCode` 同一编号体系（`华泰柏瑞基金管理有限公司` = `42742`）。
- `parentCompany`、`listedCode` 源表可空，原样返回 `null`，不抹 0、不参与匹配。
- 同一名称可能命中多家主体（如英文名相同的主体与其分支机构），候选按 `companyCode` 分开保留，不合并、不截断。

## 7. 空数据与异常值语义

- 零、一、多候选均 HTTP 200；零候选不是基础设施故障，应请用户核对名称写法（全称、简称、拼音简称、英文名），不得据此断言公司不存在。
- 唯一候选可续调下游；多候选必须展示 `companyName` 等可区分信息并等待用户确认，不按第一条或规模擅自挑选。
- 参数错误为 HTTP 400 `PARAM_INVALID`；数据库真实失败或源数据异常（企业编号缺失、类型错误）返回 HTTP 503 `DEGRADED`，不得伪装成零命中。
- 不提供虚构映射，也不存在任何内置示例映射。真实源未启用或解析链路失败时返回 **503 `DEGRADED`**（`error.detail` 含 reason），不会返回成功空候选以外的伪造结果。失败结果不得用于真实续调。

## 8. 前置条件与调用限制

需有效授权与内网网关可达，调用间隔建议 ≥3 秒。注册 scope 同时面向 query 与 analysis，但仍受当前 Key 的实际授权控制。

## 9. 相关工作流

见 `references/workflows/company-code-resolution.md`。解析出的 `companyCode` 即 `fund-company-funds` 的入参口径，直接续调。

## 10. 验证与交付边界

适配器及双 SQL 资产由 `CompanyResolveAdapterTest` 验证（含双方言资产形状断言），SQL 资产同时纳入 `ExternalSqlAssetAssertionTest` 与 `OracleSqlAssetGuardTest` 清单。注册资产为 `48-company-resolve-registry.sql`（另有 Oracle MERGE 版 `db/sql-oracle/48-company-resolve-registry.sql`），须管理员另行执行，执行后需重启应用（注册表为启动全量加载）；单测不等于已连通生产数据库或已上线。
