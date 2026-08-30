---
name: kimi-datasource
description: |
  通用数据源助手，适用于股票（Wind、S&P、SEC EDGAR）、宏观数据（世界银行、IMF、FRED、国家统计局）、中国政府数据与标准（GB/HB/DB/TT）、企业、学术、法律、WHO/FAO/OECD 等国际组织数据，以及新华财经、财新等财经资讯。
  本 skill 通过内置 CLI 调用 Kimi 数据源，优先读取缓存 schema；有 schema 证据时执行 `desc` 刷新，再通过 `call` 取数。
---

# kimi-datasource — 通用数据源助手

## 0. 调用方式

解析本 skill 目录，将 `scripts/kimi-datasource.mjs` 的绝对路径记为 `CLI`。要求 Node.js >= 18.17；脚本缺失时报告安装不完整。

- `node "$CLI" desc <source> --quiet`：获取一个数据源的当前接口说明
- `node "$CLI" call <source> <api> --json '<params>'`：调用说明中的接口

`call` 也支持通过 `--json-file <path|->` 从文件或标准输入读取 JSON 参数。

CLI 会读取当前 Kimi Code 环境对应的本地 OAuth 登录凭据；当设置了 `KIMI_CODE_OAUTH_HOST` / `KIMI_CODE_BASE_URL` 时，会使用对应环境的隔离凭据。如果没有登录凭据，让用户先在 Kimi Code 里执行 `/login`。

## 1. 这个 skill 提供什么能力

本 skill 后面挂了 25 个外部数据源。每一行的"数据源名"就是传给 `desc` 和 `call` 的 source。

| 能力域 | 数据源名 | 典型问题 |
|---|---|---|
| **A股 / 港股 / 美股 行情和财务** | `stock_finance_data` | "茅台现在多少钱"、"宁德时代 2024 年财报"、"腾讯股东"、"杭州的人工智能股票" |
| **Yahoo Finance 全球金融** | `yahoo_finance` | "苹果分析师评级"、"AAPL 期权链"、"苹果前十大机构股东" |
| **世界银行历史宏观** | `world_bank_open_data` | "中国历年 GDP"、"印度通胀率"、"各国人口增长对比" |
| **中国企业工商信息** | `tianyancha` | "字节跳动股东"、"比亚迪司法风险"、"宁德时代专利" |
| **arXiv 论文预印本** | `arxiv` | "找 RAG 综述"、"下载 2406.xxxxx" |
| **Google Scholar 学术搜索** | `scholar` | "Hinton 最新论文"、"transformer 综述高引文献" |
| **中国法律法规 / 司法案例** | `yuandian_law` | "民法典关于居住权的规定"、"帮我查劳动合同解除的相关法条"、"找几个不当得利的判例" |
| **Wind 万得（A股/基金/债券/宏观）** | `wind` | "茅台今天的分钟线"、"十年期国债收益率走势"、"基金净值查询" |
| **IMF 国际宏观（汇率 / CPI / 预测）** | `imf` | "美元兑人民币汇率"、"各国 GDP 增速预测"、"全球通胀率对比" |
| **恒生聚源智能筛选** | `gildata` | "筛选净利润增速超 30% 且 ROE 大于 15% 的股票"、"基金经理筛选" |
| **美股 SEC 披露文件** | `sec_edgar` | "特斯拉 10-K 年报"、"苹果 10-Q 季报"、"Form 4 内部人交易"、"13F 机构持仓" |
| **S&P Capital IQ 美股基本面** | `sp_data` | "苹果分析师一致预期"、"美股估值比率对比"、"竞争对手关系" |
| **中国政府开放数据目录（国家数据局）** | `china_nda` | "全国公共数据资源登记目录里有什么"、"各省开放数据平台有哪些数据集" |
| **国家统计局宏观指标** | `china_nbs` | "中国历年 GDP 官方口径"、"各省市人口与就业统计"、"社会消费品零售总额" |
| **中国标准查询（国标 / 行标 / 地标 / 团标）** | `china_standards` | "查 GB 国家标准全文"、"某行业的现行行业标准" |
| **WHO 全球健康** | `who` | "全球婴儿死亡率"、"各国预期寿命" |
| **FAO 农业粮食** | `fao` | "各国粮食产量"、"农产品价格" |
| **联合国统计司 UNdata** | `unsd` | "联合国成员国统计年鉴表"、"国际贸易统计" |
| **欧洲央行统计** | `ecb` | "欧元区基准利率"、"欧元区货币供应量" |
| **欧盟统计局** | `eurostat` | "欧盟各国失业率"、"欧元区 CPI" |
| **联合国儿童基金会** | `unicef` | "全球儿童营养指标"、"儿童免疫接种率" |
| **OECD 数据** | `oecd` | "OECD 国家 GDP 对比"、"成员国教育支出" |
| **FRED 美国/全球宏观** | `fred` | "美国 CPI 长时间序列"、"联邦基金利率走势" |
| **新华财经新闻公告** | `xhcj` | "新华财经快讯"、"A 股公司公告"、"行业政策新闻" |
| **财新数据库** | `caixin` | "财新数据接口检索"、"财新新闻与数据" |

