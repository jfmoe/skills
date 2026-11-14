# 接口语义目录（api-catalog）

> **选接口的唯一入口。每轮请求第一步读本文件。**
>
> 用「用户会怎么说」列按**语义**匹配用户意图 → 取该行 `api_id` → **再读 `references/apis/<api_id>.md`**
> 拿参数定义与口径，然后才构造请求。
>
> 详细文档路径恒为 `references/apis/<api_id>.md`（文件名 = `api_id` 原样，故下表不重复列路径）。
> 本文件刻意**不写参数、不写响应结构、不写示例**，以免两处漂移。路径均相对本技能目录。

## 怎么用

1. 按语义匹配。**那一列是"用户的话"，不是接口名**——别按接口名猜。
2. 命中多行时看「区别 / 注意」列消歧。
3. 取 `api_id`，读它的详细文档。**未读文档不得构造请求。**
4. 「区别 / 注意」列写了「先 resolve」等字样时，先按 `references/workflows/` 对应流程走。

## 前置：名称与代码口径解析

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 只给基金产品名称、需要把一种基金代码转换为目标接口口径 | `fund-resolve` | 只做有效披露名称/代码精确映射，不是公司、经理或指数解析；先读 `workflows/fund-code-resolution.md` |
| 只给指数名称、需要把一种指数代码转换为目标指数接口口径 | `index-resolve` | 只做指数名称/代码精确映射，不是基金、公司或经理解析；先读 `workflows/index-code-resolution.md` |
| 只给公司名称（全称/简称/拼音简称/英文名）、需要拿到企业编号 | `company-resolve` | 只做公司名称/编号精确映射，不是基金、指数或经理解析；先读 `workflows/company-code-resolution.md` |

## 一、基金基础与静态信息

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 这只基金什么类型、什么时候成立、谁管的、现在多大 | `fund-basic-info` | 只给静态档案；净值走 `fund-nav`、费率走 `fund-rate` |
| 管理费/托管费/申购赎回费率多少 | `fund-rate` | 只给费率，不含业绩与规模 |
| 分红过几次、每 10 份分多少、登记日/除息日 | `fund-dividend-history` | 只给已发生的历史分红，不含未来分红预期 |
| 最近几个报告期规模多大、是净申购还是净赎回 | `fund-asset-size` | 报告期序列；最新规模单值在 `etf-capital-report` |
| 某家基金公司旗下有哪些基金 | `fund-company-funds` | 入参是**公司内码** `companyCode` 不是基金代码；只有公司名称时先 `company-resolve` |

## 二、基金经理

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 用户**只说了经理姓名**（"张坤管哪些基金"） | `fund-manager-resolve` | 只做姓名→人，不单独成答；**先读** `workflows/manager-name-resolution.md` |
| 这位经理的学历、从业年限、在管规模、代表作 | `fund-manager-info` | 入参 `personalCode`；**先 resolve** |
| 这只基金历任经理是谁、各自任期回报 | `fund-manager-history` | 入参是**基金代码**，从基金看人；**无需**解析姓名 |
| 这位经理什么标签、获过什么奖、什么风格 | `fund-manager-tag` | 入参 `personalCodes` 数组（上限 50）；**先 resolve** |
| 这位经理管多少钱、规模这几年怎么变的、规模在同行排第几 | `fund-manager-scale` | **逐报告期规模序列 + 排名 + 全市场同类均值**；从**人**汇总，不是 `fund-asset-size`（产品规模）；**先 resolve** |
| 这位经理以前在哪家公司干过、跳槽几次、当基金经理多久、当时什么职务 | `fund-manager-experience` | **历任公司与任职履历**（起止日/时长/公司/职务），不含任期回报；从**人**看履历，不是 `fund-manager-history`（从基金看人）；**先 resolve** |
| 这位经理季报里怎么说的、怎么看后市、运作分析原文 | `fund-manager-viewpoint` | **报告观点原文**（运作分析 + 市场展望两段）；不是标签、不是规模；**先 resolve** |

