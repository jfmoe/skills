# 第 5 章 - 自动化测试

> 测试不仅仅是为了正确性。它们是人们理解你的代码如何工作时最先去看的地方。

* Rust 中的测试用属性宏 `#[test]` 声明。大多数代码编辑器可以单独编译和运行该宏下声明的函数，或成块运行。
* 测试可以通过 `#[cfg(test)]` 拥有特殊的编译标志。如果其中包含 `#[test]`，也可以在代码编辑器中执行；这是 mock 复杂函数或覆盖 trait 的好方式。

## 5.1 测试作为活文档

在 Rust 中（和许多其他语言一样），测试常常展示函数的预期用法。如果测试清晰且有针对性，它往往比阅读函数体更有帮助；与其他测试结合时，它们就构成了活文档。

### 使用有描述性的名称

> 在单元测试名称中，我们应该看到以下内容：
> * `unit_of_work`：我们调用的*函数*，即将执行的**动作**。这通常就是被测函数所在测试 `mod` 的名字。
```rust
#[cfg(test)]
mod test {
    mod function_name {
        #[test]
        fn returns_y_when_x() { ... }
    }
}
```
> * `expected_behavior`：验证测试有效所需的一组**断言**。
> * `state_that_the_test_will_check`：该特定测试用例的总体**准备**（arrangement）或设置（setup）。

#### ❌ 不要给测试用泛化的名字
```rust
#[test]
fn test_add_happy_path() {
    assert_eq!(add(2, 2), 4);
}
```
#### ✅ 使用读起来像句子、能描述期望行为的名称
> 另外，如果你的函数有太多测试，可以把它们归拢到一个 `mod` 里，这样更易于阅读和导航。

```rust
// OPTION 1
#[test]
fn process_should_return_blob_when_larger_than_b() {
    let a = setup_a_to_be_xyz();
    let b = Some(2);
    let expected = MyExpectedStruct { ... };

    let result = process(a, b).unwrap();

    assert_eq!(result, expected);
}

// OPTION 2
mod process {
    #[test]
    fn should_return_blob_when_larger_than_b() {
        let a = setup_a_to_be_xyz();
        let b = Some(2);
        let expected = MyExpectedStruct { ... };

        let result = process(a, b).unwrap();

        assert_eq!(result, expected);
    }
}
```

> 执行 `cargo test` 时，两种方式的测试输出分别是：
> 方式 1：`process_should_return_blob_when_larger_than_b`。
> 方式 2：`process::should_return_blob_when_larger_than_b`。

### 使用模块来组织

大多数 IDE 可以整体运行单个测试模块。
输出中的测试名称也会包含模块名。
合起来看，这意味着你可以用模块名把相关测试分组：

```rust
#[cfg(test)]
mod test { // IDEs will provide a ▶️ button here

    mod process {
        #[test] // IDEs will provide a ▶️ button here
        fn returns_error_xyz_when_b_is_negative() {
            let a = setup_a_to_be_xyz();
            let b = Some(-5);
            let expected = MyError::Xyz;

            let result = process(a, b).unwrap_err();

            assert_eq!(result, expected);
        }

        #[test] // IDEs will provide a ▶️ button here
        fn returns_invalid_input_error_when_a_and_b_not_present() {
            let a = None;
            let b = None;
            let expected = MyError::InvalidInput;

            let result = process(a, b).unwrap_err();

            assert_eq!(result, expected);
        }
    }
}
```

### 每个函数只测试一个行为

为了保持测试清晰，它们应该只描述被测单元做的_一件_事。
这样更容易理解测试为什么失败。

#### ❌ 不要在同一个测试中测多件事
```rust
fn test_thing_parser(...) {
    assert!(Thing::parse("abcd").is_ok());
    assert!(Thing::parse("ABCD").is_err());
}
```

#### ✅ 每个测试只测一件事
```rust
#[cfg(test)]
mod test_thing_parser {
    #[test]
    fn lowercase_letters_are_valid() {
        assert!(
            Thing::parse("abcd").is_ok(),
            // Works like `eprintln`, `format` and `println` macros
            "Thing parse error: {:?}",
            Thing::parse("abcd").unwrap_err()
        );
    }

    #[test]
    fn capital_letters_are_invalid() {
        assert!(Thing::parse("ABCD").is_err());
    }
}
```

> `Ok` 场景应该把 `Err` 情况通过 `eprintln` 打印出来。

### 每个测试使用很少——理想情况下一个——断言

当一个测试中有多个断言时，既更难理解预期行为，也常常需要多轮迭代才能修复失败的测试，因为你得逐个排查断言。

❌ 不要在一个测试中放很多断言：

