# 华泰柏瑞 ETF 数据网关

华泰柏瑞基金提供的基金与指数数据接口，数据来自恒生聚源（响应 `meta.dataSource` 为 `gildata-jydb` 或 `dataservice`）。覆盖不限于 ETF：主动基金的持仓、行业分布、经理资料同样可查。客户端在本目录 `scripts/htbr_client.py`，只用标准库；凭据与环境见[配置说明](../../references/setup.md)。在 Fire 项目中用 `pixi run etf-htbr`。

## 调用

```bash
pixi run etf-htbr invoke fund-resolve '{"secuCode":"510300"}'
pixi run etf-htbr invoke etf-earning-forecast '{"innerCode":16930,"beginDate":"2026-10-14","endDate":"2026-11-13"}'
```

其他环境把 `pixi run etf-htbr` 换成 `python <技能目录>/providers/htbr/scripts/htbr_client.py`，并设置 `HTBR_API_KEY`。客户端先用密钥换短期令牌（缓存在本目录 `.cache/`），再调用 `/business/<api_id>:invoke`；成功时打印完整响应并以 0 退出，失败时把 HTTP 状态和网关错误写到标准错误并以 1 退出。

1. 在[接口目录](references/api-catalog.md)按需求找到 `api_id`，再读 `references/apis/<api_id>.md` 确认参数、代码口径和字段含义。目录和接口文档是上游原文，只列实测可用的接口。
2. 先解析代码。接口要的代码口径各不相同：六位证券代码（`510300`）、带后缀代码（`510300.OF`、`000300.SH`）、内码（`16930`）、经理编号、公司编号。只有名称或口径不符时，按 `references/workflows/` 里对应的解析流程先调 `fund-resolve`、`index-resolve`、`company-resolve` 或 `fund-manager-resolve`；多个候选时请用户选择，不按第一条取。
3. 序列接口只取需要的日期区间；日期格式以接口文档为准，`etf-capital-flow` 和 `etf-capital-flow-stats` 用 `yyyyMMdd`，其余多为 `yyyy-MM-dd`。
4. 读响应的 `success`、`data` 和 `meta`。`meta.degraded` 为真或 `meta.warnings` 非空时如实说明；空记录不等于数据不存在，先核对代码口径和日期。

上游文档里的 `<SKILL_DIR>`、`config.py`、`api_client.py`、安装与更新步骤指的是官方包自身，本技能不使用；凭据只来自 `HTBR_API_KEY`。

## 额度与节奏

- 每个密钥每天 500 次成功调用，北京时间 0 点重置；认证失败不计数。响应的 `meta.quota` 实测为空，客户端无法查询剩余额度，需要自己计数。
- 上游建议调用间隔不少于 3 秒。多数接口 1 秒内返回，少数（`fund-basic-info`、`fund-nav-change`、`etf-pr-components`）实测 20—90 秒。
- 429 表示额度用完，当日不再调用。

## 独有或更强的能力

| 需求 | 接口 | 实测情况（2026-11-14） |
|---|---|---|
| ETF 跟踪指数的盈利预测 | `etf-earning-forecast` | 每个自然日一组，含上一年实际值和未来三年预测的 EPS、营收、归母净利润及同比；历史从 2024 年某日开始，2024-01 无数据、2025-01 有数据 |
| 基金全部持股的行业分布 | `fund-industry-dist` | 中报、年报可按全部持股给出申万一级行业占比；006567 的 2026 年中报返回 17 个行业 |
| 基金经理定期报告观点原文 | `fund-manager-viewpoint` | 按经理返回其全部产品历次季报、中报、年报的运作分析和市场展望；姜诚返回 402 条，报告期自 2014 年起 |
| 基金持仓加权估值 | `fund-valuation` | 逐报告期的持仓 PE-TTM、PB、股息率 |
| 基金历史分红明细 | `fund-dividend-history` | 每次分红的每 10 份金额、登记日、除息日、发放日 |
| 指数成分与权重 | `index-constituents` | 单个截止日的全部成分，含权重、市值和证监会二级行业；查历史需逐日调用 |
| 名称与代码精确映射 | 四个 resolve 接口 | 基金、指数、公司、经理 |

盈利预测在 2025 年度由“预测”变为“实际”的日期是 2026-04-30（年报披露截止日），说明序列按当时可得的信息逐日保存。这不能证明历史值从未修订；用于回测前见所在项目对时点数据的要求。

## 已登记但未开放的接口

上游文档登记了 72 个接口，其中 20 个实测返回 404 `API_NOT_FOUND`，不要调用，也不要改用其他接口拼凑：

- 基金经理 13 个：评分画像、阶段收益及排行、逐期收益、风险收益、逐产品收益、行业分布、行业集中度、持股明细、持股集中度、持债集中度、持股反查基金、概念持仓。
- 指数 7 个：行业分布、多周期行情、估值分析、收益风险指标、PE 估值带、两融、分档资金流。

逐个接口的状态见 [availability.json](references/availability.json)；重新核对的方法见[维护说明](../../references/maintenance.md)。指数行业分布可以用 `index-constituents` 返回的证监会二级行业自行聚合，口径不是申万。
