# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

主要来源：提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 `.agents/skills/dsh-pre-push-checks/SKILL.md`。

保留范围：

- 第 8–37 行：钩子／CI 分工、范围检查和相关证据；
- 第 39–60 行：聚焦测试和覆盖率选择；
- 第 62–64 行：完整演练边界；
- 第 83–92 行：失败处理。

补充来源：

- 根目录 `AGENTS.md` 第 87–93、116、122 行；
- `docs/testing.md` 第 7–49 行；
- `examples/AGENTS.md` 第 7–18 行；
- `packages/client/AGENTS.md` 第 113–130 行中的窄检查阶梯。

## 通用化改动

- 删除 DeepSeek 命令、精确覆盖率阈值、GitHub stack sync、强制 push、push 流程和远程检查查询。
- 明确声明提交、push 和远程修改不在本 Skill 的授权范围内。
- 保留上游“最小证据”“不重复通过检查”、覆盖范围、完整演练和环境举证规则。
- 保留回归与过时测试的区分、将未覆盖分支判断为死代码的可能性，以及类型边界对敌意输入测试的限制。
- 从上游 GUI 指令加入 UI 路径验证。
- 新增简体中文翻译，不降低验证强度。

原文快照：`../../../upstream/repository/.agents/skills/dsh-pre-push-checks/SKILL.md.orig`；wrapper 为镜像中同目录的 `agents/openai.yaml`。
