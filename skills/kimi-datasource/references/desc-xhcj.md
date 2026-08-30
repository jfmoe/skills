# xhcj

**Description:** 新华财经(CNFIC)公告、新闻、政策数据

## Available APIs

### get-las-vector

**Description:** 政策关键字查询

**Optional Parameters:**
- `keyword` (string): 关键词
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

---

### get_xhcj_hotNews

**Description:** 得到新华财经热点新闻，可按更新时间范围筛选

**Optional Parameters:**
- `begTime` (string): 开始时间（更新时间），格式如 2025-04-01 00:00:00
- `endTime` (string): 结束时间（更新时间），格式如 2025-04-10 23:59:59

---

### search_prodinfo

**Description:** 搜索资讯成品稿，支持多条件筛选

**Optional Parameters:**
- `title` (string): 标题
- `contentTxt` (string): 正文内容
- `tagName` (string): 标签名称
- `IfProd` (string): y/n,y为新华财经签发稿件，n为互联网数据

---

### get_newsflash_Commodities

**Description:** 大宗快讯

**Optional Parameters:**
- `Title` (string): 资讯标题
- `ExternalSource` (string): 稿件来源
- `news_type` (string): 资讯类型
- `startdate` (string): 开始日期
- `enddate` (string): 结束日期

---

### get_AStock_News_byStockName

**Description:** 根据股票名称提取股票资讯

**Optional Parameters:**
- `stockName` (string): 股票名称

---

### xhcj-mcp-announce-search

**Description:** 公告关键词查询

**Optional Parameters:**
- `keyword` (string): 关键词
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期
- `topN` (integer): 返回前N(1-100) (default: 10)

---

### get_newsflash_foreign_currency

**Description:** 外汇自动报价快讯

**Optional Parameters:**
- `Title` (string): 资讯标题
- `ExternalSource` (string): 稿件来源
- `startdate` (string): 开始日期
- `enddate` (string): 结束日期

---

### search_prodinfo_stockSector_news

**Description:** 新华财经成品稿板块资讯搜索，支持按时间、标题、内容、标签筛选

**Optional Parameters:**
- `begTime` (string): 开始时间
- `endTime` (string): 结束时间
- `title` (string): 标题
- `contentTxt` (string): 正文内容
- `tagName` (string): 标签名称

---

### get_newsflash_stock

**Description:** 股票快讯

**Optional Parameters:**
- `Title` (string): 资讯标题
- `ExternalSource` (string): 稿件来源
- `news_type` (string): 资讯类型
- `startdate` (string): 开始日期
- `enddate` (string): 结束日期

---
