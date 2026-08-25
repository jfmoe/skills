# 泄漏 few-shot 示例

这些示例提炼自 2026 年 8 月的全仓清理及后续 review。应用时识别支配原则，不要把文字当成模板。本文有意引用泄漏措辞作为校准材料；[召回检索式](recall-batteries.zh.md)会排除本 Skill 目录，本文写法也不代表其他位置可以使用。

## 失效引用

### 有已提交所有者的决定序号

**泄漏：** “斜杠输入根据可见目录解析（decision 21）。”

**修复：** “斜杠输入根据可见目录解析——这是纯文本引用决定，由 [web 输入状态机 note](https://github.com/deepseek-ai/deepseek-harness/blob/b150a551b8d465e31e418e1b2eaf5e79bbb7d28e/.agents/notes/implemented/architecture/2026-07-25-web-input-machine-and-slash-pipeline.md)负责。”

该序号在当前仓库状态无法解析；决定名称和所属 note 路径可以解析。每个文件至少按路径链接一次所属 note，后续可以只使用可搜索名称。

### 没有所有者的决定序号

**泄漏：** “注册表拒绝重复名称（decision 7：名称是扁平的，不使用命名空间）。”

**修复：** “注册表拒绝重复名称；名称是扁平的，不使用命名空间。”

没有已提交产物拥有“decision 7”，因此删除引用；但“名称扁平”这一事实条款需要改写成独立成立的句子，不能和引用一起删除。

### 审计项编号

**泄漏：** “渲染是纯函数：相同快照产生相同字符串（audit R3）。”

**修复：** “渲染是纯函数：相同快照产生相同字符串。”

仓库中没有对应审计文档；编号只是会话速记，不承载命题。

### 未提交草稿章节号

**泄漏：** “分层遵循设计稿（v2 §3.2）：`src/core/` 是纯核心。”

**修复：** “分层规则：`src/core/` 是纯核心。”

无人提交的草稿 `§N` 无法解析。对比之下，“根据 RFC 9110 §10.1.5 转义”应保留：外部标准按设计在仓库外解析；拥有固定章节编号的已提交文档也可以按章节引用。

### 计划阶段标签

**泄漏：** “`src/client/` 是 shell（T4）；P-I 迁移负责适配器。”

**修复：** “`src/client/` 是 shell；适配器位于 `src/client/adapters/`。”

阶段标签索引的是从未提交的计划。应使用该阶段真正产出的事实替换标签。

## 堆叠和 PR 视角

### 长期文字中的堆叠位置

**泄漏：** “未来远程后端会实现这个接口（沙箱后端是该 stack 中后续的 PR）。”

**修复：** “远程后端可以实现该接口，无需修改渲染层。”

长期文字看不到 PR stack。保留扩展点约定；待完成工作应放在 PR、`TODO` 或 issue 中。

### README 中的“本 PR”

**泄漏：** “本 PR 为会话列表增加基于游标的分页。”

**修复：** “会话列表使用游标分页。”

README 会比任何 PR 存在得更久；应把机制写成当前事实。

## 变更叙述和版本戳

### 带 PR 编号的踩坑故事

**泄漏：** “颜色以前来自没有任何定义的 `--widget-*` token，所以总是显示 fallback；别名 token 修复了它（PR #88）。”

**修复：** “颜色来自别名 token；未定义 token 时显示 fallback。”

两个当前事实都应保留：现行机制和长期失败行为；两者改为现在时。缺陷经历属于 PR 和相应决策记录。

### 删除过程叙述

**泄漏：** “`probe` 字段随删除改动消失；badge 现在使用通用 projection pair。”

**修复：** “Badge 使用通用 projection pair。”

从未见过 `probe` 的读者无法从“它不存在”得到任何信息。与已删除过去状态对比的“现在”属于版本戳。

### 已修复回归改成现在时反事实

**泄漏：** “以前会对多字节标签执行两次编码。”

**修复：** “没有字节长度保护时，多字节标签会被编码两次。”

回归约束以现在时反事实保留，并指出保护机制；“以前”只会把读者引向仓库考古。

### 索引式版本戳

**泄漏：** “本次改动中批量渲染是同步的；异步路径属于 roadmap。”

**修复：** “批量渲染是同步的。”（暂缓事项放到调用点的 `TODO(widget-batch):`。）

“this cut”“v1”“today”在合入后立即陈旧。决策记录的变更故事章节可以使用历史阶段名称，例如“第一版发布了 X”；索引式写法始终不合适。

## Review 过程

### 把 review 结论写进正文

**泄漏：** “Review 中否决：缓存解析后的 spec。我们保留逐次调用解析。”

**修复（放在决策记录的 Alternatives considered）：** “**缓存解析后的 spec。** 否决：spec 依赖每次调用的 cwd，因此按请求建立缓存会返回陈旧根目录。”

“备选方案”文体是允许的位置；评审人和轮次不是理由的一部分。

### 草稿序号

**泄漏：** “截至本 note 的 v5，loader 还会验证 manifest。”

**修复：** “Loader 验证 manifest。”

已实施决策记录描述发布事实；自身修订历史由 git 保存。

## 面向评审人的辩解

### 为类型转换辩护

**泄漏：** “该 cast 是安全的——SDK 构造了对象，只是没有把可选字段声明得足够严格。”

**修复：** “SDK 构造对象时会填充每个可选字段；声明类型比运行时保证更宽松。”

说明维护者不能破坏的不变量。“只是……”是在回应当前仓库状态中不存在的质疑。如果代码已明显表达该不变量，应删除注释。

### 诉诸 review 权威

**泄漏：** “这是正确的，因为评审人确认了包装顺序。”

**修复：** 删除；包装顺序已经写在函数的 `@returns` 中。

正确性主张引用不变量或测试，不引用个人。

## 复述和推导

### 控制流叙述

**泄漏：** “先规范化标签，再截断，然后包装。”

**修复：** 删除。

注释下方三行代码已经表达同一内容。

### 测试过程说明

**泄漏：** “这个测试创建会话、发送两条消息、等待第二次回复，然后断言日志包含四项。”

**修复：** “两次往返必须产生恰好四条日志项；projection 会去重共享前缀。”

只保留不明显的断言理由；过程说明只是复述测试体。

## 保留语气和规划残留

### 没有标记的暂缓事项

**泄漏：** “目前急切渲染应该没问题。”

**修复：** 删除；暂缓事项已有 `TODO(widget-batch):` 标记。

没有所有者的保留语气属于规划残留。如果不存在标记，应写一个，例如 `TODO(widget-batch): coalesce per animation frame`，而不是保留模糊语气。

### 模糊容量

**泄漏：** “64 KiB 缓冲区对大多数情况应该足够。”

**修复：** “64 KiB 可以容纳当前观察到的最大 frame（48 KiB），并留有余量；更大 frame 会在 `decode` 中明确失败。”

用实际边界及超限时的失败行为替换保留语气。

## 写作语言残留

**泄漏：** “The renderer runs on the client 端; see the 设计稿 for spacing. ---- 私有 ----”

**修复：** “渲染器在客户端运行；间距遵循 Figma frame `widget-badges`。”

工作语言片段和会话分隔符属于转录残留。Figma frame 名称应保留：它是按设计在仓库外解析的外部来源。

## 应保留的内容

### Issue 引用在任何位置都长期有效

**保留：** “上限作用于包括包装层在内的完整渲染值（后续工作由 issue #1470 负责）。”

没有辅助判断的清理曾删除该句，理由是 issue 引用属于决策记录。方向错误：issue 在任何位置都能根据当前仓库状态解析，“#N 负责后续工作”正是 README 中暂缓工作的允许归属。决策记录和事故记录额外允许把**已合并 PR**作为证据。

### 失效名称不等于“指明所有者”

**删除：** “Widget seam 上的 badge 渲染器（见 widget-rendering RFC）。”

没有辅助判断的清理曾把它当成“按主题指明所属文档”而保留。判断标准是能否解析，不是形式：仓库中没有名为“widget-rendering RFC”的已提交文件。如果存在已提交所有者，应重新指向它；否则删除。

### 抑制规则理由

**保留（修正后）：** `// oxlint-disable-next-line no-non-null-assertion -- the one-element literal guarantees index 0.`

理由条款属于必要文字。原理由不真实时，例如声称“上方循环保护保证存在 frame”但根本没有循环，应修正理由，不能删除。

### 测量边界

**保留：** “深度上限（测量结果：512 层嵌套约为 0.15 秒同步时间；4096 层会阻塞循环）。”

测量结果能够防止在缺乏信息时随意调整常量；“测量结果”提供了数据来源，区分事实和猜测。

### 运行时 old/new 不是变更历史

**保留：** “旧连接完成排空后，新连接才接受请求。”

这里的“旧”和“新”是切换期间同时存在的运行时对象，不是仓库状态。变更叙述禁令针对仓库历史，不针对生命周期词汇。

## 过度修正陷阱

以下每种错误都曾在最初清理中合入，随后被 review 发现。精简前先列出段落命题。

### 把义务翻转为认可

**原文：** “These direct registrations are exceptions pending migration to slots.”

**过度修正：** “These direct registrations are sanctioned exceptions.”

**正确：** “These direct registrations are exceptions pending migration to slots.”

“Pending migration”是一项义务；“sanctioned”则认可现状。精简在缩短文字的同时反转了语气强度。

### 把假设提升为已发布功能

**原文：** “A future IPC-based shell subclasses the executor and overrides `spawn`.”

**过度修正：** “An IPC-based shell subclasses the executor and overrides `spawn`.”

**正确：** “A hypothetical IPC-based shell—no such shell exists—would subclass the executor and override `spawn`.”

只删除未来标记，会把设计示例变成“该类已经发布”的主张。应明确标记假设，而不是简单去掉未来语气。

### 连同推理过程删除真实事实

**原文：** “The gate notice narrates the check order; the notice text is also what `verify-doc-typecheck` compiles against.”

**过度修正：** 删除整个句子，认为它都是叙述。

**正确：** “The notice text is what `verify-doc-typecheck` compiles against.”

句子前半是叙述，后半是关键耦合。当多个命题共享一行时，应按条款删除，不要整句删除。

### 保留数字却丢失来源

**原文：** “The 4 MiB ceiling is measured: the largest generated `py-types` module is 3.1 MiB.”

**过度修正：** “The ceiling is 4 MiB; the largest generated `py-types` module is 3.1 MiB.”

**正确：** 保留“measured”。

没有“measured”，3.1 MiB 看起来像定义，而不是观察结果；以后提高上限时也没人知道需要重新测量。
