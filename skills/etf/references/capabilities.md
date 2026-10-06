# CLI 与脚本能力核验

核验日期：2026-10-03。南方运行时为 ETFirst 0.4.2；华宝使用包内客户端和当日刷新得到的 17 个接口元数据。以下是有限样本，不是全市场覆盖或精度基准。仅华宝官网用于确认品牌，文章中的案例不作为接口已验证的替代。

## 源码与命令证据

- ETFirst 的 `etfapp/core/index_detail.py:aggregate`、`core/product.py:aggregate_etf`／`aggregate_otc` 都只向服务端聚合接口发一次 POST，随后透传各子结果。子接口数量不是客户端网络往返次数。
- `etfirst etf-detail all --help` 和 `otc-detail all --help` 的 `--date-range` 为 INTEGER；字符串 `1m` 等不是合法 CLI 参数。具体整数含义未确认时使用起止日期。
- 华宝包内 `scripts/etf_index.py` 的 `call` 获取 registry 后发送一次业务 POST；缓存有效期内无需再次获取元数据。业务码失败仍可能退出 0，因此必须检查 JSON。
- 华宝 schema 的多代码、管理人、日期和 `_members` 是接口参数；支持参数不等于所有代码均有数据。

## 成功的样本调用

华宝命令形式为 `pixi run etf-fsfund call PATH 'JSON'`，这些样本均返回业务码 `0000`。

| 能力 | PATH 与请求 | 实际结果 |
|---|---|---|
| 主动基金持仓 | `INF_FUND_PRT_SECDETAIL`，`FUND_WINDCODE=006567.OF`，`STDATE=ENDDATE=20260630`，`currentPage=1` | 返回 39 行持券明细，基金代码及报告期匹配；不将 39 行直接称为十大股票 |
| Alpha、Beta、信息比率 | `INF_FUND_PERF`，`FUND_WINDCODE=510300.SH`，`STDATE=ENDDATE=20260811` | 返回 1 行，多个 `ALPHA_*`、`BETA_*`、`INFO_RATIO_*` 字段非空 |
| 全收益指数历史价格 | 先以 `INF_INDX_INFO`、`INDX_SNAME_LIKE=中证红利全收益` 确认 `h00922.CSI`；再 `INF_INDX_PRICE`，该代码、`STDATE=20230810`、`ENDDATE=20230811` | 返回两个历史交易日及收盘价；该样本的股息率为 null，不证明三年连续完整 |
| PS／PCF／股息率序列 | `INF_INDX_INFO` 确认 `INDX_CODE=000922` 对应 `000922.CSI`；`INF_INDX_VALUATION`，该代码、`STDATE=20260810`、`ENDDATE=20260811` | 返回两日 `PSR_TTM`、`PCF_TTM`、`DYR` 等非空字段 |
| 多代码与管理人服务端交集筛选 | `INF_FUND_INFO`，`FUND_WINDCODE=510300.SH,510500.SH`、`FUND_MGR=南方`、`currentPage=1` | 只返回 `510500.SH`，管理人为南方基金 |

南方 `etfirst --json etf-detail all --product-code 510300 --start-date 20260810 --end-date 20260811` 与 `index-detail all --index-code 000922 --index-type 1 --start-date 20260810 --end-date 20260811` 均成功，`_errors` 为空。ETF 返回 11 个子结果，指数返回 9 个；两者有 `getRealTimeData`、交易日及时刻，净流入序列匹配指定两日。指数综合详情返回 PE/PB、分位、ROE 等非空字段。本次处于非交易时段，未实测 5 秒刷新速度。

## 已发现的限制

- 华宝误传 `000922.SH` 时，估值接口业务成功但返回空列表；正确 `.CSI` 代码能返回数据。空响应先核对代码，不能立刻归为覆盖缺失。
- 南方指数估值 `list` 不遵守本次两日起止范围，返回 2611 行、从 `20160104` 至 `20260930`；相同请求的资金流却按范围返回。子结果必须分别检查。
- 南方实时行情原始价格与字段文档单位不一致，CLI 无统一转换。详见[数值核验](../providers/etfirst/references/presentation.md)，未确认缩放前不直接输出原始数值为价格。
- 南方 FED 的所有产品覆盖、华宝全市场分页完整性、底层数据供应商或整体准确率未核实。指数 ETF 合计净流入已有六产品两日交叉核验，仍有文档口径冲突。额度按用户提供的信息视为两家不限额度，不将其表述为独立验证过的官方保证。不得将这些写成已验证能力或保证。

## 完整接口覆盖

下表所有接口已发起实际调用并取得非空业务样本；它只证明指定对象和区间可用，不保证全市场、全历史完整。F=510300.SH，I=000922.CSI；日区间 D=20260810–20260811，季度 Q=20260630，月区间 M=20260801–20260831。每个接口的最终参数仍由动态 schema 确认。

