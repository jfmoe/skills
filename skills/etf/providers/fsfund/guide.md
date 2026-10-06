# 华宝 UDSP

客户端在本目录的 `scripts/etf_index.py`，HTTP 与元数据模块均随技能提供。Python 3.10+，网络请求仅用标准库；环境配置见[配置说明](../../references/setup.md)。在 Fire 项目中使用 `pixi run etf-fsfund`，它从项目 `.env` 加载凭据，不需要旧技能目录。

## 动态接口工作流

```bash
pixi run etf-fsfund list-apis
pixi run etf-fsfund schema INF_FUND_INFO
pixi run etf-fsfund call INF_FUND_INFO '{"FUND_CODE":"510300","currentPage":"1"}'
```

在其他环境，把 `pixi run etf-fsfund` 换成 `python <技能目录>/providers/fsfund/scripts/etf_index.py`，并配置环境变量。`list-apis`、`schema`、`call` 都会自动在缓存缺失或过期时获取元数据；已知接口发生变化时使用 `refresh-meta`。缓存位于本提供方目录 `.cache/meta_registry.json`，默认 3600 秒，可由 `HJ_META_CACHE_SEC` 调整。Skill 标识始终是 `fsfund-etf-index`，不要因入口重命名而修改它。

1. `list-apis`（可加 `--json`）确认当前 PATH；推荐使用 PATH；客户端也接受 PATH 大小写变体及 `API_URL` 别名。
2. `schema PATH` 查看入参、必填组与出参。`NOTNULLFLAG=1` 且无必填组表示独立必填；有必填组时组内至少提供一项，不要求该组所有字段。`NOTNULLFLAG=0` 且无组表示可选，缺失标志显示未声明；枚举以当前 schema 为准。`IS_ETF_FUND` 使用 `1/0`；`IS_ETF_LINK` 的实测枚举是 `1-是/0-否`，传 `1` 会空返，不可类推。
3. 选择必要字段类别与日期区间，构造 JSON。代码及大小写从基本信息核实，场外可能为 `.OF`，指数可能为 `.CSI`。实测中证红利为 `000922.CSI`、全收益指数为 `h00922.CSI`；误用 `000922.SH` 的估值查询会成功返回空列表，不能据此断言无数据。
4. 调用后同时检查业务 `code`、`message` 和 `data`。客户端打印原始响应，进程退出 0 不等于业务成功；成功示例为 `code=0000`。360 聚合的 `data.result` 是按 PATH 键控的对象，每个子项有自己的 `code`、`message`、`result`、`total`；外层 `total=0` 不代表空结果。逐项检查并按子项 total 判断完整性。

## 任务与典型接口

| 任务 | PATH 与注意点 |
|---|---|
| 基金列表、代码核实、管理人或跟踪指数筛选 | `INF_FUND_INFO`；服务端 `FUND_MGR` 可模糊匹配，精确公司统计需核对管理人字段 |
| 指数信息／分类 | `INF_INDX_INFO`／`INF_INDX_INDS_TYPE` |
| 基金日行情、贴水率、复权价格 | `INF_FUND_PRICE`；同时有当日份额 `FUND_SHARE`，检查价格是否复权、数据日期与单位 |
| 净值、规模、净流入 | `INF_FUND_NAV`；日期必填性按 schema；单产品规模优先按 `ASSET_NAV` 定义，合计行与独立份额避免双计 |
| 指数行情、估值、主力资金流 | `INF_INDX_PRICE`／`INF_INDX_VALUATION`／`INF_INDX_CAP_DIRECT` |
| 基金业绩／风险指标、经理 | `INF_FUND_PERF`（含 Alpha、Beta、信息比率等，逐周期核对可用值）／`INF_FUND_MGR_INFO` |
| 持券、行业比例、资产配置 | `INF_FUND_PRT_SECDETAIL`／`INF_FUND_PRT_INDS_RATIO`／`INF_FUND_PRT_ASSET` |
| 同时需要多类历史数据 | `FUND360_DATA`／`INDX360_DATA`；先看 `_members` 可选值，仅选所需子接口 |

时间范围遵循用户要求；未指定且确需历史走势时，可用近 6 个月并说明区间。基本信息、单期快照不自动扩展半年查询。多代码仅用于 schema 明确支持的逗号分隔字段。

## 分页与输出

- 仅 schema 声明分页参数时才翻页。指数估值、指数分类、指数主力流、指数行业比例及基金行业比例当前没有分页入参；这些接口用代码和日期缩小范围，不能循环添加无效页码。支持分页时，`currentPage` 逐页增加，`pageSize` 仅在 schema 支持时传入，按该接口上限设置。检查实际响应分页字段、累计唯一记录数及总量；不能把一页或固定约 1000 条结果当全量。
- 无总量时按接口分页行为继续到空页，重复页或接口错误时停止并报告完整性未知；一页少于请求页大小本身不足以证明结束。汇总保留基金代码、日期和份额维度，不能按代码去掉不同日期的数据。
- 以 `schema` 中文字段名或响应 `titleMap` 展示。单位按具体接口定义；元／万元／亿元不得混用。华宝 `DYR` 样本返回约 `0.0438`，不能照搬南方百分比字段已乘 100 的规则；显示百分号前核对比例口径。
- 指数行业权重样本按月末提供，两天窗口空返时可在用户范围内检查月末快照。经理接口没有日期入参，不能声称按历史时点筛选经理。
- 回复末尾逐指标标注日期：行情常见 `DATA_DATE`／`TRADE_DT`／`TRADE_DATE`，估值 `TRADE_DATE`，持仓 `END_DT`／`DATA_DATE`，业绩 `TRADE_DATE`；公告日期单独解释。缺失日期时说明未知，不能凭查询区间推断。
- schema 没有的 FED／ROE 分位等不能冒充服务端提供；需要这些指标时回到入口路由。

已实测 `INF_FUND_PRT_SECDETAIL` 返回主动基金 `006567.OF` 在 `20260630` 的持仓。当前接口存在基金代码过滤，不代表所有主动基金均有数据；按具体基金、报告期和返回验证，不套用“全面不支持”或“完整覆盖”的结论。

完整接口样本与边界见[能力核验](../../references/capabilities.md)。`INF_INDX_CONSEC_WGHT.DATA_TYPE=4` 为月权重；1/2/3 仅文档声明覆盖华宝关注指数。`INF_INDX_CAP_DIRECT.NET_FLOW_IN` 单位为万，资金类型 STK 指成分股加权主力流。
