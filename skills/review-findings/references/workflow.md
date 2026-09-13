# 范围、Git 和交互流程

## 解析输入

支持 `uncommitted`、`branch <branch>`、`commit <sha> [title]`、`pr <ref>` 和 `folder <paths...>`。自然语言请求映射到同样的范围；无法确定范围或缺少必需参数时提供选择。`--extra <value>` 和 `--extra=<value>` 可用于任何模式；重复时保留最后一个值，`--extra` 缺少后续 token 时报告错误。

引号包围的路径作为一个完整路径；自然语言明确指定的路径也保持原样。只有未分组的路径列表才按空白分割。把命令参数作为独立参数传给 Git/gh，避免 shell 插值。

已有活动审查时，要求先结束，不开启第二个；用户明确要求替换当前审查时，结束旧审查再开始新范围。先执行 `git rev-parse --git-dir` 确认仓库，再解析目标。

## 交互选择

固定顺序提供以下选项，允许取消和返回：

1. Review uncommitted changes
2. Review against a base branch
3. Review a commit
4. Review a pull request
5. Review a folder (or more)
6. Add custom review instructions / Remove custom review instructions

共享指令存在时第六项为删除，否则为添加。添加使用多行输入；空输入或取消保持原值，成功后保存去除首尾空白的值，回到选择器。共享指令适用于当前对话的全部审查模式，保留最近值；它不是跨会话的全局配置。

建议的默认范围由以下规则决定；呈现选项时保留顺序，不自动提交选择：

- `git status --porcelain` 有输出：未提交变更。
- 否则当前分支不同于默认分支：对比分支。
- 否则：指定提交。

当前分支用 `git branch --show-current`。默认分支先取 `git symbolic-ref refs/remotes/origin/HEAD --short` 并去掉 `origin/`；失败后检查本地 `main`、`master`，最后回退 `main`。

分支选择器列出 `git branch --format=%(refname:short)` 的本地分支，排除当前分支，默认分支优先，其余按名称排序。提交选择器列出 `git log --oneline -n 20`，保留 SHA 和标题。两者支持按名称/标题模糊筛选；无候选时报告并返回。目录输入默认 `.`，按上述路径规则解析；空输入返回。PR 输入接受编号或 URL。

通过选择工具或对话提供选项。用户直接指定范围时跳过选择器。

## 目标解析

模板来自 `targets.json`：

| 目标 | 模板与替换 |
| --- | --- |
| 未提交 | `UNCOMMITTED_PROMPT` |
| 分支，共同祖先可用 | `BASE_BRANCH_PROMPT_WITH_MERGE_BASE`：`{baseBranch}`、`{mergeBaseSha}` |
| 分支，共同祖先不可用 | `BASE_BRANCH_PROMPT_FALLBACK`：`{branch}` |
| 提交有标题 | `COMMIT_PROMPT_WITH_TITLE`：`{sha}`、`{title}` |
| 提交无标题 | `COMMIT_PROMPT`：`{sha}` |
| PR，共同祖先可用 | `PULL_REQUEST_PROMPT`：`{prNumber}`、`{title}`、`{baseBranch}`、`{mergeBaseSha}` |
| PR，共同祖先不可用 | `PULL_REQUEST_PROMPT_FALLBACK`：`{prNumber}`、`{title}`、`{baseBranch}` |
| 目录 | `FOLDER_REVIEW_PROMPT`：`{paths}`，以 `, ` 连接路径 |

共同祖先：先执行 `git rev-parse --abbrev-ref <branch>@{upstream}`，成功则执行 `git merge-base HEAD <upstream>`；失败则执行 `git merge-base HEAD <branch>`。均失败时用 fallback 模板，让审查任务继续查找比较基点。不额外 fetch，也不把比较替换为双端提交 diff；提示使用 `git diff <merge-base>`，包含当前工作树的相关变化。

未提交模式分别检查 `git diff`、`git diff --cached`，并用 `git ls-files --others --exclude-standard` 列出未跟踪文件后读取内容。普通 diff 不包含未跟踪文件。目标不存在或基点无法确定时报告范围无法完成，不把读取失败当作“没有问题”。

## PR 准备

1. 检查 `gh --version`、`gh auth status`。不可用或未登录时提示安装/登录办法，停止本次 checkout。
2. 用 `git status --porcelain` 检查已跟踪文件的暂存或未暂存变化；忽略 `??` 行。发现变化则阻止 checkout，提示用户先 commit 或 stash；不自动执行这些操作。
3. 接受完整正整数编号或 GitHub PR URL。编号属于当前仓库；URL 必须保留 owner/repo，并用 `gh repo view --json nameWithOwner` 核对当前仓库。仓库不一致时停止 checkout，说明目标与当前仓库，请用户指定正确本地仓库；不得只取编号审查另一个 PR。
4. 执行 `gh pr view <number> --json baseRefName,title,headRefName`。读取失败或 JSON 无效时报告失败。
5. 紧邻 checkout 前再次检查已跟踪文件变化，然后执行 `gh pr checkout <number>`。checkout 失败时报告命令错误，不清理文件。未跟踪文件冲突由 gh/Git 报错。
6. 成功后使用 PR 的目标分支、标题和编号构建目标。PR 准备失败后返回审查选项。

这是实际的本地 Git 分支切换。不自动恢复原 Git 分支，结束审查只改变当前对话中的审查阶段。