## 三、净值、行情与业绩走势

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 这只 ETF 资金情况、场内份额与净申购、融资余额或近几日融资净买入 | `etf-capital-report` | 单只 ETF 资金报表；先 resolve 取得目标内码，见 `workflows/fund-code-resolution.md`；不是场内资金流向或市场聚合统计 |
| 这只 ETF 融资融券、融券余额/余量、融券净卖出或两融占流通市值比 | `etf-margin` | 单只 ETF 两融明细（融资买入/偿还、融券卖出/偿还、期末余额余量、占流通市值比）；先 resolve 取得目标内码；问「近N日融资净买入」「最新规模」改走 `etf-capital-report` |
| 这只 ETF 份额变动、份额变化率、规模较上期变动或份额变动原因 | `etf-shares-change` | 单只 ETF 份额/规模期间变动（份额、较上期变动、变化率(%)、规模、变动原因）；先 resolve 取得目标内码；问「最新份额/规模」改走 `etf-capital-report`，两融改走 `etf-margin` |
| 这只 ETF 跟踪指数的盈利预测、指数 EPS/营收/净利润预测或预测增长率 | `etf-earning-forecast` | 单只 ETF 跟踪指数盈利预测（预测年度、EPS/营收/归母净利润及同比、是否预测值）；先 resolve 取得目标内码；出的是指数层面预测，非基金自身财务指标；预测数据非承诺值 |
| 场内基金今天收盘多少、涨跌多少、成交额多大、停牌了吗 | `fund-daily-quote` | **场内交易行情**（≠净值）；入参 6 位场内代码；与 `fund-nav` 不同源 |
| 这只 ETF 这半年涨了多少、这段时间最高到过多少、区间日均成交额多大 | `etf-range-quote` | **区间聚合**（一行/基金）：区间涨跌幅/振幅/换手率/日均量额；与 `fund-daily-quote`（逐日明细）、`fund-nav-trend`（净值走势）口径不同 |
| 最新净值多少、累计净值多少、某段时间每天的净值 | `fund-nav` | 逐日净值序列，**支持自定义区间与统计周期**；入参是**基金内码**；要走势曲线用 `fund-nav-trend` |
| 这段时间净值怎么走的、画走势、区间涨了多少 | `fund-nav-trend` | **走势主接口**，可自定义区间、首日归零 |
| 跑赢**沪深300/某指数**了吗 | `index-performance-trend` | **补充接口，默认不调**；入参是**指数净码**；同上先读 workflow |

## 四、收益与风险指标

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 这只基金近一年/三年收益多少、回撤多大、夏普/卡玛/信息比率多少、同类排第几（**多指标一起问**） | `fund-return-risk` | **7 指标合并长表（dataservice 通道）**：一次返回 基金×指标×周期×计算日，含排名与二级分类；入参 `innerCodes` 或 `secuCodes`（**不是** `.OF` 后缀的 `fundCode`）；货币基金在 Sharpe/Calmar/Info/AnnualRisk 可 0 行属正常 |
| 近一年/三年收益多少、同类排名第几、跑赢基准吗 | `fund-stage-performance` | **固定区间枚举 + 带同类均值与排名** |
| 每月/每季度/每年收益明细 | `fund-monthly-return` / `fund-quarterly-return` / `fund-yearly-return` | **逐期**一行；季度按 1-3/4-6/7-9/10-12 月分组 |
| 这段时间累计收益多少、收益排名分位 | `fund-return-sum` | **多周期累计**（含排名）；与 `fund-stage-performance` 周期口径不同 |
| 最大回撤多少、历史最多亏多少 | `fund-max-dd` | **只给幅度，不给回撤起止日**；要起止日见 workflow |
| 回撤怎么走的、哪段时间回撤最深、画个回撤曲线 | `fund-drawdown` | **逐日序列**（不是单一幅度值）；区间只由 `beginDate`/`endDate` 表达，无快捷区间参数 |
| 夏普 / 卡玛 / 信息比率多少 | `fund-sharpe` / `fund-calmar` / `fund-info-ratio` | 三者**无量纲**，口径不同不可互替 |
| 年化收益多少 | `fund-annual-return` | 仅 **6 个年化周期**，无"今年来/成立来" |
| 年化波动率多大、年化风险多少 | `fund-annual-risk` | 是**波动率**不是回撤 |

> 上表中 `fund-stage-performance` / 三个逐期收益 / `fund-return-sum` / `fund-max-dd` / 三个比率 /
> `fund-annual-return` / `fund-annual-risk` 这 7 个指标接口**共享一套入参口径**（`fundCode` 带 `.OF` 后缀、
> 日期语义、周期集），**调用前先读** `workflows/return-risk-indicators.md`。`fund-drawdown` 的代码后缀与
> 日期口径同此（无周期集、无快捷区间参数），同样先读该 workflow。
>
> `fund-return-risk` 是这 7 个指标的**合并线上接口版**（一次出全部指标，入参改为 `innerCodes`/`secuCodes`），
> 与上述 7 个单指标接口**不共享** `fundCode` 入参口径；7 个线下单指标接口当前**暂停保留**，不要与本接口混调。

