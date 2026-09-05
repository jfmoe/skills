# 第 2 章 - Clippy 与 Lint 规范

确保你的 Rust 编译器已安装 `cargo clippy`，在 Rust 项目目录的终端中运行 `cargo clippy -V`，你应该会看到类似 `clippy 0.1.86 (05f9846f89 2025-03-31)` 的输出。如果终端无法显示 clippy 版本，请运行以下命令：`rustup update && rustup component add clippy`。

Clippy 文档可以在[这里](https://doc.rust-lang.org/clippy/usage.html)找到。

## 2.1 为什么要关心 lint？

Rust 编译器是一个能捕获许多错误的强大工具。然而，一些更深入的分析需要额外的工具，这就是 `cargo clippy` 发挥作用的地方。Clippy 检查：
* 性能陷阱。
* 风格问题。
* 冗余代码。
* 潜在 bug。
* 不地道的 Rust 写法。

## 2.2 始终运行 `cargo clippy`

将以下内容加入你的日常工作流：

```shell
$ cargo clippy --all-targets --all-features --locked -- -D warnings
```

* `--all-targets`：检查库、测试、基准测试和示例。
* `--all-features`：在启用所有 feature 的情况下检查代码，自动解决 feature 冲突。
* `--locked`：要求 `Cargo.lock` 是最新的，可通过 `$ cargo update` 解决。
* `-D warnings`：将警告视为错误。

可以考虑添加的参数：

* `-- -W clippy::pedantic`：相当严格或偶有误报的 lint。
* `-- -W clippy::nursery`：可选添加，用于检查仍在开发中的新 lint。
* ❗ 把它加入你的 Makefile、Justfile、xtask 或 CI 流水线。

> ApolloGraphQL 的示例
>
> 在 `Router` 项目中配置了一个用于 lint 的 `xtask`，可以通过 `cargo xtask lint` 执行。

## 2.3 需要重视的重要 Clippy Lint

| Lint 名称 | 原因 | 链接 |
| --------- | ----| -----|
| `redundant_clone` | 检测不必要的 `clone`，有性能影响 | [link (nursery + perf)](https://rust-lang.github.io/rust-clippy/master/#redundant_clone) |
| `needless_borrow` 组 | 移除冗余的 `&` 借用 | [link (style)](https://rust-lang.github.io/rust-clippy/master/#needless_borrow) |
| `map_unwrap_or` / `map_or` | 简化嵌套的 `Option/Result` 处理 | [`map_unwrap_or`](https://rust-lang.github.io/rust-clippy/master/#map_unwrap_or) [`unnecessary_map_or`](https://rust-lang.github.io/rust-clippy/master/#unnecessary_map_or) [`unnecessary_result_map_or_else`](https://rust-lang.github.io/rust-clippy/master/#unnecessary_result_map_or_else) |
| `manual_ok_or` | 建议使用 `.ok_or_else` 而非 `match` | [link (style)](https://rust-lang.github.io/rust-clippy/master/#manual_ok_or) |
| `large_enum_variant` | 当枚举有很大的变体（对内存不利）时发出警告，建议将其装箱（`Box`） | [link (perf)](https://rust-lang.github.io/rust-clippy/master/#large_enum_variant) |
| `unnecessary_wraps` | 如果你的函数总是返回 `Some` 或 `Ok`，你就不需要 `Option`/`Result` | [link (pedantic)](https://rust-lang.github.io/rust-clippy/master/#unnecessary_wraps) |
| `clone_on_copy` | 捕获对 `Copy` 类型（如 `u32` 和 `bool`）意外调用 `.clone()` 的情况 | [link (complexity)](https://rust-lang.github.io/rust-clippy/master/#clone_on_copy) |
| `needless_collect` | 防止在不需要分配时对迭代器进行收集和分配 | [link (nursery)](https://rust-lang.github.io/rust-clippy/master/#needless_collect) |

## 2.4 修复警告，不要压制它们！

**永远不要**只是 `#[allow(clippy::lint_something)]`，除非：

* 你**真正理解**警告发生的原因，并且有理由说明这样做更好。
* 你**记录**了忽略它的原因。
* ❗ 不要使用 `allow`，而要用 `expect`——如果 lint 不再成立，它会给出警告：`#[expect(clippy::lint_something)]`。

### 示例：

```rust
// Faster matching is preferred over size efficiency
#[expect(clippy::large_enum_variant)]
enum Message {
    Code(u8),
    Content([u8; 1024]),
}
```

> 修复方式是：
>
> ```rust
> // Faster matching is preferred over size efficiency
> #[expect(clippy::large_enum_variant)]
> enum Message {
>     Code(u8),
>     Content(Box<[u8; 1024]>),
> }
> ```

### 处理误报

有时即使你的代码是正确的，Clippy 也会报错。在这些情况下有两种解决方案：
1. 尝试重构代码，从而消除警告。
2. 使用 `#[expect(clippy::lint_name)]` 在**局部**覆盖该 lint，并附上说明原因的注释。
3. 避免全局覆盖，除非这是核心 crate 的问题。一个很好的例子是 Bevy 引擎，它有一组默认应被允许的 lint。

## 2.5 配置工作区/包的 lint

在你的 `Cargo.toml` 文件中，可以指定哪些 lint 生效以及它们之间的优先级。当两个或更多 lint 冲突时，优先级更高的会被采用。包的示例配置：

```toml
[lints.rust]
future-incompatible = "warn"
nonstandard_style = "deny"

[lints.clippy]
all = { level = "deny", priority = 10 }
redundant_clone = { level = "deny", priority = 9 }
manual_while_let_some = { level = "deny", priority = 4 }
pedantic = { level = "warn", priority = 3 }
```

工作区的配置：

```toml
[workspace.lints.rust]
future-incompatible = "warn"
nonstandard_style = "deny"

[workspace.lints.clippy]
all = { level = "deny", priority = 10 }
redundant_clone = { level = "deny", priority = 9 }
manual_while_let_some = { level = "deny", priority = 4 }
pedantic = { level = "warn", priority = 3 }
```
