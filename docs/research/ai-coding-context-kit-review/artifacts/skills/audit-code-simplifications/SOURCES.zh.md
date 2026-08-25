# 来源和通用化改动

[English](SOURCES.md) | 中文

## 精确上游来源

主要来源：提交 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` 中 `.agents/skills/dsh-find-simplifications/SKILL.md`。

保留范围：

- 第 8–31 行：用途和强候选项分类体系；
- 第 33–63 行：广泛调查、信任／生命周期分析和依赖替换；
- 第 64–80 行：消费方证据和否决门槛；
- 第 99–121 行：长期提案与行内注记的区分，改写到报告部分；
- 第 133–146 行：验证和报告原则。

补充来源：根目录 `AGENTS.md` 第 116、122 行；`packages/AGENTS.md` 第 9–12 行；`docs/testing.md` 第 10 行；以及 `docs/defensive-patterns.md` 第 7–33 行。

## 通用化改动

- 删除 DeepSeek 包名、受保护的双实现、Agent Note 路径、分支折叠、PR 修改和固定命令。
- 大体逐字保留上游候选项分类和证明方法。
- 将 DeepSeek Agent Note 输出改为仓库无关的证据报告；目标项目可再把长期候选项放入自己的决策记录格式。
- 将上游关于过时行为、死代码覆盖率和类型边界测试的规则明确写入候选 Skill，并要求消费方证据。
- 在依赖健康检查中加入许可证、安全和平台支持，因为这些是移植到其他仓库时必须考虑的边界事实。
- 新增简体中文翻译，不改变判断门槛。

原文快照：`../../../upstream/repository/.agents/skills/dsh-find-simplifications/SKILL.md.orig`。
