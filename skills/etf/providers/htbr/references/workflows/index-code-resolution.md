# Workflow：指数名称与代码精确映射

## 适用与范围

用户只给指数名称（如「沪深300」），或现有指数代码与目标接口口径不同：先读 `references/apis/index-resolve.md`。本流程只解析指数；基金名称/代码按 `fund-code-resolution.md`，经理姓名按 `manager-name-resolution.md`。混合请求须拆分标的范围，不能把基金映射结果当指数代码，反之亦然。

## 目标接口 → 代码字段映射（续调前先对照）

| 目标接口 | 实际入参 | resolve 后取 |
|---|---|---|
| `index-basic-info` | `indexObject[]` **内码**（纯数字） | `innerCode` |
| `index-constituents` | `indexObject[]` 聚源代码（带后缀）或内码 | `gilCode`（或 `innerCode`） |
| `index-daily-quote` | `indexCodes[]` ≤50 带后缀（服务端剥后缀） | `gilCode` |
| `index-range-quote` | `indexCodes[]` ≤50 带后缀（同上） | `gilCode` |
| `index-performance-trend` | `indexCode` **SecuCode 净码**（原样全串等值） | `secuCode` |
| `fund-index-related` | `indexCode` **指数内码**（必填，服务端不解析） | `innerCode` |

SecuCode 净码不限于 6 位数字：真库含字母代码（如 `ISEQ`、`HZ5014`）与含点代码（如 `000001.ESCI`）；resolve 返回的 `secuCode` 原样可传。字母代码按库内大小写（`ISEQ` 大写）精确等值，库排序规则 `Chinese_PRC_BIN` 区分大小写。

若参数名恰为 indexCode，也必须查清目标接口实际口径（上表），不按名称猜、不自行拼/剥后缀。

## 编排

1. 先确定目标业务接口，阅读其单接口文档，明确需要 gilCode、secuCode 还是 innerCode。
2. 用户直接给出符合类型、格式及目标口径的代码时可直调；否则将原始名称或一种代码交给精确映射，不先补零或拼后缀。
3. 确认来源真实且未降级，再判断 matchCount：
   - 0：说明名称或代码未精确命中，请用户核对，结束本轮。不能据此断言指数不存在。
   - 1：直接取唯一候选中目标接口对应的代码字段续调，不再让用户确认。带后缀接口取 gilCode，SecuCode 净码接口（如 `index-performance-trend`）取 secuCode（原样，含字母/含点代码不改写），明确要求内码的接口（如 `index-basic-info`、`fund-index-related`）取 innerCode；仍按目标文档校验格式。
   - 大于 1：展示各候选的 indexName（证券简称）与 secuCode/gilCode 等可区分信息，编号后停下等用户选择，不按第一条或知名度擅自挑选。
4. 用户确认后，只用选中完整代码组合续调；相同 innerCode 不代表不同 secuCode/gilCode 可以忽略。代码缺失或格式仍不满足目标时停下说明，不自行推导。

## 边界

名称只来自 SecuMain（SecuCategory=4）五个名称字段的精确等值，不做模糊/拼音补全/大小写改写。按裁定不加 LC_IndexBasicInfo 收口：解析出的候选可能在下游接口查不到数据，届时如实返回空集。无公网、后缀猜测或额外缓存。matchedNames 仅表示本次命中行名称，不是完整别名库。真实失败按降级处理，不能假装零候选或拿演示映射续调。