| 华宝接口 | 对象／范围与结果 | 关键边界 |
|---|---|---|
| INF_FUND_INFO | 两基金代码+南方管理人交集返回 1 行；沪深300联接筛选返回 71 行 | IS_ETF_LINK=1-是；基金代码列可能 null，使用 FUND_WINDCODE 标识；有申赎状态 |
| INF_FUND_NAV | F、D，pageSize=1 的第1/2页各1行，总数2，日期不同 | 分页生效；ASSET_NAV 与合计行不同；NAV 无独立当日份额数量字段 |
| INF_FUND_PRICE | F、D，同样验证两页；9月30日另返回日价格及复权价格 | 当日份额在 FUND_SHARE；两种价格口径分开 |
| INF_FUND_PERF | F、20260811，1行 | Alpha/Beta/信息比率非空，很多字段缺缩放声明 |
| INF_FUND_MGR_INFO | F，2行 | 无日期入参，不能回放历史经理时点 |
| INF_FUND_PRT_ASSET | F、Q，5行 | 资产类型和总资产／净资产比例不能混合累加 |
| INF_FUND_PRT_SECDETAIL | F、Q，339行；主动基金006567.OF、Q，39行 | 是持券明细，不等同十大股票；按证券类型筛选 |
| INF_FUND_PRT_INDS_RATIO | F、Q，14行 | 无分页入参；日期字段的披露／报告语义需核对 |
| FUND360_DATA | F、Q，不传_members返回8类子结果且均成功 | 指定NAV+PRICE则仅2类；逐子项读取total，外层total=0不表示无数据 |
| INF_INDX_INFO | 确认中证红利及全收益代码 | 000922.CSI、h00922.CSI；错误后缀可能只空返 |
| INF_INDX_PRICE | 全收益h00922.CSI、20230810–11，2日收盘 | 股息率字段为null；I、M另返回21行行情 |
| INF_INDX_CONSEC_WGHT | I、M、DATA_TYPE=4，100行 | 是月权重；其他3种类型覆盖和返回未实测 |
| INF_INDX_VALUATION | I、D，2行；M，21行 | PS/PCF/股息率非空；无分页入参 |
| INF_INDX_INDS_TYPE | I，1行 | 无日期与分页入参 |
| INF_INDX_CAP_DIRECT | I、D，2行；M，21行 | NET_FLOW_IN元数据单位万；STK主力口径，不是ETF申赎 |
| INF_INDX_INDS_RATIO | I、D为空；扩大到M后28行，日期8月31日 | 该样本是月末快照，短窗口空返不是不支持 |
| INDX360_DATA | I、M，7类子结果全部成功 | 仅选PRICE+VALUATION则2类；无pageSize参数 |

### 南方覆盖及边界

- 分类 `clas --type 2` 成功；列表 type=1/2/3 均有样本。沪深300 ETF 以 pageSize=1 查询前两页各一条，以 pageSize=100 一次返回全部30条；不能将上游“常见每页只有5条”当固定服务上限，完整性仍按 totalRows 与实际条数判断。
- 指数／ETF／场外详情分别返回9／11／9个子结果；场外460300可返回持仓结构、其它份额和关联指数。空 `_errors` 之外还需检查预期子项是否存在。
- `type=3` 的460300列表样本也返回yield，但没有ETF价格／成交额／溢折率字段。不能认定所有yield都是实时行情。
- 指数 `queryIndustryDistribution` 样本为10行成分，`queryCompanyWeight` 为三级行业；日期为最近快照，不随请求历史区间改变。全部历史成分权重优先华宝。
- `getReturnTrendList` 的map键分别指产品与指数，closePrice含义随实体不同；回撤样本为正，成交金额单位尚未确认。不能套用普通行情字段的单位。
- 中证红利ETF列表为6只，逐产品默认type=3净流入在两日的亿元合计为 -2.607533 和 3.110250；指数 `--net-inflow-type etf` 对应 -2.61 和 3.11，样本吻合到两位小数。某ETF `--net-inflow-type 2` 也返回所跟踪指数的合计流入。保留产品范围和舍入差异。

### 失败语义

华宝 `INF_FUND_PRICE` 仅传 FUND_CODE 和 currentPage，省略必填日期，返回业务码 A2099（STDATE必填），但脚本退出码仍是0。行情查询错用000922.SH则可能业务成功、结果为空。两类情况都不能靠进程退出码判断数据可用。

### 未做的保证

不限额度不意味着不限响应大小、无限并发或不存在服务端超时。未进行压力测试、全市场全历史下载、准确率排名或交易时段刷新频率基准。完整梳理指覆盖所有当前接口及核心边界，不是穷举所有参数组合和产品。
