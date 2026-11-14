# fund-manager-resolve

| 项 | 值 |
|---|---|
| `api_id` | `fund-manager-resolve` |
| 服务端登记名 | 基金经理姓名解析 |
| 领域 | fund |
| 资料完整度 | 完整（请求 + 响应 + 口径均有） |
| 性质 | **前置编排接口**：仅用于把「姓名」解析成「人」，不单独成答 |

## 1. 功能与适用场景

用户**只给了基金经理姓名**、没给代码时，先把姓名解析为唯一的 `personalCode`，再据此调用下游接口。

适用：用户问「张坤管理的基金有哪些」「某位经理的履历」，且**没有**可用的人员编号。

## 2. 不适用场景与易混接口

- **不要**用本接口的返回值直接组织回答 —— 它只产出 `personalCode`，正题由 `fund-manager-info` / `fund-manager-tag` 回答。
- 用户问的是**某只基金的历任经理**（已给定基金代码）时，直接用 `fund-manager-history`，不需要解析姓名。
- 本接口做**精确姓名匹配**，不做模糊检索、不支持拼音。

## 3. 请求参数

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `managerName` | string | 是 | 经理**中文姓名**，精确匹配 |

## 4. 调用示例

```bash
pixi run etf-htbr invoke fund-manager-resolve '{"managerName":"张坤"}'
```

## 5. 返回数据路径与关键字段

读 `$.data`，关键字段：

| 字段 | 含义 |
|---|---|
| `matchCount` | 命中人数，**决定走哪一态**（见下） |
| `candidates[]` | 候选列表 |
| `candidates[].personalCode` | 人员编号（下游接口的入参） |
| `candidates[].chineseName` | 姓名 |
| `candidates[].gender` / `.education` | 性别 / 学历 |
| `candidates[].experienceTime` | 从业年限 |
| `candidates[].companyAbbrName` | 现任公司简称（**消歧首选字段**） |

## 6. 数据口径

- **三种结果全部是 HTTP 200，都不报错**，必须靠 `matchCount` 分支：
  - `matchCount = 1` —— 唯一命中。
  - `matchCount > 1` —— 重名，需消歧。
  - `matchCount = 0` —— 零命中。
- 各分支的**处理动作**（何时直接续调、何时停下等用户选择、话术要求）见 `references/workflows/manager-name-resolution.md`。
- 同一轮对话内对同一姓名的解析结果**可复用**，不必重复调用。

## 7. 空数据与异常值语义

- `matchCount = 0` 时 `candidates` 为空数组 —— 表示该姓名无命中，需引导用户核对姓名，**不得**用相近姓名猜测替代。
- 单个候选人字段缺失（如 `companyAbbrName` 为空）时按缺失展示，不要补造。

## 8. 前置条件与调用限制

- 需已配置 API Key（`config.py status` 为 configured），网关可达；调用间隔建议 ≥ 3 秒。

## 9. 相关工作流

- `references/workflows/manager-name-resolution.md` —— **必读**，含三态处理与展示规则。
