# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

主要来源：提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 `.agents/skills/dsh-code-review/SKILL.md` 第 8–49 行。

补充来源：

- `packages/AGENTS.md` 第 9–18 行；
- 根目录 `AGENTS.md` 第 116、122 行；
- `docs/defensive-patterns.md` 第 7–33 行；
- `docs/testing.md` 第 21–49 行；
- `docs/cookbook/responding-to-pr-review-on-a-stack.md` 第 9–24 行；
- `docs/cookbook/maintaining-dsh-code-review.md` 第 9–17、19–48 行。

## 保留的原文写法

开头的适用边界、review 优先级、接口／生命周期／消费方／执行点／派生状态／边界／真实入口／测试强度／transcript 检查和 findings 格式均基本保留上游写法。

## 通用化改动

- 删除 DeepSeek 命令、包形式、不变量 companion、Agent Note 生命周期、双语政策和 GitHub 专用回复机制。
- 增加明确的工作区范围，因为通用 Skill 不只覆盖 PR。
- 将上游堆叠 review 中“在引入问题的层修复”规则并入接收 review 部分，不引入堆叠状态修改。
- 保留维护实操手册中的人工判断：生成或委派的 review 输出不是权威，单次事故也不会自动成为通用规则。
- 根据上游长期指令，明确加入对过时测试、死代码覆盖率和类型边界测试的 review。
- 新增简体中文翻译，不改变严重程度或举证要求。

原文快照：`../../../upstream/repository/.agents/skills/dsh-code-review/SKILL.md.orig`。