## 五、基金持仓、财报与估值

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 重仓了哪些股票、某只股票占净值多少、上季加了还是减了 | `fund-holding-detail` | **基金持股明细**（dataservice 直连）；入参 `fundObject` 是**基金内码**不是 GilCode，`poscharacter` 切重仓/全部持股；行字段**全小写 19 字段**，持股量万股 / 市值万元；先 resolve 取内码 |
| 都配在哪些行业、各行业占比多少 | `fund-industry-dist` | **逐行业明细**；`scope` 切全部持股/前十大 |
| 行业集中不集中、前五大行业占了多少 | `fund-industry-concentration` | **Top1~5 累计值**；`scope=report` 时 `induStandard` 必填 |
| 持仓的 PE/PB 多少、组合贵不贵、股息率多少 | `fund-valuation` | **持仓加权估值**（dataservice 直连）；入参 `innerCode` **内码单值** + 可选 `beginDate`/`endDate` 区间；先 resolve 取内码；行字段全小写 10 字段，市值（`totalmv`/`negotiablemv`）单位为**亿元** |
| 这期利润多少、期末资产净值多少、REITs 经营现金流 | `fund-fin-indicator` | **财务指标**；报告期只有四个季末 |
| 净值变动是经营带来的还是申赎带来的、期初期末净值 | `fund-nav-change` | **净值变动表科目**；入参是**基金内码** |

## 六、ETF 申赎与资金流

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 这只 ETF 能不能申购、最小申赎单位多少、现金差额多少 | `etf-pr-list` | **申赎要素卡片**（一基金一行）；入参**内码** |
| 申赎清单里有哪些成分股、某成分权重多少 | `etf-pr-components` | **成分股明细**；收盘价按上游前一交易日口径（A股/科创板含行情最大日截断）；入参**内码** |
| 这只 ETF 最近资金是流入还是流出、大单买了多少 | `etf-capital-flow` | **单只基金**逐日分档；⚠ 日期格式 `yyyyMMdd` |
| 今天全市场 ETF 净流入多少、股票型 ETF 流入多少 | `etf-capital-flow-stats` | **全市场汇总**（无基金入参）；五类合计与全市场不可互推 |

## 七、指数

| 用户会怎么说 | api_id | 区别 / 注意 |
|---|---|---|
| 沪深300 是哪家机构发布的、基期基点和编制方法是什么、多少只成分股、多久调整一次 | `index-basic-info` | **指数静态资料**（一行/指数：类型/基期基点/发布日期与机构/成份类型与数量/调整周期/加权方式/简介）；无任何行情字段，无日期入参；`indexObject` **只收内码**（先调 `index-resolve` 取 `innerCode`，传代码/净码会 400） |
| 沪深300 有哪些成分股、各占多少权重 | `index-constituents` | 入参 `indexObject[]` 聚源代码（`000300.SH`）或内码；逐股一行，含权重/行情/成交/股本市值/证监会行业 |
| 沪深300 今天收盘多少、涨了多少、成交额多大 | `index-daily-quote` | **逐日行情**（OHLC）；≤50 只/次 |
| 沪深300 这个月涨了多少、区间最高到过多少点 | `index-range-quote` | **区间聚合**（一行/指数）；⚠ `rangePCTBT` 是**点差**不是百分比 |
| 哪些基金跟踪沪深300、指数关联基金清单、跟踪误差多大 | `fund-index-related` | 按指数列**跟踪该指数的基金清单**（代码/简称、管理人、近一年收益与超额、跟踪误差、费率、最新规模、申赎状态）；入参 `indexCode` **必填指数内码**（如 `3145`）；只有名称/净码/聚源代码时先调 `index-resolve` 取 `innerCode`（与 `index-constituents` 的 `indexObject` 口径不同，勿混用） |

## 八、非本期接口（本技能不提供，勿调用）

未在本目录登记的接口一律视为本技能未提供。用户问到相关能力时**如实说明未提供**，
不要改调其它接口拼凑，也不要凭名称猜参数。
