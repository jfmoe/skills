# 召回探针组

针对[分类法](../SKILL.md#taxonomy)的探针，在 2026-08 清理行动期间调优。每个命中都需要语义判断——探针组按设计会过度匹配，而按天性又会匹配不足：清理行动的每一轮评审都发现了没有任何探针捕获到的案例，所以要配合一次对范围内最密集行文的无模式通读。

## 调用规则

- 加上 `--hidden --glob '!.git/**'`，使 `.agents/` 被搜索到；ripgrep 默认跳过点目录，而清理行动最大的漏报风险就在 Agent Notes。
- 排除项放在最后，使后面的 include 无法再把它们重新放进来：加入目标仓库的受保护、依赖、冻结记录、fixture 和快照路径，再加上 `--glob '!**/trim-cot-leakage/**'`，因为该 skill 自己的文件会引用泄露措辞作为校准材料。一份 rationale 文档也可能通过引用的证据而自命中；把它当证据判断，而不是当使用情况。
- 自然语言行携带 `-i`，让句首大写也能命中（"This PR adds…"、"Probably fine…"）；第一行匹配代码模式，保持大小写敏感——`-i` 会把 `\bT\d\b` 和 `\bP-I\b` 变成噪声。
- 界定完整短语。`\bthis PR\b` 必须匹配 "this PR adds"，同时不匹配 "this project"、"this process" 或 "this provider"。
- 一个零命中的模式在匹配到已知正例之前什么都证明不了；一个噪声很大的模式在拒绝一个险些误报的负例之前也什么都证明不了。在信任语料结果之前，两者都要校准。
- 把创作语言探针指向相反语言的表面：在以英文为主的 Markdown 和代码注释/JSDoc 中搜索工作语言残留，并在 `*.zh.md` 内搜索工作语言的变更叙述。对中文行文中的英文残留做通用 ASCII 搜索在代码和标识符附近噪声太大；改为把行文的新增内容与对应副本做比较。

## English battery

```sh
rg -n --hidden '\(decision \d|\(audit [A-Z]\d|design §|plan §|design ledger|\(B ruling|\bP-I\b|\bW\d\b|\bT\d\b' ...
rg -n --hidden -i '\bthis PR\b|\bthis branch\b|\bthis stack\b|\blater PRs?\b|\bprevious commits?\b|\bthis commit\b' ...
rg -n --hidden -i '\bused to\b|\bno longer\b|\bpreviously\b|\bthe old\b|\bwas renamed\b|\bwas moved\b' ...
rg -n --hidden -i '\bv1\b|this cut|\bcut \d|\btoday\b|\bfor now\b|roadmap' ...
rg -n --hidden -i 'rejected in review|review round|reviewer|as of v\d' ...
rg -n --hidden -i 'probably |should be enough|should suffice|it simply|is safe —|is safe --' ...
rg -n --hidden '§\d' ...
```

## Chinese batteries

```sh
# Change or review narration in Chinese counterparts.
rg -n --hidden '评审|上一?轮|旧版|老的|不再|以前|本版|遗留' --glob '*.zh.md' ...

# Chinese authoring-language slips in English Markdown.
rg -n --hidden '设计稿|评审|上一?轮|旧版|老的|不再|以前|本版|遗留|私有|(^|[^a-zA-Z])端([^a-zA-Z]|$)' --glob '*.md' --glob '!*.zh.md' ...

# Chinese authoring-language slips in English code comments and JSDoc.
rg -n --hidden '(^[[:space:]]*(//|/\*|\*)|//|/\*)[^\r\n]*(设计稿|评审|上一?轮|旧版|老的|不再|以前|本版|遗留|私有|端)' --glob '*.{ts,tsx,js,jsx,mjs,cjs,css}' ...
rg -n --hidden '#[^\r\n]*(设计稿|评审|上一?轮|旧版|老的|不再|以前|本版|遗留|私有|端)' --glob '*.py' ...
```

## 已知的误报家族

在清理行动期间经过判定并保留；预期还会再次遇到：

- **工具性的 "used to"** —— "the key used to sign requests" 是工具性用法，不是时间性用法。时间性用法前面会有一个主语状态（"colors used to come from…"）。
- **运行时的新旧** —— "the old connection drains before the new one accepts" 指代交接过程中的存活对象，不是仓库状态。
- **流程文档中的 "This PR"** —— *关于* PR 工作流的文档（"the PR body should…"、模板、本仓库的流程说明）合法地使用 "PR"；禁令针对的是文档站在某个 PR 的视角谈论代码。
- **作为协议或路径段的 `v1`** —— `/v1/chat` 端点和线格式名称是标识符，不是版本印记。
- **带有已提交归属者的 `§N`** —— 外部标准（RFC 9110 §10.1.5）和拥有自己 § 编号体系的已提交文档仍然可以按章节引用。
- **对照性的 "actually" 和名词性的 "wait"** —— 普通英语，不是含糊措辞；没有任何已提交行去探测它们，所以只有当你用更宽泛的含糊措辞模式扩展探针组时它们才会浮现。
- **运行时的 "today" 和录制的时间戳** —— 询问当前日期的 prompt 或测试使用的是自然时间，而不是仓库版本印记；录制的 CLI 输出保留它自己的语气。到达模型或用户的措辞在任何编辑之前仍然遵循行为证据规则。
- **中文行文中的"本版本"** —— 在有版本产物的语境中是 "this release" 的合法译法；被禁的指示词是作为裸印记、对应 "this cut" 的"本版"。
- **Alternatives-considered 章节** —— Agent Note 体裁槽位里的 "rejected" 是被认可的去处，不是评审过程编排。
