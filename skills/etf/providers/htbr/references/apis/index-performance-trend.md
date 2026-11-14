# index-performance-trend

| 项 | 值 |
|---|---|
| `api_id` | `index-performance-trend` |
| 服务端登记名 | 指数业绩走势 |
| 领域 | index |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |
| 性质 | **业绩走势的补充接口**（默认不调） |

## 1. 功能与适用场景

取**指数**的同期走势，用于回答「这只基金跑赢沪深300了吗」「同期指数涨了多少」。

**仅在用户点名要与指数对比时调用**；用户没说跟谁比就不要替他挑指数。

## 2. 不适用场景与易混接口

- 不是主走势接口 —— 主接口是 `fund-nav-trend`。
- 要与**业绩比较基准**对比不在本接口范围（基准 ≠ 指数）；问区间基准收益用 `fund-stage-performance` 的 `benchGR`。
- ⚠ 本接口的 `indexCode` 与 `index-constituents` 的要求**不同**，见第 3 节。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `indexCode` | string | 是 | **SecuCode 净码，原样全串等值**：6 位数字净码（如 `000300`）、字母代码（如 `ISEQ`，须按库内大小写）、含点代码（如 `000001.ESCI`），**不带交易所后缀**。与 `index-constituents` 的 `indexObject[]`（收 `000300.SH` 或内码）口径不同 |
| `beginDate` | string | 是 | `yyyy-MM-dd` |
| `endDate` | string | 是 | `yyyy-MM-dd` |

> 三参必传。行情源由服务端按 DS 优先级（申万基金 → Wind → 中证 → 中债 → 海外 → 商品 → 申万宏源）**自动定源**，无需指定。

## 4. 调用示例

```bash
pixi run etf-htbr invoke index-performance-trend '{"indexCode":"000300","beginDate":"yyyy-MM-dd","endDate":"yyyy-MM-dd"}'
```

## 5. 返回数据路径与关键字段

读 `$.data.trends[]`，**交易日升序**：

| 字段 | 含义 |
|---|---|
| `indexCode` / `indexName` | 指数代码 / 简称 |
| `date` | 交易日 |
| `value` | 区间累计收益率（**小数**） |

## 6. 数据口径

- `value` 是**小数**，展示须 ×100 加 `%`；**首行恒为 0**（与主接口一致）。
- 区间语义与主接口同为「以区间起点为基准的累计收益率」。

## 7. 空数据与异常值语义

- HTTP 200 + 空数组 = 无命中或该区间无数据，**不报错**。看到空序列时**先核对 `indexCode` 是否为 SecuCode 净码原样值**（带交易所后缀不会命中；字母代码大小写与库不一致也不会命中），再下「无数据」结论。
- 带交易所后缀的多段代码（`000300.SH` 等）不会命中——本接口按 `SecuMain.SecuCode` **全串等值**匹配，不做后缀剥离也不做 GilCode 解析，见 `01a-Q事项挂账台账.md` Q-IDX-01；库内原生的含点 SecuCode（如 `000001.ESCI`）属于净码本身、原样传入即可命中。
- 三参缺失同样静默返回空序列。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。
- 追加调用前先确认用户确实需要指数对比。

## 9. 相关工作流

- `references/workflows/performance-trend-lines.md`
