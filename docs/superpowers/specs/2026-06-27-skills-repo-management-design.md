# Skills 仓库管理架构重构 — 设计文档

- 日期:2026-06-27
- 仓库:`~/Coder/skills`(remote `https://github.com/jfmoe/skills`)
- 状态:已确认设计,待实现

## 1. 背景与目标

当前仓库只服务「纯自定义 skill」,对另外两种真实场景支撑不足:

1. **情况 1 — 项目内直装第三方**:在其他项目里用 `npx skills` 装 GitHub 源的第三方 skill。当前没有任何地方记录「哪个项目装了哪些第三方 skill / 什么版本」,无法复现、无法批量更新。`registry/third-party.md` 只记 global 范围,且手工维护、会漂移。
2. **情况 2 — fork 改造第三方**:基于第三方 skill 改一个自定义版本。当前仓库没有约定区分「原创」和「魔改」,也没有地方记 upstream 来源 / 版本 / 改了什么;upstream 更新时无法对比同步。

**目标**:一次性系统重构,让仓库同时支撑这两种场景,且关键状态「不漂移」。

设计决策(已与用户确认):

- fork 保留一份未改动的 upstream 原始副本,供 upstream 更新时 diff。
- 项目级复现靠每个项目自己的 `skills-lock.json`(`npx skills` 原生能力);中心仓库另维护一份**跨项目总账**当总览。
- 总账与 fork 元数据靠**扫描脚本自动生成**,而非手工维护。

## 2. 核心概念:三类 skill

| 类别 | 含义 | 是否进本仓库 | 如何识别 |
| --- | --- | --- | --- |
| **Original** 原创 | 纯自定义 | ✅ `skills/<cat>/<skill>/` | `registry/upstream/` 下无同名目录 |
| **Fork** 魔改 | 基于第三方改造(情况 2) | ✅ `skills/<cat>/<skill>/` | `registry/upstream/<skill>/` 下有同名目录 |
| **Third-party** 直装 | 未改动,项目内 / 全局直装(情况 1) | ❌ 不进仓库 | 仅出现在总账中 |

`<cat>` 仍限 `workflows` / `coding` 两个分类,不新增分类。

## 3. 关键约束:`.upstream/` 不能内置于 skill 文件夹(已验证)

实测 `npx skills add` 安装一个 skill 时会**整体拷贝/软链该 skill 文件夹**,包括点开头的子目录;且 CLI **没有任何 ignore / exclude 选项**(已查 `add --help`)。

验证记录:

```text
源:  src/coding/demo-fork/SKILL.md
     src/coding/demo-fork/.upstream/SKILL.md
     src/coding/demo-fork/.upstream/meta.yaml

安装后(项目内):
     .claude/skills/demo-fork/SKILL.md
     .claude/skills/demo-fork/.upstream/SKILL.md     ← 原始副本被一起带进项目
     .claude/skills/demo-fork/.upstream/meta.yaml    ← 元数据也被带进项目
```

CLI 不会把 `.upstream/SKILL.md` 当成第二个 skill(仍是 "Found 1 skill"),但会把整份 upstream 副本塞进每个安装该 fork 的项目——既冗余,运行时 agent 还可能误读那份 pristine 的 SKILL.md。

**结论**:upstream 原始副本必须存放在**可安装 skill 文件夹之外**。所有「管理用」内容收归 `registry/`,`skills/` 回归「纯可安装」语义。

## 4. 目录结构(总览)

```text
AGENTS.md                 # 仓库规则(CLAUDE.md 为其 symlink)
README.md                 # Layout 说明
skills/
  workflows/<skill>/SKILL.md   # 原创或 fork,均为干净可安装内容
  coding/<skill>/SKILL.md
registry/
  upstream/               # fork 的 upstream 原始副本(绝不进项目)
    <skill>/
      SKILL.md            # pristine,upstream 原样
      ...                 # upstream 的其他文件
      meta.yaml           # 来源元数据
  projects.yaml           # 【手工维护·唯一输入】要扫描的项目路径清单
  third-party.md          # 【自动生成·勿手改】人读总账
  inventory.json          # 【自动生成·可选】机器可读总账
docs/superpowers/specs/   # 设计文档
```

## 5. Fork 约定(详细)

### 5.1 魔改版(可安装)

住在分类目录下,**只放可安装内容**,与原创 skill 外观一致:

```text
skills/coding/handoff/
  SKILL.md            # 魔改版,实际被安装的版本(+ 真正需要的资源)
```

### 5.2 upstream 原始副本(集中存放,永不安装)

```text
registry/upstream/handoff/
  SKILL.md.orig       # pristine upstream 副本,SKILL.md 必须改名为 .orig(见下)
  ...                 # upstream 的其他文件(如 references/、scripts/)原样保留
  meta.yaml           # 来源元数据
```

> **已验证的关键约束**:`npx skills` 按字面文件名 `SKILL.md` 在**整个仓库**递归发现 skill,且无 ignore/exclude 选项。pristine 若仍叫 `SKILL.md`,会被误收录成可安装 skill(还会和真 fork 撞名)。因此快照里每个 `SKILL.md` 一律改名为 `SKILL.md.orig`;diff 仍基于内容,不受影响。点目录(`.upstream/`)也不能规避——已实测点目录不被发现逻辑跳过。

`registry/upstream/handoff/meta.yaml`:

```yaml
source: https://github.com/mattpocock/skills.git   # upstream 源仓库
ref: main                                           # 分支 / tag
commit: <sha>                                       # 抓取时的精确 commit
upstream_path: handoff                              # 在源仓库内的子路径
local_path: skills/coding/handoff                   # 本仓库内魔改版位置
fetched_at: 2026-06-27                              # 抓取日期
notes: |
  - 改了 X
  - 删了 Y
```

