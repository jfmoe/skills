# Workflow：基金经理姓名解析 → 人

> 适用：用户**只给了基金经理姓名**（没给人员编号）的请求，如「张坤管理的基金有哪些」「某位经理的履历/风格」。
>
> 本流程只负责**跨接口编排**：先解析出人，再决定调什么、何时停下问用户。
> 各接口的参数与响应字段以 `references/apis/<api_id>.md` 为准，本文件不复制参数定义。

## 涉及接口

| 步骤 | api_id | 作用 | 文档 |
|---|---|---|---|
| ① 解析 | `fund-manager-resolve` | 姓名 → `personalCode` | `references/apis/fund-manager-resolve.md` |
| ② 取档案 | `fund-manager-info` | 学历、年限、在管规模、代表作 | `references/apis/fund-manager-info.md` |
| ③ 取标签 | `fund-manager-tag` | 能力/获奖/风格标签 | `references/apis/fund-manager-tag.md` |

## 编排流程

```
用户只给姓名
   └─ ① fund-manager-resolve(managerName)
        ├─ matchCount = 1  → 直接取 candidates[0].personalCode，续调 ② / ③
        ├─ matchCount > 1  → 展示候选编号列表，停下等用户选择（不得自动挑人）
        └─ matchCount = 0  → 引导核对姓名，结束本轮（不得用相近姓名猜测）
                             ↓（用户选择后，用选中的 personalCode）
                        续调 ② / ③
```

## 三态处理规则

### `matchCount = 1`（唯一命中）

- 直接取 `candidates[0].personalCode` 续调下游，**不再询问用户**。
- 用户问的是简历 → 调 ②；问的是风格/标签/获奖 → 调 ③；问「他管哪些基金」→ 看 ② 的在管基金数，
  或按产品维度改用 `fund-company-funds` / 具体基金的 `fund-manager-history`（视问题而定）。

### `matchCount > 1`（重名）

- 按以下顺序列成**编号选项**展示，供用户选择：

  1. 现任公司（`companyAbbrName`；该字段缺失时**明确标注「公司简称缺失」**）
  2. 从业年限（`experienceTime`）
  3. 性别（`gender`）
  4. 学历（`education`）

- ⚠ **不展示 `personalCode` 内部代码**。
- 提示用户回复数字后**停下等待选择**，**不得**自动挑一个（如按年限最长/公司知名而擅自选定）。
- 用户选定后，用对应 `candidates[i].personalCode` 续调 ② / ③。

### `matchCount = 0`（零命中）

- 引导用户核对姓名，提示方向：是否有错别字、是否已离职、是否并非基金经理岗。
- **不得**用相近姓名、同音字或其它拼接方式猜测替代。

## 复用与限制

- 同一轮对话内，**同一姓名的解析结果可复用**，不需要为 ② 和 ③ 各解析一次，也不要重复调用。
- 本流程做**精确姓名匹配**，**不支持模糊检索与拼音检索**。姓名写不全或记不清时，如实说明该限制，
  不要用近似匹配替代。
- `fund-manager-tag` 的入参是数组（上限 50），批量查询时注意分批。

## 不适用本流程的情形

- 已给定**基金代码**、要看该基金历任经理 → 直接用 `fund-manager-history`（入参是基金代码，无需解析姓名）。
