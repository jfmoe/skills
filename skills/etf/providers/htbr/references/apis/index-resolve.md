# index-resolve

| 项 | 值 |
|---|---|
| `api_id` | `index-resolve` |
| 服务端登记名 | 指数名称与代码精确映射 |
| 领域 | index |
| 资料完整度 | 完整（请求、响应、口径） |
| 性质 | 内网前置解析，不替代目标业务取数 |

## 1. 功能与适用场景

将指数名称或一种指数代码精确映射为代码组合，供后续指数业务接口按各自入参口径选取所需字段。入口为 `POST /api/v1/business/index-resolve:invoke`，沿用统一认证与响应包装。

## 2. 不适用场景与易混接口

- 不是基金、公司或经理解析。基金名称/代码用 `fund-resolve`；公司名称/编号用 `company-resolve`；经理姓名用经理解析流程。
- 不提供公网检索、模糊搜索、拼音补全、大小写改写、后缀猜测。输入原样与名称字段精确等值比对。
- 原始直接代码的类型、格式和目标口径已经满足时，可以直接调用目标接口，不必无条件映射。

## 3. 请求参数

四个字段恰好提交一个，不允许额外字段；显式 null 也不合法。

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `indexName` | string | 四选一 | trim 后非空，精确匹配下列五个名称字段之一：中文名称（ChiName）、中文名称缩写（ChiNameAbbr）、英文名称（EngName）、证券简称（SecuAbbr）、拼音证券简称（ChiSpelling） |
| `secuCode` | string | 四选一 | trim 后非空，SecuCode 净码原样精确等值：含 6 位数字净码（如 `000300`）、字母代码（如 `ISEQ`、`HZ5014`）、含点代码（如 `000001.ESCI`），保留前导零，不接受数值；字母代码大小写须与库内一致（如 `ISEQ` 须大写） |
| `gilCode` | string | 四选一 | trim 后非空，带交易所后缀口径（如 `000300.SH`），原样匹配，不补/改后缀 |
| `innerCode` | string 或整数数值 | 四选一 | 字符串 trim 后仅含十进制数字；数值必须为整数；值在 1 至 9223372036854775807，按正整数绑定 |

对象、数组、布尔值不能转换为字符串接受。数值型 innerCode 支持 JSON 整数及数学上为整数的 decimal，不接受浮点 Java 类型。

## 4. 调用示例

以下仅为请求格式示例，不保证库内存在该名称或代码：

```bash
pixi run etf-htbr invoke index-resolve '{"indexName":"沪深300"}'
pixi run etf-htbr invoke index-resolve '{"secuCode":"000300"}'
pixi run etf-htbr invoke index-resolve '{"gilCode":"000300.SH"}'
pixi run etf-htbr invoke index-resolve '{"innerCode":"3145"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `matchType` | 固定 `EXACT`，不是唯一命中的标志 |
| `matchCount` | 去重后的完整代码组合数量，不是 SQL 行数 |
| `candidates[]` | 候选代码组合 |
| `candidates[].innerCode` | 内码字符串 |
| `candidates[].secuCode` | SecuCode 净码字符串（6 位数字净码、字母代码或含点代码），原样返回，保留前导零 |
| `candidates[].gilCode` | 带交易所后缀代码字符串，保留源后缀 |
| `candidates[].indexName` | 证券简称（SecuAbbr），供多候选时消歧展示 |
| `candidates[].matchedNames` | 本次命中行的名称去重列表，不承诺返回全部历史名称 |

## 6. 数据口径

- 名称唯一来源为 `SecuMain`（`SecuCategory=4` 指数）的五个名称字段：中文名称/中文名称缩写/英文名称/证券简称/拼音证券简称；与 `BaseCode` 按 InnerCode JOIN。不承诺任意别名、曾用名都收录。
- 跨市场唯一化（用户裁定）：SecuMain 同一 SecuCode 在多个 SecuMarket 挂多条记录时，按 SecuMarket **升序取最小市场**的那条（`ROW_NUMBER() PARTITION BY SecuCode` 取 1）；`gilCode` 带后缀已指定市场、`innerCode` 已定位单行，不受此规则影响。
- 只用绑定参数等值匹配，不加额外缓存，不改写大小写、代码后缀或补零；文本比较遵循数据库排序规则 `Chinese_PRC_BIN`（**大小写敏感**），字母代码（如 `ISEQ`）须按库内大小写原样传入。
- 按用户裁定**不加** LC_IndexBasicInfo 收口：候选可能包含下游指数接口查不到数据的代码（SecuCode 跨市场存在与基金重码的可能），下游查不到时如实返回空集，不得据此断言指数不存在。
- 按完整 `(innerCode,secuCode,gilCode)` 组合归并 matchedNames；相同内码下不同证券代码或 GilCode 必须保留为不同候选。代码输入可命中同一组合的多个名称行，名称输入只收集本次精确命中的名称行。

## 7. 空数据与异常值语义

- 零、一、多候选均 HTTP 200；零候选不是基础设施故障。唯一候选可续调，多候选必须等待用户确认。
- 参数错误为 HTTP 400 `PARAM_INVALID`；数据库真实失败沿现有 JDBC 语义返回 HTTP 503 `DEGRADED`，不得伪装成零命中。
- 不提供虚构映射，也不存在任何内置示例映射。真实源未启用或解析链路失败时返回 **503 `DEGRADED`**（`error.detail` 含 reason），不会返回成功空候选以外的伪造结果。失败结果不得用于真实续调。

## 8. 前置条件与调用限制

需有效授权与内网网关可达，调用间隔建议 ≥3 秒。受当前 Key 的实际授权控制。

## 9. 相关工作流

见 `references/workflows/index-code-resolution.md`。按目标接口对应代码字段续调：成分股/日行情/区间行情取 gilCode（带后缀），业绩走势取 secuCode（SecuCode 净码，含字母代码如 `ISEQ` 与含点代码）；指数关联基金推荐 secuCode，也接受 gilCode/内码（服务端自行换算）。

## 10. 验证与交付边界

适配器及双 SQL 资产由 `IndexResolveAdapterTest` 验证。注册资产为 `15-index-resolve-registry.sql`，须管理员另行执行；单测不等于已连通生产数据库或已上线。