### 5.3 创建 fork 的流程(由 manage-skills 固化)

1. 抓取 upstream 指定 skill 到临时目录,记录 `ref` / `commit`。
2. 把 pristine 文件落到 `registry/upstream/<skill>/`,写 `meta.yaml`。
3. 复制一份到 `skills/<cat>/<skill>/` 作为魔改版起点,按需修改。
4. 跑只读校验:`npx skills add ~/Coder/skills --list`,确认 fork 被识别为单个 skill。

### 5.4 从 upstream 更新 fork 的流程

三方对比:

- A:新抓取的 upstream(临时目录)
- B:`registry/upstream/<skill>/`(旧 pristine)
- C:`skills/<cat>/<skill>/`(你的魔改版)

步骤:diff A↔B 得到 upstream 的增量 → 把想要的增量挑进 C → 用 A 刷新 B(覆盖 pristine)→ 更新 `meta.yaml` 的 `commit` / `fetched_at` / `notes`。

## 6. 中心总账(registry)

### 6.1 输入:`registry/projects.yaml`(手工维护,很小)

```yaml
projects:
  - /Users/jfmoe/Coder/foo
  - /Users/jfmoe/Coder/bar
```

### 6.2 输出:`registry/third-party.md`(自动生成)

带「自动生成,勿手改」头,分三段:

1. **全局第三方**:全局安装的、非自创的 skill,含来源。
2. **各项目第三方**:遍历 `projects.yaml`,列每个项目装的第三方 skill + 版本 / commit。
3. **本仓库 Forks**:扫 `registry/upstream/*/meta.yaml`,列 fork 名、upstream 来源、`ref`/`commit`、`fetched_at`。

### 6.3 输出:`registry/inventory.json`(可选,机器可读)

同样三段内容的结构化版本,便于后续工具消费。是否生成由实现阶段决定;若实现简单则一并产出。

## 7. 扫描脚本规格

- 位置:`skills/workflows/manage-skills/scripts/sync-registry.mjs`(随 manage-skills 一起安装,职责自洽)。
- 职责:
  1. **全局第三方**:读全局 lock `~/.agents/.skill-lock.json`(version 3,含 `source`/`sourceType`/`sourceUrl`/`skillPath`),过滤掉自创的。
  2. **各项目**:遍历 `projects.yaml` → 读各项目 `skills-lock.json`(version 1,含 `source`/`sourceType`/`skillPath`/`computedHash`)→ 记第三方项。
  3. **Forks**:扫 `registry/upstream/*/meta.yaml`。
  4. **输出**:重写 `registry/third-party.md`(带生成头)+ `registry/inventory.json`。
- 自创判定:`source === 'jfmoe/skills'`、`sourceUrl` 含 `jfmoe/skills`、或 `sourceType: local` 且路径解析为本仓库根。
- 幂等:输出经排序、无时间戳,多次运行结果稳定(便于 git diff 审阅)。
- 失败处理:某项目路径不存在 / 无 `skills-lock.json` 时,跳过并在「Scan notes」段标注,不让整次扫描失败。

### 7.1 数据源(已验证)

- 全局 lock 文件名是 `~/.agents/.skill-lock.json`(点开头,version 3);项目级是各项目根的 `skills-lock.json`(version 1)——两者文件名与 schema 不同,脚本分别处理。
- 两份 lock 都带 `source`/`sourceType`/`skillPath`,足以判定第三方与来源;无需依赖 `ls --json`(后者不含来源)。
- 实跑结果:9 个全局第三方 + 5 个项目共 59 条;并发现旧手工 `third-party.md` 已漂移(仅记 4 条,实际全局有 9 条),印证重构必要性。

## 8. 配套文档改动

- **AGENTS.md**:
  - 补充三类 skill 概念模型。
  - 补充 fork 布局:魔改版在 `skills/<cat>/<skill>/`,pristine 在 `registry/upstream/<skill>/`,严禁把 upstream 副本放进 skill 文件夹。
  - 说明 `registry/third-party.md` 为**生成物**,`registry/projects.yaml` 为唯一手工输入,生成物勿手改。
  - 放宽原「registry 仅限 third-party.md」一条,允许 `registry/upstream/`、`registry/projects.yaml`、生成的 `inventory.json`,以及 manage-skills 下的脚本。
- **README.md**:更新 Layout 段落,反映新结构。
- **skills/workflows/manage-skills/SKILL.md**:新增三段流程——「创建 fork」「从 upstream 更新 fork」「同步总账 / 维护 projects.yaml(跑 sync-registry.mjs)」。

## 9. 验收标准

1. fork 一个第三方 skill 后:`skills/<cat>/<skill>/` 干净可安装;`registry/upstream/<skill>/` 有 `SKILL.md.orig` + `meta.yaml`。
2. 把该 fork 安装进任意项目,项目里**不出现** upstream 副本或第二个 SKILL.md。
3. `npx skills add ~/Coder/skills --list` 把每个 fork 识别为**单个** skill,pristine 快照不出现在列表里。
4. 跑 `sync-registry.mjs` 后,`registry/third-party.md` 三段(全局 / 各项目 / forks)内容与真实状态一致;重复运行结果稳定。
5. AGENTS.md / README / manage-skills 文档与新结构一致。

## 10. 非目标(YAGNI)

- 不用 git subtree / submodule 管理 upstream(已排除)。
- 不做 fork 与 upstream 的自动合并;diff 后由人工挑选变更。
- 不自动发现项目;扫描范围严格由 `registry/projects.yaml` 决定。
- 不记录项目级安装到 `third-party.md` 之外的手工台账(项目级复现由各项目 `skills-lock.json` 负责)。
