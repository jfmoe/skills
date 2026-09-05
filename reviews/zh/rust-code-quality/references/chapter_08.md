# 第 8 章 - 注释 vs 文档

> 清晰的代码胜过清晰的注释。然而，当"为什么"不明显时，直白地注释出来——或者链接到可以阅读更多上下文的地方。

## 8.1 注释 vs 文档：弄清区别

| 用途 | 使用 `// comment` | 使用 `/// doc` 或 `//! crate doc` |
|-------------- |------------------------------------------- |---------------------------------------------------------------- |
| 描述"为什么" | ✅ 是——解释棘手的推理 | ❌ 不用于文档 |
| 描述 API | ❌ 没用 | ✅ 是——公共接口、用法、细节、错误、panic |
| 可维护性 | 🚨 常常会过时且难以推理 | ✅ 与代码绑定，出现在生成的文档中，并且可以运行测试用例 |
| 可见性 | 仅限本地开发 | 导出给用户以及 `cargo doc` 等工具 |

## 8.2 何时使用注释

当某些事情无法在代码中清晰表达时，使用 `//` 注释（双斜线），例如：
* **安全性保证**，其中一些可以更好地用代码条件表达。
* 变通方案或**优化**。
* 遗留或**特定平台**的行为。其中一些可以用 `#[cfg(..)]` 表达。
* 指向**设计文档**或 **ADR** 的链接。
* 不明显的假设或**坑**。

> 给你的注释命名！例如，关于安全性保证的注释应以 `// SAFETY: ...` 开头。

### ✅ 好的注释：
```rust
// SAFETY: `ptr` is guaranteed to be non-null and aligned by caller
unsafe { std::ptr::copy_nonoverlapping(src, dst, len); }
```

### ✅ 设计上下文注释：
```rust
// CONTEXT: Reuse root cert store across subgraphs to avoid duplicate OS calls:
// [ADR-12](link/to/adr-12): TLS Performance on MacOS
```

## 8.3 当注释成为障碍

避免以下注释：
* 重述显而易见的事情（`// increment i by 1 for the next loop`）。
* 会随着时间过时的注释。
* 没有后续行动的 `TODO`（应链接到某个版本化的 issue）。
* 可以用更好的命名或更小的函数替代的注释。

### ❌ 差的注释：
```rust
fn compute(counter: &mut usize) {
    // increment by 1
    *counter += 1;
}
```

### ❌ 太长或已过时
```rust
// Originally written in 2028 for some now-defunct platform
```

## 8.4 不要写"活文档"（活的注释）

把注释当作"活文档"是一个**危险的迷思**，因为注释**不是免费的**：
* 它们会**腐烂**——没有人编译注释。
* 它们会**误导**——读者通常不加批判地假设它们是真的，例如"另一个开发者比我更懂这段代码"。
* 它们会**过时**——除非与代码一起维护，否则就变得无关紧要。
* 它们**嘈杂**——注释会用多行不必要的内容弄乱你的代码。

如果某些内容值得活到 PR 之后，把它放在：
* 一份 **ADR**（架构设计记录）中。
* 一份设计文档中。
* 通过使用类型、文档注释、示例、把代码块重构成更清晰的函数，**在代码中**记录它。
* 添加测试来覆盖和解释这个变更。

> ### 🚨 如果你发现一条注释，**结合上下文阅读它**。它仍然说得通吗？如果说不通，删除或更新它，或者寻求帮助。注释应该让你感到不安。

## 8.5 用代码替代注释

与其写大段注释，不如把逻辑拆成有名字的辅助函数：

#### ❌ 注释式代码块：
```rust
fn save_user(&self) -> Result<(), MyError> {
    // check if the user is authenticated
    if self.is_authenticated() {
        // serialize user data
        let data = serde_json::to_string(self)?;
        // write to file
        std::fs::write(self.path(), data)?;
    }
}
```
**✅ 提取以获得清晰度**：

```rust
fn save_auth_user(&self) -> Result<PathBuf, MyError> {
    if self.is_authenticated() {
        let path = self.path();
        let serialized_user = serde_json::to_string(self)?;
        std::fs::write(path, serialized_user)?;
        Ok(path)
    } else {
        Err(MyError::UserNotAuthenticated)
    }
}
```

## 8.6 `TODO` 应该变成 issue

不要让没有负责人的 `// TODO:` 散落在代码库中。取而代之：
1. 提交 GitHub Issue 或 Jira 工单。（公共仓库优先用 GitHub Issues。）
2. 在代码中引用该 issue：

```rust
// TODO(issue #42): Remove workaround after bugfix
```

这让 `TODO` 可跟踪、可执行，并对所有人可见。

## 8.7 何时使用文档注释

使用 `///` 文档注释来记录：
* 所有**公共函数、结构体、trait、枚举**。
* 它们的用途、用法和行为。
* 开发者要正确使用它所需要理解的一切。
* 与 `Errors` 和 `Panics` 相关的上下文。
* 充足的示例。

### ✅ 好的文档注释：

```rust
/// Loads [`User`] profile from disk
///
/// # Error
/// - Returns [`MyError`] if the file is missing [`MyError::FileNotFound`].
/// - Returns [`MyError`] if the content is an invalid Json, [`MyError::InvalidJson`].
fn load_user(path: &Path) -> Result<User, MyError> {...}
```

