# fund-resolve

| 项 | 值 |
|---|---|
| `api_id` | `fund-resolve` |
| 服务端登记名 | 基金名称与代码精确映射 |
| 领域 | fund |
| 资料完整度 | 完整（请求、响应、口径） |
| 性质 | 内网前置解析，不替代目标业务取数 |

## 1. 功能与适用场景

将有效基金产品名称或一种基金代码精确映射为代码组合，供后续基金业务接口选取所需字段。入口为 `POST /api/v1/business/fund-resolve:invoke`，沿用统一认证与响应包装。

## 2. 不适用场景与易混接口

- 不是公司、经理或指数解析。公司名称/编号用 `company-resolve`；经理姓名用经理解析流程；指数代码按目标指数接口文档核对，不能交给本接口。
- 不提供公网检索、模糊搜索、拼音、补全、后缀猜测或任意基金全称覆盖。
- 原始直接代码的类型、格式和目标口径已经满足时，可以直接调用目标接口，不必无条件映射。

## 3. 请求参数

四个字段恰好提交一个，不允许额外字段；显式 null 也不合法。

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `fundName` | string | 四选一 | trim 后非空，精确匹配有效 `DisclName` |
| `secuCode` | string | 四选一 | trim 后非空，保留前导零，不接受数值 |
| `gilCode` | string | 四选一 | trim 后非空，原样匹配，不补/改后缀 |
| `innerCode` | string 或整数数值 | 四选一 | 字符串 trim 后仅含十进制数字；数值必须为整数；值在 1 至 9223372036854775807，按正整数绑定 |

对象、数组、布尔值不能转换为字符串接受。数值型 innerCode 支持 JSON 整数及数学上为整数的 decimal，不接受浮点 Java 类型。

## 4. 调用示例

以下仅为请求格式示例，不保证库内存在该名称或代码：

```bash
pixi run etf-htbr invoke fund-resolve '{"fundName":"待核对的产品披露名称"}'
pixi run etf-htbr invoke fund-resolve '{"secuCode":"510300"}'
pixi run etf-htbr invoke fund-resolve '{"gilCode":"510300.OF"}'
pixi run etf-htbr invoke fund-resolve '{"innerCode":"12345"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `matchType` | 固定 `EXACT`，不是唯一命中的标志 |
| `matchCount` | 去重后的完整代码组合数量，不是 SQL 行数 |
| `candidates[]` | 候选代码组合 |
| `candidates[].innerCode` | 内码字符串 |
| `candidates[].secuCode` | 证券代码字符串，保留前导零 |
| `candidates[].gilCode` | GilCode 字符串，保留源后缀 |
| `candidates[].matchedNames` | 本次命中行的有效 DisclName 去重列表，不承诺返回所有历史名称 |

## 6. 数据口径

- 名称唯一来源为 `MF_FundProdName` 中 `IfEffected=1` 的 `DisclName`；与 `BaseCode` 按 InnerCode JOIN。不承诺任意简称、全称或份额名称都收录。
- 只用绑定参数等值匹配，不加额外缓存，不改写大小写、代码后缀或补零；是否区分文本大小写遵循数据库既有比较规则。
- 按完整 `(innerCode,secuCode,gilCode)` 组合归并 matchedNames；相同内码下不同证券代码或 GilCode 必须保留为不同候选。代码输入可命中同一组合的多个名称行，名称输入只收集本次精确命中的名称行。

## 7. 空数据与异常值语义

- 零、一、多候选均 HTTP 200；零候选不是基础设施故障。唯一候选可续调，多候选必须等待用户确认。
- 参数错误为 HTTP 400 `PARAM_INVALID`；数据库真实失败沿现有 JDBC 语义返回 HTTP 503 `DEGRADED`，不得伪装成零命中。
- 不提供虚构映射，也不存在任何内置示例映射。真实源未启用或解析链路失败时返回 **503 `DEGRADED`**（`error.detail` 含 reason），不会返回成功空候选以外的伪造结果。失败结果不得用于真实续调。

## 8. 前置条件与调用限制

需有效授权与内网网关可达，调用间隔建议 ≥3 秒。注册 scope 同时面向 query 与 analysis，但仍受当前 Key 的实际授权控制。

## 9. 相关工作流

见 `references/workflows/fund-code-resolution.md`。按目标接口对应代码字段续调，而不是固定选 secuCode 或拼后缀。

## 10. 验证与交付边界

适配器及双 SQL 资产由 `FundResolveAdapterTest` 验证。注册资产为 `08-fund-resolve-registry.sql`，须管理员另行执行；单测不等于已连通生产数据库或已上线。
