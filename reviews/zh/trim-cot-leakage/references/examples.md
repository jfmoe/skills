# 小样本泄露示例

提炼自 2026-08 全仓库清理行动及其评审轮次。用它们来识别主导原则，而不是当作文本模板。本文件刻意引用泄露措辞作为校准材料——[召回探针组](recall-batteries.md)已排除该 skill 的目录，这些措辞不构成在其他地方使用的许可。

## 失效引用

### 有已提交归属者的决策序数

**泄露：** "Slash input resolves against the visible catalog (decision 21)."

**修复后：** "Slash input resolves against the visible catalog — the plain-text-reference decision, owned by [the web input-machine note](https://github.com/deepseek-ai/deepseek-harness/blob/b150a551b8d465e31e418e1b2eaf5e79bbb7d28e/.agents/notes/implemented/architecture/2026-07-25-web-input-machine-and-slash-pipeline.md)."

该序数在 HEAD 处无处可解析；决策的名称和归属笔记路径可以。每个文件至少一次给出归属笔记的路径——在表面支持链接时用链接形式——之后的提及可以只用可搜索的名称。

### 没有归属者的决策序数

**泄露：** "The registry rejects duplicate names (decision 7: names are flat, no namespacing)."

**修复后：** "The registry rejects duplicate names; names are flat, with no namespacing."

没有任何已提交产物拥有 "decision 7"，所以引用被删除——但它的事实性子句（扁平命名）被重述为独立成立的表述，而不是随引用一起删除。

### 审查条目编号

**泄露：** "Rendering is pure: same snapshot, same string (audit R3)."

**修复后：** "Rendering is pure: same snapshot, same string."

仓库中不存在任何审查文档；该编号是纯会话速记，承载零个命题。

### 未提交草稿的章节号

**泄露：** "Layering follows the design (v2 §3.2): `src/core/` is the pure core."

**修复后：** "Layering: `src/core/` is the pure core."

没人提交过的草稿的 `§N` 不可解析。对照："escapes per RFC 9110 §10.1.5" 保留——外部标准按设计在仓库之外可解析，而拥有自己 § 编号体系的已提交文档可以按章节引用。

### 计划阶段标签

**泄露：** "`src/client/` is the shell (T4); the P-I migration owns the adapters."

**修复后：** "`src/client/` is the shell; the adapters live in `src/client/adapters/`."

阶段标签索引的是一份从未落地的计划。用该阶段实际产出的东西替换标签。

## 栈与 PR 视角

### 耐久行文中的栈位置

**泄露：** "A future remote backend implements this interface (the sandbox backend is a later PR in this stack)."

**修复后：** "A remote backend can implement this interface without changing the render layer."

耐久行文看不到栈。保留扩展点契约；待办工作的去处是 PR 本身、一个 `TODO`，或一个 issue。

### README 中的 "This PR"

**泄露：** "This PR adds cursor-based pagination to the session list."

**修复后：** "The session list paginates by cursor."

README 比每个 PR 都活得久；把机制陈述为当前事实。

## 变更叙述与版本印记

### 带 PR 编号的战史

**泄露：** "Colors used to come from `--widget-*` tokens, which nothing defined, so it always rendered the fallbacks; the alias tokens fixed that (PR #88)."

**修复后：** "Colors come from the alias tokens; an undefined token renders the fallbacks."

两个存活的事实都保留了——当前机制和持续存在的失败行为——以现在时重述。这个 bug 的传记属于 PR 及其 Agent Note。

### 移除叙述

**泄露：** "The `probe` field is gone with the removal cut; badges ride the generic projection pair now."

**修复后：** "Badges use the generic projection pair."

从未见过 `probe` 的读者从它的缺席中学不到任何东西。与被删除的过去形成对照的 "now" 是版本印记。

### 已修复的回归 → 反事实现在时

**泄露：** "This used to double-encode multibyte labels."

**修复后：** "Without the byte-length guard, multibyte labels double-encode."

