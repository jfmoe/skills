# 审阅包校验器说明

[English implementation](verify-review-bundle.mjs)

该脚本对集中审阅目录执行以下机械检查：

- `source-manifest.tsv` 恰好包含 70 个互不重复的来源和镜像路径；
- 每个镜像文件的 Git blob SHA 和行数与 manifest 一致；
- `prompt-surface-scan.tsv` 恰好包含 125 条互不重复的路径；
- 处置值属于已知集合；
- 审阅包内不存在实际符号链接，也不存在会生效的字面文件名 `SKILL.md`、`AGENTS.md` 或 `CLAUDE.md`；
- 7 个候选 Skill 全部存在，英文和中文入口的 `name` 与目录一致；
- 每个 Skill 都有双语 UI 元数据和双语来源记录；
- `ARTIFACT_INDEX.tsv` 中每个产物、中文对侧和来源记录都存在；
- Markdown 翻译对的标题层级和围栏代码保持一致；
- 除原文证据、来源记录和语言无关 TSV 外，每份派生产物都登记在产物索引中；
- 需要固定提交的来源记录确实写明提交 SHA。

默认运行 `node audit/scripts/verify-review-bundle.mjs` 时，校验器只使用审阅包内的 manifest 和镜像，因此不依赖临时克隆。

运行 `node audit/scripts/verify-review-bundle.mjs --upstream <deepseek-harness-clone>` 时，它还会直接读取固定提交的完整 Git tree：

- 重新核对 70 个来源路径、blob SHA 和镜像字节；
- 根据常见 Agent 指令文件名、`.claude/skills`、所有 `SKILL.md`、名称含 prompt/instruction 的文件及完整 preset 目录，重新推导 125 条扫描路径；
- 确认 11 个仓库 Skill 目录的全部文件、全部 preset 文件，以及所有长期指令／发现入口都进入 manifest。

哈希计算使用 Git blob 规则：对 `blob <字节数>\0<内容>` 计算 SHA-1。该检查能够证明镜像内容一致，不依赖临时克隆仍然存在。

脚本只检查结构、覆盖和哈希，不能证明翻译语义正确或提示词决策合理；这些仍由人工 review 负责。`--upstream` 模式只读 Git 对象，不修改上游克隆。