### 选源原则

1. **用户点名了数据源** → 直接用指定的源。
2. **没点名** → 按能力域从上表选最匹配的一个；结合下面的"能力边界参考"和用户问题的深度、范围自行判断。
3. **一次简单查询只选一个数据源**，不要并行读取其他源的 desc。选定的源成功返回且已经覆盖用户问题后，立即回答；不要为了补充字段、重新格式化或交叉验证继续调用其他 API。只有用户明确要求跨源对比时，才能查询第二个数据源。

### 能力边界参考（客观事实，选源时考虑）

- `yahoo_finance` 的外汇历史最多 2 年；`imf` 提供长期的汇率、CPI、GDP 预测和国际收支序列
- `stock_finance_data` 的行情是实时/收盘快照；分钟级分时序列在 `wind`（另有基金、债券、国债收益率）
- 股东 / 机构持仓：`yahoo_finance`、`sec_edgar`（13F）、`sp_data`（S&P 标准化持有人）都覆盖，口径和深度不同
- `world_bank_open_data` 是 50 年以上的历史宏观序列；要 IMF 的预测值用 `imf`
- `gildata` 的查询输入是自然语言条件（选股 / 选基金 / 基金经理筛选），`tianyancha` 是企业工商档案
- `wind` 的 `indexes`/`indicators` 参数要求 Wind 原生字段名；PE/PB/ROE/总市值这类常用字段先调 `wind_search_fields` 映射（支持别名和中文，一次查一个），不要硬猜字段名
- 中国官方统计口径：`china_nbs` 是国家统计局宏观指标序列（GDP / CPI / PPI 等，全国 / 省 / 主要城市），`china_nda` 是国家数据局的开放数据目录（回答"有什么数据集可用"）；`world_bank_open_data` 和 `imf` 是国际口径的历史与预测序列
- WHO、FAO、UNSD、ECB、Eurostat、UNICEF、OECD、FRED 各自是独立数据源，按机构名直接选；IMF 自己的数据集（汇率 / CPI / GDP 预测）走 `imf`
- 国家标准（gb）、行业标准（hb）、地方标准（db）、团体标准（tt）查 `china_standards`；法律法规与判例在 `yuandian_law`，别混
- 新华财经（`xhcj`）偏公告 / 快讯 / 政策新闻；`caixin` 覆盖 600+ 财新数据接口，先用它的 `caixin_api_search` 找合适接口再调用

**不支持的能力**：通用 Web 搜索，以及 `xhcj` / `caixin` 覆盖之外的实时新闻。

## 2. 标准工作流：缓存 schema → `call`

后端可用 API 经常会调整。本 skill 为每个数据源缓存一份接口说明，默认读取缓存，只有出现 schema 证据时才调用 `desc` 刷新。

```
1. 根据用户问题，从上表只挑一个 data_source_name
2. 只读取 `references/desc-<source>.md`
3. 仔细读返回的 Markdown，里面列了：
     - 该数据源整体说明（含 ticker 格式、全局约束）
     - 每个 API 的描述 / 必填参数 / 可选参数 / 默认值 / 取值范围
4. 选最匹配的 API，按文档拼 params
5. 执行 `node "$CLI" call <source> <api> --json '<params>'` 取数；需要先发现接口 / 字段 / 实体的源（caixin_api_search、wind_search_fields、天眼查公司搜索），发现类调用不受“一次”限制，继续调到真正的取数 API。结果成功且已经覆盖问题时停止调用
6. 读返回结果，用用户提问时使用的语言回答
```

### 刷新过期缓存

只有以下情况属于 schema 证据：缓存文件缺失、用户明确要求最新 schema、用户需要的能力不在缓存中，或后端返回结果与缓存记录的 API / 参数冲突。认证失败、配额不足、空数据和普通运行错误不属于 schema 证据。

