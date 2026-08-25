# 召回检索式

这些检索式用于探测[分类体系](../SKILL.zh.md.review#分类体系)，在 2026 年 8 月的清理中完成校准。每个命中都需要语义判断：检索式有意扩大匹配范围，因此会误报；它们本质上也会漏检。最初清理的每轮 review 都发现了检索式没有捕获的情况，因此还要在没有模式提示的情况下阅读范围内文字最密集的位置。

## 调用规则

- 添加 `--hidden --glob '!.git/**'`，使 `.agents/` 等隐藏目录也被搜索；ripgrep 默认跳过点目录。
- 排除项放在最后，避免后续 include 重新纳入：加入目标仓库的受保护目录、依赖目录、冻结记录、fixture 和快照路径，再加入 `--glob '!**/trim-cot-leakage/**'`，因为 Skill 自己会引用泄漏措辞作为校准材料。理由文档也可能因为引用证据而命中；应将其判断为证据，不是实际用法。
- 自然语言行使用 `-i`，使句首大写形式也能命中，例如“This PR adds…”和“Probably fine…”。第一行匹配代码模式，保持大小写敏感；加入 `-i` 会让 `\bT\d\b` 和 `\bP-I\b` 产生大量噪声。
- 在已知正例上确认检索式能够命中之前，零结果不能证明不存在问题。

## 英文检索式

```sh
rg -n --hidden '\(decision \d|\(audit [A-Z]\d|design §|plan §|design ledger|\(B ruling|\bP-I\b|\bW\d\b|\bT\d\b' ...
rg -n --hidden -i 'this PR|this branch|this stack|later PR|previous commit|this commit' ...
rg -n --hidden -i 'used to |no longer|previously|the old |was renamed|was moved' ...
rg -n --hidden -i '\bv1\b|this cut|\bcut \d|\btoday\b|\bfor now\b|roadmap' ...
rg -n --hidden -i 'rejected in review|review round|reviewer|as of v\d' ...
rg -n --hidden -i 'probably |should be enough|should suffice|it simply|is safe —|is safe --' ...
rg -n --hidden '§\d' ...
```

## 中文检索式

```sh
rg -n --hidden '设计稿|评审|上一?轮|旧版|老的|不再|以前|本版|遗留|私有' ...
rg -n --hidden '(^|[^a-zA-Z])端([^a-zA-Z]|$)' --glob '*.md' ...
```

## 已知误报类别

以下情况在清理中经过判断并保留；预期以后仍会出现：

- **工具用途的“used to”**——“the key used to sign requests”中 `used to` 表示“用于”，不是时间。时间形式会在前面带有主体状态，例如“colors used to come from…”。
- **运行时 old/new**——“the old connection drains before the new one accepts”指切换期间的实时对象，不是仓库状态。
- **流程文档中的“This PR”**——讲解 PR 工作流的文档可以合理地写“the PR body should…”。禁令针对文档采用某个具体 PR 的代码视角。
- **协议或路径中的 `v1`**——`/v1/chat` endpoint 和协议格式名称属于标识符，不是版本戳。
- **有已提交所有者的 `§N`**——外部标准和拥有固定章节编号的已提交文档可以按章节引用。
- **对比性的“actually”和名词“wait”**——它们是普通英文，不一定属于保留语气。已提交检索式不探测它们；只有扩展为更宽的模式时才会出现。
- **生成时间戳和 CLI 输出样例中的“Today”**——录制输出保留原有口吻。
- **中文版本化产物中的“本版本”**——在确实有版本的产物中，它可以合理翻译“this release”；禁止的是作为“this cut”对应物的裸“本版”。
- **Alternatives considered 章节**——决策记录特定文体位置中的“rejected”属于允许归属，不是 review 过程。