```rust
#[test]
fn test_valid_inputs() {
    assert!(the_function("a").is_ok());
    assert!(the_function("ab").is_ok());
    assert!(the_function("ba").is_ok());
    assert!(the_function("bab").is_ok());
}
```

如果你在测试不同的行为，就拆成多个测试，各自使用有描述性的名字。
为避免样板代码，可以使用共享的 setup 函数，或使用 *带描述性测试名*的 [rstest](https://crates.io/crates/rstest) 用例：
```rust
#[rstest]
#[case::single("a")]
#[case::first_letter("ab")]
#[case::last_letter("ba")]
#[case::in_the_middle("bab")]
fn the_function_accepts_all_strings_with_a(#[case] input: &str) {
    assert!(the_function(input).is_ok());
}
```

> 使用 `rstest` 的注意事项
>
> * IDE 和人类都更难运行/定位特定测试。
> * 期望值与条件的命名在视觉上反转了（期望在前）。

## 5.2 在文档中添加测试示例

文档部分我们会在后面深入讨论，本节只简要介绍如何在文档中添加测试。Rustdoc 可以用 `///` 把示例变成可执行的测试，有以下几个优点：

* 这些测试会随 `cargo test` 一起运行，**但不会**随 `cargo nextest run` 运行。如果使用 `nextest`，请确保单独运行 `cargo t --doc`。
* 它们既是文档又是正确性检查，并且由于编译器会检查它们，能随代码变更保持更新。
* 无需额外的测试样板。你可以通过在行首加 `#` 轻松隐藏测试片段。
* ❗ 文档测试与其他非面向公众的测试之间存在重复没有问题。

```rust
/// Helper function that adds any two numeric values together.
/// This function reasons about which would be the correct type to parse based on the type
/// and the size of the numeric value.
///
/// # Examples
///
/// ```rust
/// # use crate_name::generic_add;
/// use num::numeric;
///
/// # assert_eq!(
/// generic_add(5.2, 4) // => 9.2
/// # , 9.2)
///
/// # assert_eq!(
/// generic_add(2, 2.0) // => 4
/// # , 4)
/// ```
```

这段文档代码看起来会是：
```rust
use num::numeric;

generic_add(5.2, 4) // => 9.2
generic_add(2, 2.0) // => 4
```

## 5.3 单元测试 vs 集成测试 vs 文档测试

一般来说，不深入*测试金字塔的命名之争*，Rust 有 3 类测试：

### 单元测试

与**被测单元**声明在**同一个模块**中的测试。这让测试运行器可以访问私有函数和父级的 `use` 声明。如有需要，它们也可以调用其他模块的 `pub(crate)` 函数。单元测试可以更专注于**实现和边界情况检查**。

* 它们应该尽可能简单，测试单元的一个状态和一个行为。KISS 原则。
* 它们应该测试错误和边界情况。
* 同一单元的不同测试可以合并在一个 `#[cfg(test)] mod test_unit_of_work {...}` 下，允许为不同的 `unit_of_work` 使用多个子模块。
* 尽量把 API 的外部状态/副作用降到最低，并将这类测试集中在 `mod.rs` 文件中。
* 尚未完全实现的测试可以用 `#[ignore = "optional message"]` 属性忽略。
* 故意 panic 的测试应该用 `#[should_panic]` 属性标注。

```rust
#[cfg(test)]
mod unit_of_work_tests {
    use super::*;

    #[test]
    fn unit_state_behavior() {
        let expected = ...;
        let result = ...;
        assert_eq!(result, expected, "Failed because {}", result - expected);
    }
}
```

### 集成测试

放在 `tests/` 目录下的测试。它们完全位于你的库外部，使用与任何其他代码相同的调用方式，无法访问私有和 crate 级函数，这意味着它们**只能测试**你**公共 API** 上的函数。

> 它们的目的是测试代码的多个部分能否正确地协同工作——单独运行正确的代码单元，集成起来可能有问题。

* 测试正常路径和常见用例。
* 允许外部状态和副作用，[testcontainers](https://rust.testcontainers.org/) 可能有帮助。
* 如果测试二进制程序，尽量把**可执行入口**和**函数**分别拆到 `src/main.rs` 和 `src/lib.rs`。

```
├── Cargo.lock
├── Cargo.toml
├── src
│   └── lib.rs
└── tests
    ├── mod.rs
    ├── common
    │   └── mod.rs
    └── integration_test.rs
```

### 文档测试

如 [5.2](#52-add-test-examples-to-your-docs) 节所述，文档测试应包含正常路径、公共 API 的一般用法，以及能增强文档的更强大属性，比如代码块的自定义 CSS。

### 属性：

* `ignore`：告诉 Rust 忽略这段代码。通常不推荐——如果你只想要格式化的代码文本，用 `text`。
* `should_panic`：告诉 Rust 编译器这个示例块会 panic。
* `no_run`：编译但不执行代码，类似 `cargo check`。处理文档中的副作用时非常有用。
* `compile_fail`：测试 rustdoc，表示这个代码块应该编译失败。当你想演示错误用法时很重要。

## 5.4 如何使用 `assert!`

Rust 自带 2 个断言宏：
* `assert!` 用于断言布尔值，如 `assert!(value.is_ok(), "'value' is not Ok: {value:?}")`
* `assert_eq!` 用于检查两个不同值之间的相等性，`assert_eq!(result, expected, "'result' differs from 'expected': {}", result.diff(expected))`。

### 🚨 `assert!` 提醒
* Rust 的断言支持格式化字符串，如前面的示例所示。这些字符串会在失败时打印，因此最好写出实际状态是什么、与期望有何不同。
* 如果你不关心模式匹配的具体值，将 `matches!` 与 `assert!` 结合可能是不错的替代方案。
```rust
assert!(matches!(error, MyError::BadInput(_), "Expected `BadInput`, found {error}"));
```
* 明智地使用 `#[should_panic]`。只有当 panic 是期望行为时才应使用它；优先返回 result 而非 panic。
* 还有一些可以增强测试体验的 crate：
    * [`rstest`](https://crates.io/crates/rstest)：基于 fixture 的测试框架，带过程宏。
    * [`pretty_assertions`](https://crates.io/crates/pretty_assertions)：覆盖 `assert_eq` 和 `assert_ne`，生成彩色 diff。

## 5.5 使用 `cargo insta` 进行快照测试

> 当正确性体现在视觉或结构上时，快照比断言更能说明问题。

1. 添加到你的依赖：
```toml
insta = { version = "1.42.2", features = ["yaml"] }
```
> 对于大多数真实世界的应用，建议对可序列化的值使用 YAML 快照。因为它们在版本控制和 diff 查看器中效果最好，并且支持数据脱敏（redaction）。要使用它，启用 insta 的 yaml feature。

2. 为了获得更好的审查体验，安装 CLI：`cargo install cargo-insta`。

3. 编写一个简单的测试：
```rust
fn split_words(s: &str) -> Vec<&str> {
    s.split_whitespace().collect()
}

#[test]
fn test_split_words() {
    let words = split_words("hello from the other side");
    insta::assert_yaml_snapshot!(words);
}
```

4. 运行 `cargo insta test` 执行测试，运行 `cargo insta review` 审查冲突。

想了解更多关于 `cargo insta` 的信息，请查看它的[文档](https://insta.rs/docs/quickstart/)——它是一个非常完整且文档齐全的工具。

### 什么是快照测试？

快照测试将你的输出（文本、JSON、HTML、YAML 等）与保存的"黄金"版本进行比较。在未来的运行中，除非经人工批准，否则输出一旦变化测试就会失败。它非常适合：
* 生成的代码。
* 复杂数据的序列化。
* 渲染后的 HTML。
* CLI 输出。

#### ❌ 不适合用快照测试的场景
* 非常稳定、纯数值或与少量结构化数据相关的逻辑（优先使用 `assert_eq!`）。
* 关键路径逻辑（优先使用精确的单元测试）。
* 不稳定的测试、随机生成的输出，除非做了脱敏处理。
* 外部资源的快照——使用 mock 和 stub。

## 5.6 ✅ 快照最佳实践

* 使用命名快照，让快照文件名有意义，例如 `snapshots/this_is_a_named_snapshot.snap`
```rust
assert_snapshot!("this_is_a_named_snapshot", output);
```

* 保持快照小而清晰。
```rust
// ✅ Best case:
assert_snapshot!("app_config/http", whole_app_config.http);

// ❌ Worst case:
assert_snapshot!("app_config", whole_app_config); // Huge object
```

> #### 🚨 避免对巨大对象做快照
> 巨大对象难以审查和推理。

* 避免对简单类型做快照（基本类型、扁平枚举、小结构体）：
```rust
// ✅ Better:
assert_eq!(meaning_of_life, 42);

// ❌ OVERKILL:
assert_snapshot!("the_meaning_of_life", meaning_of_life); // meaning_of_life == 42
```

* 对不稳定字段（随机生成、时间戳、uuid 等）使用[脱敏（redaction）](https://insta.rs/docs/redactions/)：
```rust
use insta::assert_json_snapshot;

#[test]
fn endpoint_get_user_data() {
    let data = http::client.get_user_data();
    assert_json_snapshot!(
        "endpoints/subroute/get_user_data",
        data,
        ".created_at" => "[timestamp]",
        ".id" => "[uuid]"
    );
}
```
* 把快照提交到 git。它们会存储在测试旁边的 `snapshots/` 目录中。
* 在接受变更前仔细审查。