需要刷新时，把 `node "$CLI" desc <source> --quiet` 的输出写入目标 reference 同目录的临时文件。命令成功且文件非空后，再移动覆盖 `references/desc-<source>.md`；随后重新读取缓存、重建参数，并把失败的数据调用重试一次。发现失败时保留原缓存。

### 例 1：用户问"茅台最近一年走势"

1. 股票走势 → `stock_finance_data`
2. 读取 `references/desc-stock_finance_data.md`

3. 从文档里找到"获取历史价格"那个 API，看它要 `ticker / start_date / end_date / file_path` 等
4. 用 web_search 核对 → 茅台 = `600519.SH`
5. 执行 `node "$CLI" call stock_finance_data <文档里的API> --json '{"ticker":"600519.SH","start_date":"...","end_date":"...","file_path":"/tmp/mao_1y.csv"}'`

### 例 2：用户问"找几篇 retrieval augmented generation 的综述"

1. 论文搜索 → `arxiv`（或 `scholar`，arxiv 更适合预印本，scholar 引用更全）
2. 读取 `references/desc-arxiv.md`

3. 从文档里找到搜索类 API，看它要 `query / file_path / max_results` 等
4. 执行 `node "$CLI" call arxiv <文档里的API> --json '<params>'`

### 例 3：用户问"字节跳动有哪些股东"

1. 企业工商 → `tianyancha`
2. 读取 `references/desc-tianyancha.md`

3. 注意：tianyancha 的 API 是动态注册的，文档会指引你**先用搜索类接口找到合适的 API 名，再调用**
4. **必须使用企业全称**（"北京字节跳动科技有限公司"），不要用简称。不知道全称就先用 tianyancha 文档里的"公司搜索"接口查

## 3. 调用前的几条铁律

### 3.1 股票代码必须核对，不能凭记忆猜

A 股 `.SH/.SZ/.BJ`，港股 `.HK`，美股 `.US` 等。用户通常只说中文名（"茅台"、"宁德时代"、"腾讯"），不会给代码。

**调任何股票相关 API 前**，先用 `web_search` / `WebSearch` 一类联网工具确认正确代码 + 后缀。

如果当前环境没有任何联网工具，**让用户亲口确认代码**，不要硬猜。错了的话接口会静默返回错数据或空数据。

### 3.2 企业相关查询必须用全称

`tianyancha` 拒收"特斯拉"、"网易"、"腾讯"这种简称，必须给"北京特斯拉销售有限公司"这种全名。不知道全名时，先调它的公司搜索 API。

### 3.3 多数 API 需要 `file_path`

绝大部分数据源 API 把完整结果以 CSV 形式写到 `file_path`。漏传会报 `Missing required parameters: file_path`。不知道传啥时，给一个 `/tmp/<场景>_<时间戳>.csv` 即可。

### 3.4 一次调用不要堆太多 ticker

`stock_finance_data` 的实时接口最多 3 个 ticker，历史接口最多 10 个。超过会被截断或报错。多了就分批调。

## 4. 怎么读返回结果

`call` 命令的标准输出一般含两段：

1. **`data_preview`**：CSV 头 + 前几行（通常 1~3 行），方便你直接答简单问题
2. **`CSV 数据已写入：/tmp/xxx.csv`**：完整数据落盘路径

策略：
- 用户只问"XX 现在多少钱"、"中国 2023 GDP 多少"这种单值 → `data_preview` 一般够，直接答
- 用户要画图、对比、算盈亏、列清单 → 用 `Read` 工具把 CSV 读出来再处理
- 混合 A+港股查询时服务端会自动把 CSV 拆成 `_a.csv` / `_hk.csv` 两份，原 `file_path` 那个文件不存在

如果接口返回失败，提示文字一般会写明原因（参数不对 / 不支持 / 数据空等）。把人话原因反馈给用户，不要硬走第二次。

## 5. 注意事项

- **回答用户时，使用用户提问时使用的语言**。如果用户用中文问，就用中文答；如果用户用英文问，就用英文答；用其他语言问，就用其他语言答。
- **不要凭记忆猜股票代码 / 企业全称**。错代码会让接口静默返回错数据，用户察觉不到
- **不要在没读缓存说明或本次会话的刷新结果时硬传 `api_name`**。后端会报 `API_NOT_FOUND`
- 如果某个数据源接口返回的报错明显是后端 bug（参数 schema 自相矛盾、内部 Python 报错等），**汇报错误给用户，不要硬试**——这种 bug 我们这边修不了，要后端服务侧改
