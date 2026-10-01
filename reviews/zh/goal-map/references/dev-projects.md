# 开发项目

让 DEV 项目与 GitHub 上跟踪的需求保持同步。GitHub ticket 仍是工作单元；DEV 项目是一个独立需求在目标层面的把手。

## 需求文档或 wayfinder 地图发布时

在仓库的 issue tracker 工作流（`to-spec`、`wayfinder`）创建 GitHub issue 之后执行。

1. 查找项目：`linear project list --team DEV --json`，匹配 description 中的 `github:` 行或明显相同的名称。
2. 新 issue 只是补充某个已有项目的范围时，用 `linear project update <id> --description` 把它的 `github:` 行追加到该项目的 description。追加后会超过 255 字符，或改变了完成标准时，改为告诉用户要在概览里改什么。
3. 它是一个独立需求时，提议一个项目：名称、摘要、完成标准、目标日期、目标、仓库标签。确认后：

   ```bash
   linear project create --team DEV --name "<requirement name>" \
     --description "github: <owner>/<repo>#<number>" \
     --content-file <overview.md> --status planned \
     --target-date <YYYY-MM-DD> --label "repo:<repo-name>" \
     --initiative "<goal>"
   ```

   概览遵循 `SKILL.md` 中的格式。没有商定目标时省略 `--initiative`；之后用 `linear initiative add-project <initiative> <project>` 关联。
4. 需求文档定义了阶段时，添加里程碑：`linear milestone create --project <id> --name <phase> --target-date <date>`。

完成标准：项目包含每一行 `github:`，且你已报告其标识符。

## 依据 GitHub 同步

周回顾用它收集到的 GitHub 事实执行：

- 有任何 ticket 关闭或 PR 合并后，把 `planned` 的项目设为 `started`。
- 某个里程碑的 ticket 全部以完成状态关闭时，发布 `linear project-update create <id> --health onTrack --body-file <file>`，列出已合并的 PR。

## 需求看起来已交付时

当项目各 `github:` issue 下的子 issue 全部关闭，或用户说已交付时，收集证据：每条的关闭原因（`completed` 或 `not_planned`）、已合并的 PR，以及概览中的完成标准。提议一种结果：

- **完成**：已合并的工作满足完成标准。
- **取消**：工作以“不做”关闭，或已被替代。
- **询问**：证据相互矛盾。

确认后，发布最后一次项目更新，列出交付内容以及在 GitHub 上仍未关闭的后续 issue，然后设置状态。

完成一个项目不会改动它所属的 initiative；目标在每周回顾中按其衡量指标判断。
