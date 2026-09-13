---
name: review-findings
disable-model-invocation: true
description: 手动审查代码问题并按优先级排序，支持总结与修复交接。
---

# Review Findings

执行前完整读取对应提示词，按其要求审查当前代码库。审查阶段输出 findings，不自动实施修复。

## 入口

根据用户的参数或自然语言识别操作：

| 输入示例 | 操作 |
| --- | --- |
| `review-findings` | 选择审查范围 |
| `review-findings uncommitted` / 审查未提交变更 | 审查当前变更 |
| `review-findings branch main` / 对比 main 审查 | 审查相对分支的变化 |
| `review-findings commit abc123` / 审查提交 abc123 | 审查指定提交 |
| `review-findings pr 123` / 审查 PR 链接 | 审查指定 PR |
| `review-findings folder src docs` / 审查 src 和 docs | 审查目录快照 |
| `review-findings end-review` / 结束审查 | 选择结束动作 |
| 仅结束 / 总结并结束 / 总结并修复 | 执行对应结束动作 |

先识别操作，再加载所需流程：开始审查时读取 [workflow.md](references/workflow.md)，解析范围并准备 Git 信息；结束、总结或修复时直接进入下方“结束审查”，沿用已有结果。当前审查的追问和补充要求继续作用于同一次审查。

所有审查模式要求当前目录位于 Git 仓库。范围已明确时直接执行；缺少范围时提供选择。额外关注点可用自然语言或 `--extra "focus on performance and error handling"` 提供，只用于本次审查；用户明确要求后续审查共享时才保存为共享指令。

在当前对话中保留仓库路径、审查范围、比较基点或提交 SHA、共享指令和最新审查结果，供后续总结或修复使用。一次只保留一个活动审查；不向被审仓库写会话状态文件。

## 执行审查

1. 读取完整 [review-rubric.txt](references/review-rubric.txt) 和 [targets.json](references/targets.json)。按 workflow 选择目标模板并替换占位符。
2. 从当前工作目录向上查找最近的 `REVIEW_GUIDELINES.md`，以 `git rev-parse --show-toplevel` 返回的仓库根目录为上界。读取第一个匹配文件，去除首尾空白；不存在、不可读或为空时不追加。
3. 按以下格式构造完整任务。`rubric` 是原文，`prompt` 是替换后的目标模板；占位符不属于最终正文。

```text
{rubric}

---

Please perform a code review with the following focus:

{prompt}
```

4. 按顺序追加以下非空段落，每段前隔两个换行，标题与内容之间隔两个换行。共享指令、额外指令和项目准则均去除首尾空白。

| 内容 | 标题 |
| --- | --- |
| 会话共享指令 | `Shared custom review instructions (applies to all reviews):` |
| 本次 `--extra` | `Additional user-provided review instruction:` |
| 项目准则 | `This project has additional instructions for code reviews:` |

5. 当前 agent 按完整任务执行。读取实际代码和相关消费方，按模板检查 diff 或快照，输出符合准则的全部问题、结论和人工提示。输出后保留审查结果，等待用户结束、继续讨论或请求修复。

目录模式审查所选文件的当前状态并定位到实际文件；其他模式限定本次 diff 引入的问题。更具体的用户和项目指令覆盖通用审查要求。

## 结束审查

用户请求结束审查但未指定动作时，提供以下三种选择并等待回答。用户明确请求总结时执行“总结并结束”，明确请求修复时执行“总结并修复”，不重复询问。

- **仅结束**：清除活动标记，结束审查，不生成摘要或修改代码。
- **总结并结束**：完整读取 [review-summary.txt](references/review-summary.txt)，按该原文输出交接摘要，覆盖全部可执行发现。清除活动标记，保留摘要，不自动修复。
- **总结并修复**：先按同一摘要原文生成完整交接，核对当前仓库、范围和代码是否仍对应这些发现，再完整读取 [review-fix.txt](references/review-fix.txt)，按原文在当前 agent 中实施修复。完成摘要后结束审查状态，修复结果保留在当前对话。

总结和修复均在当前对话执行。摘要中的分支交接指审查转入实施阶段；修复使用本次范围对应的最新审查摘要；多个范围存在歧义时先确认。讨论中撤回或已修复的问题不进入待修队列，保留其处理结论。

总结或修复缺少审查结果时，请求提供结果或先执行审查；仅结束无需审查结果。取消或摘要失败时保留已有结果和活动状态。用户直接要求修复已有审查发现时，执行“总结并修复”，不用再问一次。
