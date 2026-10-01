# 例行流程

秘书与用户保持的定期接触。无论是用户主动要求还是定时任务触发，每个流程的做法都一样；每个流程都可能在一次全新的对话里运行：读取之前的流程留在 Linear 里的内容，不要假设自己记得。写入权限和草稿格式遵循 `SKILL.md`。用中文给用户写，简短。

## 晨间简报

帮用户决定今天做什么，并提前提醒接下来的事。

1. 收集：
   - 两天内到期或已逾期的未完成 LIFE issue（`SKILL.md` 中的截止日期查询，日期用今天加两天）。
   - 当前 LIFE cycle 的未完成 issue（`linear issue query --team LIFE --cycle active --state unstarted --state started --json`）。
   - 跟进日期已到的 `等待` issue，以及本周进度落后的习惯。
   - started LIFE 项目在七天内到期的里程碑和目标日期（`linear milestone list --project <id>`），以及其中未完成的 issue 和名称所指的工作量。
   - 最近一份周回顾文档（`linear document list --team LIFE --cycle previous --json`，再 `linear document view <id>`）：有草稿但没有 `## 处理结果` 时，说明它还在等用户回复。
2. 建议今天最多三件重点，每件附一行理由。提到已逾期的事项、两天内到期且今天需要准备的事项，以及按目前节奏会赶不上的里程碑，并说明差距（`语法基础 10-09 截止，还剩 5 课`）。对仍在等待的回顾草稿提醒一次。

以上都没有内容时，回复今天没有事项，然后结束。

## 晚间打卡

收拢当天的事。

1. 列出今天到期的未完成 LIFE issue、进行中的 issue，以及本周进度落后的习惯。
2. 问做完了什么。收到回复后，把报告完成的 issue 标为完成并添加习惯打卡。对滑落的事项，按 `SKILL.md` 中的原则询问。

清单为空时，回复没有需要打卡的事项，然后结束。

## 周回顾（周末）

在当前 LIFE cycle 结束前回顾它；其中未完成的 issue 将顺延。先收集证据，再做判断：

1. **Linear**：当前 cycle 已完成和未完成的 issue；从打卡评论统计习惯次数；每个活跃 initiative 及其项目和最近的更新；本周完成或取消的项目。
2. **GitHub**：对 started 状态的 DEV 项目以及本周有变化的 DEV 项目中的每一行 `github:`，查本周关闭的子 issue（`gh api repos/<owner>/<repo>/issues/<number>/sub_issues --paginate`）及其 `state_reason`，以及合并的 PR（`gh pr list -R <owner>/<repo> --state merged --search "merged:>=<date>" --limit 100`）。列表达到上限时，说明数据可能不完整。按 `dev-projects.md` 依据这些事实同步 DEV 项目。
3. **额度**：按 `SKILL.md` 中所述计数。

然后写回顾：

- 进展：每个目标推进了什么，附证据。
- 按目标：衡量指标的当前值与目标值（询问过去一周缺失的值），`onTrack|atRisk|offTrack` 加一句理由，以及下一个项目或步骤。
- 滞后与停滞：将顺延的 issue、超过目标日期的项目、`等待` 条目。对滑落两次的事项询问原因。
- 额度一行。

编号草稿：每个活跃 initiative 和 started 项目的进度更新、要取消的未完成习惯 issue，以及看起来已交付的 DEV 项目（按 `dev-projects.md`）。

把回顾和草稿保存为文档 `周回顾 <YYYY>-W<ww>`，按编号附到当前 LIFE cycle；`document list --team LIFE --cycle <number> --json` 中已有同标题文档时，改为更新它。把两者一起发给用户。

完成标准：每个活跃 initiative 都有一份起草的更新，且已报告文档的标识符。

## 周规划（周初）

和用户商定新 cycle。

1. 读最近一份周回顾文档（方法同晨间简报），包括其中的 `## 处理结果`。没有活跃的 initiative 时，先邀请用户一起设定目标（愿景 → 领域 → 一到三个目标），按 `SKILL.md` 进行，再规划 issue。
2. 本周可用时间不明确时（出差、其他截止日期），问一次。
3. 提议 cycle 的 issue，按目标截止日期、依赖和工作量排序：总数不超过 10 条，顺延的 issue 和要新建的习惯 issue 都计入。说明推迟了什么以及原因。

确认后，把商定的 issue 移入该 cycle，并按 `SKILL.md` 为该 cycle 创建习惯 issue。

## 月度检查

- 每个 initiative：起草一份 initiative 更新，并检查它的衡量指标是否仍然合适。
- 项目：超过目标日期的 started 项目，以及应关闭的已完成阶段。
- 想法：每条放了一个月以上的想法，附上建议的去向（一个动作、一个项目或目标、继续放着、放弃），按 `SKILL.md` 处理。
- 额度：按 `SKILL.md` 计数，以及最老的未完成 backlog issue 作为关闭候选。
- 愿景：自上次月度检查以来有目标完成或放弃时，询问 `愿景与领域` 是否仍然成立。

与周回顾一起执行时，把它的发现和草稿条目并入那份周回顾的文档和草稿。
