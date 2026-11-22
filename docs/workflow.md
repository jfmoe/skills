# 开发工作流

本文说明本仓库里几个 skill 如何组成一条从想法到合入的开发流程：它遵循什么理念、各部分怎么分工、怎么安装、规则要改时改哪里。各 skill 的具体规则以它们自己的 `SKILL.md` 为准，本文只讲它们之间的关系。

## 理念

1. **先让它跑起来，再把它做对。** 实现和重构是两个阶段，也是两类提交。重构提交不改测试的预期值，所以可以单独回退和追溯。
2. **规格只定大方向。** 规格和拆票阶段确定模块、接口、数据形状和测试接缝。更细的结构由实施者决定，拿不准或对规格有异议时回问架构师。
3. **从第一性原理设计。** 讨论规格时先问“需求从一开始就存在时会怎么设计”，不在旧设计上打补丁；先减后加。
4. **实施者和评审者看同一份原则。** 实施者开工前读原则卡，评审时把同一份原则卡交给评审者。
5. **测试只为规则而写。** 说不出哪个 bug 会让测试变红，就不写这条测试。不设覆盖率目标，度量结果只当线索。
6. **规则从摩擦中来。** 项目规范不预先起草。实施中出现问题时，能机械判定的做成检查，需要判断的写进项目规范。

## 角色

| 角色 | 是谁 | 负责 |
| --- | --- | --- |
| 架构师 | 调用 `herdr-architect` 的会话 | 设计、裁定、评审、合入、关票、回顾 |
| 工人 | Herdr 其他 pane 里的 Agent，种类不限 | 实现、修正、跑检查、查证 |
| 顾问 | 用户用 `advisor=` 指定的 Agent，通常是与架构师不同的模型；可选 | 设计阶段基于同一份前提独立出一份方案，由架构师取舍 |
| 评审者 | `code-review` 启动的两个 subagent | 分别按规范和规格评审 diff |

## 流程

```text
准备（架构师）
  提问                 只问决定方案走向、需要用户拍板的问题（grilling、domain-modeling）
  [顾问]               用户指定时：架构师写下设计前提，与顾问各自出方案，再综合（可选）
  设计                 呈现思路、行为变化、关键结构改动和放弃的备选；按第一性原理设计，讨论到用户认可；有顾问时列出两份方案的分歧
  to-spec、to-tickets  用户手动调用；规格和票先写成本地草稿
  评审                 一个 subagent 对照认可的设计评审两份草稿
  发布                 用户确认拆票方案后发布规格和票
  项目事实             检查命令、合入策略、授权、可选度量是否开启

每张票（工人，上下文已清空）
  读实施说明和原则卡
  [refactor]           预备重构（可选）
  tdd                  红 → 绿；test-layers 决定测试放在哪一层
  [feat / fix]         测试和实现，一个提交
  code-review          规范来源：项目规范 + 原则卡 + test-layers
  [fix / test]         改变行为或测试预期值的评审修正（可选）
  [refactor]           纯结构的评审修正（可选）
  整理提交             超过 3 个时合并同类提交，只改写本票尚未推送的提交
  → 架构师评审 diff、合入、关票

规格收尾（架构师）
  code-review          评审整个规格
  可选度量             项目声明后才跑，只看本规格改过的文件
  修正、清理 worktree
  回顾                 返工的票、重复出现的回问和评审问题 → 落实为检查或规范
  在规格上写结论
```

工人随时可以回问：规格没覆盖的取舍、规格与代码事实冲突、对规格的设计有异议、需要改动其他票的范围。回问写成文件，由架构师裁定；裁定改动规格时，规格和受影响的票一并修改。

## 各 skill 的职责

| skill | 来源 | 在流程中的职责 |
| --- | --- | --- |
| `herdr-architect` | 本仓库，Original | 整条流程的调度规则，以及发给工人的实施说明模板 |
| `ub-mode` | 本仓库，Fork（上游 `unclebob/ub-mode`） | 原则卡：写给实施者的工程原则，也是评审的规范来源 |
| `test-layers` | 本仓库，Original | 测试放在哪一层、怎样的测试值得写；也是评审的规范来源 |
| `commit-message` | 本仓库，Original | 提交如何拆分、提交信息怎么写 |
| `audit-code-simplifications` | 本仓库，Fork | 审查存量代码的简化机会。不在每张票的路径上，在规格之间按需使用，候选项经提问和设计进入新规格 |
| `grilling`、`domain-modeling`、`to-spec`、`to-tickets`、`implement`、`tdd`、`code-review`、`retro` | 第三方，`mattpocock/skills` | 流程各阶段的具体做法 |
| `herdr` | 第三方，`herdrdev/herdr` | 操作 Herdr 的命令用法 |

第三方 skill 不在本仓库修改。本流程对它们的调整都写在 `herdr-architect` 和实施说明里，例如“先提交再运行 `code-review`”和“评审时额外加入哪些规范来源”。

### 同一类问题由谁管

