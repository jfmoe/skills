# fund-manager-viewpoint

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-viewpoint` |
| 服务端登记名 | 基金经理观点 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

按**基金经理**维度返回其在定期报告里撰写的**观点原文**：逐行给出「经理 × 截止日期 × 管理基金 × 信息来源」，
正文分两段——**投资策略和运作分析**（`strategyanalysis`）与**基金市场展望**（`fundmarketprospect`）。

适用：用户问「某位经理在季报里怎么说的」「他上期怎么看后市」「这只基金的运作分析原文是什么」
「把几位经理的观点放一起对比」。

## 2. 不适用场景与易混接口

- **与 `fund-manager-scale` 的区别**：那个给**规模数字序列**（规模/排名/同业均值）；本接口给**文字观点**。
- **与 `fund-manager-info` 的区别**：那个给**档案**（学历、从业年限、代表作）；本接口给**原文表述**。
- **与 `fund-manager-tag` 的区别**：那个给结构化标签（能力/获奖/风格）；本接口给未结构化的报告文本。
- 两段正文由**同一个** `api_id` 返回，不要当作两个接口。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `personalCodes` | integer[]（兼容单值） | **是** | 基金经理**内码**列表（如 `[101019305]`），支持多位；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |
| `year` | integer | 否 | 年份（如 `2026`）；非整数 → 400；空 = 由上游缺省 |
| `beginDate` | string | 否 | 截止日期区间起，`YYYY-MM-DD`；格式非法 → 400 |
| `endDate` | string | 否 | 截止日期区间止，`YYYY-MM-DD`；格式非法 → 400；与 `beginDate` 均空 = 由上游缺省 |
| `infoSourceCodes` | integer[]（兼容单值） | 否 | 信息来源编码列表，取值见下方速查表；非正整数 → 400；空 = 不过滤（六类全出） |

**`infoSourceCodes` 取值速查**（唯一权威；本接口只认这 6 个编码，不传 = 全部）：

| 值 | 含义 |
|---|---|
| `110101` | 年度报告 |
| `110102` | 半年度报告 |
| `110103` | 第一季报 |
| `110106` | 第二季报 |
| `110104` | 第三季报 |
| `110107` | 第四季报 |

> ⚠ 编码**不按序号递增**：第二季报是 `110106`（不是 `110105`），第三季报是 `110104`。按序号类推必错。
> ⚠ 上游只认上表 6 个编码；传其它编码**不报错**，但会被静默丢弃 → `200` + `recordCount=0`。
> 「两个季报（如第一季报 + 第三季报）」这类组合按值列举，例如 `[110103,110104]`。

> `personalCodes` 要的是**经理内码**，不是姓名、也不是基金代码。
> 只有姓名时先用 `fund-manager-resolve` 解析出 `candidates[].personalCode` 再调用本接口。

## 4. 调用示例

```bash
# 单经理最新观点（不传信息来源 = 六类全出）
pixi run etf-htbr invoke fund-manager-viewpoint '{"personalCodes":[101019305]}'
# 限定年份 + 信息来源（只看半年报与年报，含义见 §3 速查表）+ 截止日期区间
#   日期为占位，须替换成 yyyy-MM-dd 实际值，原样传会 400
pixi run etf-htbr invoke fund-manager-viewpoint '{"personalCodes":[101019305],"year":2026,"beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd","infoSourceCodes":[110102,110101]}'
# 多经理对比（同一截止日期的观点）
pixi run etf-htbr invoke fund-manager-viewpoint '{"personalCodes":[101019305,101014016]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 经理 × 截止日期 × 管理基金 × 信息来源 |
| `records[].personalobject` / `records[].personalname` | 经理内码 / 姓名 |
| `records[].enddate` | 截止日期（`YYYY-MM-DD`） |
| `records[].innercode` / `records[].secucode` / `records[].secuabbr` | 管理基金内码 / 代码 / 简称 |
| `records[].infosource` / `records[].infosourcecode` | 信息来源中文描述（形如 `定期报告:年度报告`）/ 编码（见 §3 速查表） |
| `records[].strategyanalysis` | 投资策略和运作分析（原文全文） |
| `records[].fundmarketprospect` | 基金市场展望（原文全文） |

## 6. 数据口径

- **一行 = 经理 × 截止日期 × 管理基金 × 信息来源**：同一经理同一期在管的每只基金各一行，正文按行重复；
  不要跨行合并成一行，也不要去重。
- **正文为原文全文**：`strategyanalysis` / `fundmarketprospect` 是定期报告披露文本，未经摘要与改写；
  引用时按原文，需要节选请明确标注「节选」。
- **`infosource` 是中文描述、`infosourcecode` 是编码**：展示用前者，过滤用后者（`infoSourceCodes` 就是按编码过滤）；
  中文值带来源前缀（如 `定期报告:年度报告`），对外转述时可简写为「2026 年年度报告」。
- **可取的编码只有 6 个**（`110101`/`110102`/`110103`/`110106`/`110104`/`110107`，含义见 §3 速查表）：
  上游对其它编码一律静默丢弃，本平台不报错也不补数。
- **`year` 与 `beginDate`/`endDate` 可并存**：三者各自下推上游，同时传不报错，由上游决定取舍。
- 截止日期通常是季报/半年报/年报的报告期末日。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `personalCodes` 缺失/空/非内码、`year` 非整数、日期格式非法、`infoSourceCodes` 含非正整数 —— 补齐/纠正参数 |
| 200 + `NO_DATA` 注记 | 经理内码无法解析，或该区间内没有观点记录 —— 如实说明无数据 |
| 200 + `recordCount=0`，但仅传了某个信息来源编码 | 该编码不在 §3 速查表内（被上游静默丢弃）—— 改用表内 6 个编码之一重试 |
| `strategyanalysis` / `fundmarketprospect` 为空字符串 | 该期报告未披露对应段落，不是取数失败 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `personalCodes` 必须是**经理内码**；只有姓名先走 `fund-manager-resolve`。
- 正文较长（单行可达数千字），多经理多期批量调用时注意结果体积，按需用 `year`/日期区间收窄。

## 9. 相关工作流

- 只有经理姓名、没有内码 → 先读 `workflows/manager-name-resolution.md`，用 `fund-manager-resolve` 取 `personalCode`。
- 想看经理规模与排名 → `fund-manager-scale`；档案 → `fund-manager-info`；标签 → `fund-manager-tag`。