**文档注释还可以包含示例、链接，甚至测试：**

```rust
/// Returns the square of the integer part of any number.
/// Square is limited to `u128`.
///
/// # Examples
///
/// ```rust
/// assert_eq!(square(4.3), 16)
/// ```
fn square(x: impl ToInt) -> u128 { ... }
```

## 8.8 Rust 中的文档：如何、何时以及为何

Rust 通过 rustdoc 提供**一流的文档工具**，这使得为代码编写文档成为编写地道、可维护 Rust 的关键部分。有一些专门的文档 lint 可以帮助你，例如：

| Lint | 说明 |
|-------------- |------------------------------------------- |
| [missing_docs](https://doc.rust-lang.org/rustdoc/lints.html#missing_docs) | 警告公共函数、结构体、常量、枚举缺少文档 |
| [broken_intra_doc_links](https://doc.rust-lang.org/rustdoc/lints.html#broken_intra_doc_links) | 检测内部文档链接是否失效。在重命名时特别有用。 |
| [empty_docs](https://rust-lang.github.io/rust-clippy/master/#empty_docs) | 禁止空文档——防止绕过 `missing_docs` |
| [missing_panics_doc](https://rust-lang.github.io/rust-clippy/master/#missing_panics_doc) | 警告：如果函数可能 panic，文档应有 `# Panics` 小节 |
| [missing_errors_doc](https://rust-lang.github.io/rust-clippy/master/#missing_errors_doc) | 警告：如果函数返回 `Result`，文档应有解释 `Err` 条件的 `# Errors` 小节 |
| [missing_safety_doc](https://rust-lang.github.io/rust-clippy/master/#missing_safety_doc) | 警告：如果面向公众的函数有可见的 unsafe 块，文档应有 `# Safety` 小节 |


### `///` 和 `//!` 的区别

| 风格 | 用于 | 范围 | 示例 |
|---------- |------------------------------ |------------------------------------------- |---------------------------------------------------------------- |
| `///` | 行级文档注释 | 公共条目，如 struct、fn、enum、const | 为 `fn`、`struct`、`enum` 等编写文档、提供上下文和用法 |
| `//!` | 模块级文档注释 | 模块或整个 crate | 用常见用例和快速上手来说明 crate/模块的用途 |

### `///` 条目级文档

对函数、结构体、trait、枚举、常量等使用 `///`：

```rust
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// let result = my_crate::add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```
* ✅ 清晰地写出**它做什么**以及**如何使用它**。
* ✅ 使用 `# Examples` 小节更好地解释**如何使用它**。
* ✅ 优先编写可以通过 `cargo test` 测试的示例，即使你必须用开头的 `#` 隐藏部分输出：
```rust
/// ```
/// let result = my_crate::add(2, 3);
/// # assert_eq!(result, 5);
/// ```
```
* ✅ 在相关时使用 `# Panics`、`# Errors` 和 `# Safety` 小节。
* 为类型添加相关上下文。

### `//!` 模块/Crate 级文档

当你想记录**模块或 crate 的用途**时使用 `//!`。它放在 `lib.rs` 或 `mod.rs` 文件的顶部，例如 `engine/mod.rs`：
```rust
//! This module implements a custom chess engine.
//!
//! It handles board state, move generation and check detection.
//!
//! # Example
//! ```
//! let board = chess::engine::Board::default();
//! assert!(board.is_valid());
//! ```
```

## 8.9 文档覆盖检查清单

📦 Crate 级（lib.rs）
- [ ] 顶部的 `//!` 文档解释了**这个 crate 做什么**，以及**它解决什么问题**。
- [ ] 包含 crate 级的 `# Examples` 或指向各模块的指引。

📁 模块（mod.rs 或内联）
- [ ] `//!` 文档解释了**这个模块是做什么的**、它的**导出项**以及**不变量（invariants）**。
- [ ] 除非需要澄清，否则避免在重新导出的条目上重复文档注释。

🧱 结构体、枚举、Trait
- `///` 文档应解释：
    - [ ] 这个类型扮演的角色。
    - [ ] 不变量或预期行为。
    - [ ] 构造或使用示例。
- [ ] 如果外部用户可能对其进行匹配，考虑使用 [`#[non_exhaustive]`](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute)。

🔧 函数和方法
- `///` 文档涵盖：
    - [ ] 它做什么。
    - [ ] 参数及其含义。
    - [ ] 返回值行为。
    - [ ] 边界情况（`# Panics`、`# Errors`）。
    - [ ] 用法示例，`# Examples`。

📑 Trait
- [ ] 解释 trait 的**用途**（标记用？动态分服用？）。
- [ ] 每个方法的文档——包括**何时/为何**要实现它。
- [ ] 清楚地记录默认实现的方法以及何时应覆盖它们。

📦 公共常量
- [ ] 记录它们配置什么，以及你什么时候会想用它们。

### 📌 最佳实践
* ✅ 慷慨地使用示例——它们同时充当测试用例。
* ✅ 清晰度优先于形式——这是给人看的，不是给机器看的。
* ✅ 优先用文档注释解释用法，如有必要，把实现细节留给代码注释。
* ✅ 经常使用 `cargo doc --open` 检查输出。
* ✅ 如果你想强制完整的文档覆盖，在顶层模块中添加 `#![deny(missing_docs)]` 和其他相关文档 lint。