回归钉以指名防护手段的现在时反事实形式幸存；"used to" 则把它钉进了仓库考古。

### 指示性版本印记

**泄露：** "Batch rendering is synchronous this cut; the async path is roadmap work."

**修复后：** "Batch rendering is synchronous."（推迟项放在调用点的 `TODO(widget-batch):` 中。）

"This cut" / "v1" / "today" 在合并的那一刻就过时了。Agent Note 变更故事章节内的历史阶段名（"the first cut shipped X"）对当前状态是安全的；指示性形式永远不安全。

## 评审过程编排

### 变成行文的评审结论

**泄露：** "Rejected in review: caching the resolved spec. We keep resolution per-call."

**修复后（在 Agent Note 的 Alternatives considered 中）：** "**Caching the resolved spec.** Rejected: the spec depends on per-call cwd, so a cache keyed by request would serve stale roots."

alternatives-considered 体裁是被认可的去处；评审者和轮次不属于理由的一部分。

### 草稿序数

**泄露：** "As of v5 of this note, the loader also validates manifests."

**修复后：** "The loader validates manifests."

一份已实现笔记陈述的是已交付的现实；它自己的修订历史活在 git 里。

## 面向评审者的辩解

### 为一次类型转换辩护

**泄露：** "The cast is safe — the SDK constructed the object, it simply doesn't declare the optionals strictly enough."

**修复后：** "The SDK constructs this object with every optional populated; the declared type is looser than the runtime guarantee."

陈述维护者不得破坏的不变式。"It simply…" 是在回应一个 HEAD 处没人提出的异议的声音。如果该不变式在代码中可见，就改为删除这条注释。

### 诉诸评审权威

**泄露：** "This is correct because the reviewer confirmed the wrapping order."

**修复后：**（删除；包裹顺序已在函数的 `@returns` 中陈述。）

正确性论断引用不变式或测试，绝不引用人。

## 复述与推导

### 控制流叙述

**泄露：** "First we normalize the label, then we truncate it, then we wrap it."

**修复后：**（删除。）

注释下方的三行代码已经用代码说了同样的事。

### 测试过程复述

**泄露：** "This test creates a session, sends two messages, waits for the second reply, and then asserts the log has four entries."

**修复后：** "Two round-trips must produce exactly four log entries — the projection dedupes the shared prefix."

只保留非显而易见的断言理由；过程复述只是重复测试体。

## 含糊措辞与规划残留

### 无标记的推迟

**泄露：** "Probably fine to render eagerly for now."

**修复后：**（删除；该推迟已有其 `TODO(widget-batch):` 标记。）

没有归属者的含糊措辞就是规划残留。如果没有标记，写一个（`TODO(name): coalesce per animation frame`），而不是保留含糊措辞。

### 模糊的规模估计

**泄露：** "A 64 KiB buffer should be enough for most cases."

**修复后：** "64 KiB holds the largest observed frame (48 KiB) with headroom; a larger frame fails loudly in `decode`."

用真实的界限和超出界限时的失败行为替换含糊措辞。

## 创作语言混入

**泄露：** "The renderer runs on the client 端; see the 设计稿 for spacing. ---- 私有 ----"

**修复后：** "The renderer runs on the client side; spacing follows the Figma frame `widget-badges`."

工作语言片段和会话分隔符是转写残留。Figma frame 名称保留：按设计在仓库之外可解析的外部来源。

### 成对代码围栏内的创作语言混入

**两个文件中都泄露：** 逐字代码块内的 `// 更新这里 before returning`。

**两个文件中都修复为：** `// Update this before returning.`

修正该代码块一次，然后把这段逐字节一致的围栏复制进两个语言文件。在对应副本中用不同的方式翻译代码注释会破坏成对契约——即使两条注释各自都通顺。

## 行为可见的候选项

**可疑：** 一条导出的 JSDoc 句子写着 "available for now"，而一个生成器把这句话复制进了模型可见的目录。

**错误：** 在一次纯行文清理中只改写源句子，或者只手工编辑生成的目录。

