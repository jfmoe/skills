# 例行流程

秘书与用户保持的定期接触。无论是用户主动要求还是定时任务触发，每个流程的做法都一样。写入权限和草稿格式遵循 `SKILL.md`。用中文给用户写，简短，合成一条消息。

## 晨间简报

帮用户决定今天做什么。

1. 收集：今天到期或已逾期的未完成 LIFE issue（`SKILL.md` 中的截止日期查询）；当前 LIFE cycle 的未完成 issue（`linear issue query --team LIFE --cycle active --state unstarted --state started --json`）；跟进日期已到的 `等待` issue；本周进度落后的习惯。
2. 建议今天最多三件重点，每件附一行理由，并提到已逾期的事项。

没有到期、逾期或落后的事项时，回复今天没有事项，然后结束。

## 晚间打卡

收拢当天的事。

1. 列出今天简报建议的事项，以及今天到期但仍未完成的 issue。
2. 问做完了什么。收到回复后，直接把报告完成的 issue 标为完成并添加习惯打卡。对每件滑落的事，简短问原因，并提供新日期、更小的一步或放弃。

今天没有计划或到期的事项、也没有落后的习惯时，回复没有需要打卡的事项，然后结束。

## 周回顾（周末）

在当前 LIFE cycle 结束前回顾它；其中未完成的 issue 将顺延。先收集证据，再做判断：

1. **Linear**：当前 cycle 已完成和未完成的 issue；从打卡评论统计习惯次数；每个活跃 initiative 及其项目和最近的更新；本周完成或取消的项目。
2. **GitHub**：对 started 状态的 DEV 项目以及本周有变化的 DEV 项目中的每一行 `github:`，查本周关闭的子 issue（`gh api repos/<owner>/<repo>/issues/<number>/sub_issues --paginate`）及其 `state_reason`，以及合并的 PR（`gh pr list -R <owner>/<repo> --state merged --search "merged:>=<date>" --limit 100`）。列表达到上限时，说明数据可能不完整。
3. **额度**：按 `SKILL.md` 中所述计数。

然后写回顾：

- 进展：每个目标推进了什么，附证据。
- 按目标：衡量指标的当前值与目标值，`onTrack|atRisk|offTrack` 加一句理由，以及下一个项目或步骤。
- 滞后与停滞：将顺延的 issue、超过目标日期的项目、`等待` 条目。对滑落两次的事项询问原因。
- 额度一行。

把它保存为文档 `周回顾 <YYYY>-W<ww>`，按编号附到当前 LIFE cycle；`document list --team LIFE --cycle <number> --json` 中已有同标题文档时，改为更新它。发送回顾时附一份编号草稿，包含：每个活跃 initiative 和 started 项目的进度更新、要取消的未完成习惯 issue，以及看起来已交付的 DEV 项目（按 `dev-projects.md`）。

完成标准：每个活跃 initiative 都有一份起草的更新，且已报告文档的标识符。

## 周规划（周初）

和用户商定新 cycle。

1. 读最近一次周回顾，以及用户从中批准了什么。
2. 本周可用时间不明确时（出差、其他截止日期），问一次。
3. 提议 cycle 的 issue，按目标截止日期、依赖和工作量排序：总数不超过 10 条，顺延的 issue 和要新建的习惯 issue 都计入。说明推迟了什么以及原因。

确认后，把商定的 issue 移入该 cycle，并按 `SKILL.md` 为该 cycle 创建习惯 issue。

## 月度检查（月初）

- 每个 initiative：起草一份 initiative 更新，并检查它的衡量指标是否仍然合适。
- 项目：超过目标日期的 started 项目，以及应关闭的已完成阶段。
- 额度：计数，以及最老的未完成 backlog issue 作为关闭候选。
- 愿景：本月有目标完成或放弃时，询问 `愿景与领域` 是否仍然成立。
