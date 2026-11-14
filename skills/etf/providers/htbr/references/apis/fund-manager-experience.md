# fund-manager-experience

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-experience` |
| 服务端登记名 | 基金经理历任公司 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |

## 1. 功能与适用场景

按**基金经理**维度返回其**历任公司**（逐段任职经历）：逐行给出「经理 × 一段任职经历」，含任职起止日期、
任职时长、任职公司与公司性质、职务。

适用：用户问「这位经理以前在哪家公司干过」「他做基金经理多久了」「他跳槽过几次」
「他之前是研究员还是基金经理」「某公司在某段时间有哪些基金经理」。

## 2. 不适用场景与易混接口

- **与 `fund-manager-history` 的区别**：那个从**基金**看人（这只基金的历任经理 + 各自任期回报）；本接口从**人**看履历，不含回报。
- **与 `fund-manager-info` 的区别**：那个给**档案单值**（学历、从业年限、在管规模、代表作）；本接口给**逐段经历明细**。
- **与 `fund-manager-scale` 的区别**：那个给规模时间序列；本接口给任职履历。
- **与 `fund-manager-viewpoint` 的区别**：那个给定期报告观点原文。
- 本接口**不含管理基金清单**，问「他管过哪些基金」用 `fund-manager-history` 或 `fund-basic-info`。

## 3. 请求参数

| 参数 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `personalCodes` | integer[]（兼容单值） | **是** | 基金经理**内码**列表（如 `[101019305]`），支持多位；缺失 / 空 / 非正整数 → 400 `PARAM_INVALID` |

> `personalCodes` 要的是**经理内码**，不是姓名、也不是基金代码。
> 只有姓名时先用 `fund-manager-resolve` 解析出 `candidates[].personalCode` 再调用本接口。

## 4. 调用示例

```bash
# 单经理全部任职经历
pixi run etf-htbr invoke fund-manager-experience '{"personalCodes":[101019305]}'
# 多经理履历对比
pixi run etf-htbr invoke fund-manager-experience '{"personalCodes":[101019305,101014016]}'
```

## 5. 返回数据路径与关键字段

读 `$.data`：

| 字段 | 含义 |
|---|---|
| `recordCount` | 行数 |
| `records[]` | 一行 = 经理 × 一段任职经历 |
| `records[].personalobject` / `records[].personalname` | 经理内码 / 姓名 |
| `records[].begindate` / `records[].enddate` | 任职开始 / 结束日期（`YYYY-MM-DD`；`enddate` 为 `null` = 至今在职） |
| `records[].investadvisorcode` / `records[].investadvisorname` | 任职公司代码 / 任职公司名称 |
| `records[].employmentcompany` | **任职时长**（文本，如 `3.0年`） |
| `records[].nature` | 任职公司性质（中文描述，如 `公募`） |
| `records[].duties` | 职务（中文描述，如 `基金经理`） |

## 6. 数据口径

- **`employmentcompany` 是任职时长，不是公司名**：列名沿用上游报表、语义与字面不符；任职公司看 `investadvisorname`。回答时不要把时长当公司、也不要把公司名当时长。
- **`nature` / `duties` 是中文描述**：上游直接给 `公募` / `基金经理` 等文本，不是编码；原样引用即可。
- **一行 = 经理 × 一段任职经历**：同一经理在不同公司、不同职务阶段各一行；不要合并或去重。
- **`enddate` 为 `null` 表示至今在职**，不是数据缺失。
- 行序由上游决定，未额外排序；需要「最新一段」时按 `begindate` 自行取最大。

## 7. 空数据与异常值语义

| 现象 | 含义与处理 |
|---|---|
| 400 `PARAM_INVALID` | `personalCodes` 缺失/空/非内码 —— 补齐或纠正参数 |
| 200 + `NO_DATA` 注记 | 经理内码无法解析，或该经理无任职经历记录 —— 如实说明无数据 |
| `enddate` 为 `null` | 至今在职，不是异常 |
| 接口报错（非 200） | 上游取数失败原样抛出，不代表「无数据」，如实告知稍后重试 |

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- `personalCodes` 必须是**经理内码**；只有姓名先走 `fund-manager-resolve`。
- 结果条数与经理从业年限正相关，多经理批量时按需分批。

## 9. 相关工作流

- 只有经理姓名、没有内码 → 先读 `workflows/manager-name-resolution.md`，用 `fund-manager-resolve` 取 `personalCode`。
- 想看某只基金的历任经理与任期回报 → `fund-manager-history`；档案 → `fund-manager-info`；规模 → `fund-manager-scale`；标签 → `fund-manager-tag`；观点 → `fund-manager-viewpoint`。