**正确：** 追踪源的生成扇出，更新归属者，重新生成每个衍生物，并更新归属的可运行快照。对于用户可见的字符串，附上仓库要求的行为证据。如果获授权的范围内没有归属场景，保持措辞不变并报告该推迟。

## 保留项

### Issue 引用在每个表面都是耐久的

**保留：** "The cap applies to the complete rendered value, wrappers included (issue #1470 owns the follow-up)."

一次无辅助的排查删掉了它，理由是 issue 引用属于 Agent Notes。方向错了：issue 在任何表面上都能在 HEAD 处解析，而 "#N owns the follow-up" 是 README 中推迟工作的被认可去处。Agent Notes 和事后复盘额外认可的是引用*已合并的 PR* 作为证据。

### 失效的点名不算"指名归属者"

**删除：** "Badge renderer over the widget seam (see the widget-rendering RFC)."

一次无辅助的排查把它保留为"按主题指名归属文档"。判据是可解析性，不是形式：没有任何已提交文件对应 "the widget-rendering RFC"，所以这个指针是死的。如果存在已提交的归属者，把它重定向过去；否则删除它。

### 抑制说明

**保留（修正后）：** `// oxlint-disable-next-line no-non-null-assertion -- the one-element literal guarantees index 0.`

理由子句是必需的行文。当所述理由为假时（原文写 "the loop guard above proves a frame exists"，但附近根本看不到循环），修正理由；绝不删除。

### 实测界限

**保留：** "Depth cap (measured: 512 nests ≈ 0.15s synchronous; 4096 blocks the loop)."

该测量值把常量钉住，防止不知情地重新调参，而 "measured" 是区分数据与猜测的来源标记。

### 运行时的新旧不是变更历史

**保留：** "The old connection drains before the new one accepts."

这里的 "old" 和 "new" 指代交接过程中的两个存活运行时对象，不是仓库状态。变更叙述禁令针对的是仓库历史，不是生命周期词汇。

### 运行时的自然时间不是版本印记

**保留：** "What is today's date?"

该 prompt 询问的是运行时时钟；"today" 不构成仓库状态之间的对照。因为这段文字会到达模型，任何改写仍然需要其归属的行为证据。

## 过度修正陷阱

下面每个陷阱都曾在最初的清理行动中实际交付，并在评审中被抓住。修剪一个段落之前先枚举它的命题。

### 把义务翻转成背书

**原文：** "These direct registrations are exceptions pending migration to slots."

**过度修正：** "These direct registrations are sanctioned exceptions."

**正确：** "These direct registrations are exceptions pending migration to slots."

"Pending migration" 是义务；"sanctioned" 是为现状背书。修剪在缩短句子的同时翻转了它的情态。

### 把假设提升为已交付特性

**原文：** "A future IPC-based shell subclasses the executor and overrides `spawn`."

**过度修正：** "An IPC-based shell subclasses the executor and overrides `spawn`."

**正确：** "A hypothetical IPC-based shell — no such shell exists — would subclass the executor and override `spawn`."

仅仅删除未来标记会把一个设计示例变成对类已交付的断言。要显式标出假设，而不是仅仅取消未来标记。

### 连同周围的会话记录删掉真实事实

**原文：** "The gate notice narrates the check order; the notice text is also what `verify-doc-typecheck` compiles against."

**过度修正：** "…"（整句作为叙述被删除。）

**正确：** "The notice text is what `verify-doc-typecheck` compiles against."

句子的前半是叙述；后半是一个承重的耦合关系。当多个命题共享一行时，删除子句，而不是整个句子。

### 保留数字却丢弃来源

**原文：** "The 4 MiB ceiling is measured: the largest generated `py-types` module is 3.1 MiB."

**过度修正：** "The ceiling is 4 MiB; the largest generated `py-types` module is 3.1 MiB."

**正确：** 保留 "measured"。

没有 "measured"，3.1 MiB 读起来像是定义而非观测值，也就没人在抬高上限之前重新测量。