| 问题 | 由谁管 | 说明 |
| --- | --- | --- |
| 测试怎么写 | `tdd` 管红绿循环和接缝，`test-layers` 管分层和取舍 | 接缝是测哪个接口，层是启动多少真实设施，两者独立 |
| 代码异味 | `code-review` 自带的异味基线 | 只看本次 diff；项目规范与它冲突时项目规范优先 |
| 重复代码 | 原则卡：先证明是同一份知识再合并 | 度量工具给出的重复只是候选 |
| 未覆盖的代码 | 原则卡：没有消费方就删，说得出 bug 才补测试 | 与 `audit-code-simplifications` 的判断标准一致 |
| 提交拆分 | `commit-message` 是完整规则 | 原则卡保留两行，供开工前阅读和评审时检查；实施说明规定评审修正怎么拆 |

规则冲突时的优先顺序：项目规范 > 实施说明 > 原则卡和 `test-layers`。

## 项目定制

每个项目通过自己仓库里的文件调整这套流程，不需要改 skill。

| 文件 | 作用 | 何时出现 |
| --- | --- | --- |
| `docs/agents/issue-tracker.md` | tracker 的读票、评论、关票操作 | 必需；由 `setup-matt-pocock-skills` 生成 |
| 检查命令（lint、测试、CI） | 能机械判定的规则 | 项目自带；架构师纠偏和回顾时补充 |
| `CODING_STANDARDS.md` 或项目已有的规范文件 | 需要判断的评审规则；`code-review` 必读 | 出现第一条有证据的规则时由架构师写入，没有文件时新建 |
| `docs/agents/quality-gates.md` | 声明要跑的度量工具（CRAP 分数、重复度、变异测试）、范围和阈值 | 可选；文件不存在即关闭度量。格式尚未约定 |

## 安装

本仓库是源，运行目录由它同步。安装和更新的完整规则见 `skills/manage-skills/SKILL.md`。

1. 安装本仓库的 skill 到全局（Codex 等共用 `~/.agents/skills`，Claude Code 的目录链接到它）：

   ```bash
   for s in herdr-architect ub-mode test-layers commit-message audit-code-simplifications; do
     npx skills add ~/Coder/skills -g -a codex claude-code --skill "$s" -y
   done
   ```

   架构师在准备阶段自己查找 `ub-mode` 和 `test-layers` 的安装位置，把绝对路径填进实施说明，所以它们装在哪个 skill 目录都可以。

2. 安装第三方 skill：
   - `mattpocock/skills`：Claude Code 中以插件 `mattpocock-skills@mattpocock` 安装。其他种类的工人需要另行安装其中的 `implement`、`tdd`、`code-review`；缺少时架构师会在准备阶段停下来提示。
   - `herdr`：来源 `herdrdev/herdr`。

3. 每个项目运行一次 `setup-matt-pocock-skills`，生成 `docs/agents/issue-tracker.md` 等文件。

4. 在 Herdr 中启动会话（`HERDR_ENV=1`），调用 `/herdr-architect <规格引用或想法>`。

## 维护

### 改规则时改哪里

| 想改的东西 | 改哪里 |
| --- | --- |
| 调度顺序、架构师的做法、规格收尾步骤 | `skills/herdr-architect/SKILL.md` |
| 工人每张票都要知道的事 | `skills/herdr-architect/implement-brief.md` |
| 实施原则 | `skills/ub-mode/SKILL.md`，并在 `registry/upstream/ub-mode/meta.yaml` 的 `notes` 里记下与上游的差异 |
| 测试分层和测试质量 | `skills/test-layers/SKILL.md`；审查整个套件的流程和异味表在 `references/review.md` |
| 提交拆分和提交信息 | `skills/commit-message/SKILL.md`；原则卡 Practice 一节的两行要保持一致 |
| 只对某个项目生效的规则 | 那个项目的规范文件或检查脚本 |

所有修改都在本仓库进行，不直接改运行目录。改完后：

1. 英文 skill 同步更新 `reviews/zh/<skill>/` 下的中文镜像。
2. 运行 `npx skills add ~/Coder/skills --list`，确认 skill 集合符合预期，上游快照没有被识别为 skill。
3. 重新安装改过的 skill，同步到运行目录。

### 跟进上游

- **`ub-mode`**：与上游的差异集中在三处：开头的读者说明、Optional Metrics 一节、Practice 一节，其余逐字相同。上游更新时按 `manage-skills` 的三方比较流程处理，对照 `registry/upstream/ub-mode/SKILL.md.orig`。
- **`mattpocock/skills`**：随插件更新。更新后检查 `herdr-architect` 依赖的几处是否还成立：`code-review` 的规范来源由调用者列出；`tdd` 把重构留给评审阶段；`to-spec` 的规格模板包含 Testing Decisions。

### 回顾产出的去向

架构师在规格收尾时做回顾。项目内的改进直接落实并单独提交；流程模板的改进改 `herdr-architect`；涉及原则卡等其他 skill 的改进只作为建议交给用户，由用户在本仓库修改。

## 已知限制

- 工人需要读取工作目录之外的原则卡和 `test-layers` 文件。Claude Code 可以；其他种类的 Agent 是否受沙箱限制尚未实测。
- 原则卡的描述会让它在任何实施或改代码的场景下被加载，不限于本流程。
- “结构与行为分开提交”这条规则同时写在 `commit-message`、原则卡和实施说明里，修改时要一并更新。
