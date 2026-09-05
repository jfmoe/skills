# 第 4 章 - 错误处理

Rust 强制执行严格的错误处理方式，但你*如何*处理错误，决定了你的代码是符合人体工学、一致且安全，还是晦涩而痛苦。本章深入探讨在库和二进制程序中建模和管理可能失败操作的最佳实践。

> 即使你决定用 `unwrap` 或 `expect` 让应用崩溃，Rust 也迫使你明确地声明这一意图。

## 4.1 优先使用 `Result`，避免 panic 🫨

Rust 有一个强大的类型用于包装可能失败的数据：[`Result<T, E>`](https://doc.rust-lang.org/std/result/)。它允许我们根据需要处理错误情况，并基于此管理应用的状态。

* 如果你的函数可能失败，优先返回 `Result`：
```rust
fn divide(x: f64, y: f64) -> Result<f64, DivisionError> {
    if y == 0.0 {
        Err(DivisionError::DividedByZero)
    } else {
        Ok(x / y)
    }
}
```

* 仅在不可恢复的情况下使用 `panic!`——通常是测试、断言、bug，或出于某种明确原因需要让应用崩溃。
* 有 3 个相关宏可以在适当条件下替代 `panic!`：
    * `todo!`：类似 panic，但会告知编译器你已意识到这里有代码缺失。
    * `unreachable!`：你已经对代码块做过推理，确信条件 `xyz` 不可能发生，并且如果它真的变得可能发生，你希望收到告警。
    * `unimplemented!`：特别适用于提示某个代码块尚未实现，并附上原因。

## 4.2 在生产代码中避免 `unwrap`/`expect`

虽然 `expect` 优于 `unwrap`（因为它可以携带上下文），但在生产代码中都应避免使用，因为存在更聪明的替代方案。基于此，它们应仅用于以下场景：
- 测试、断言或测试辅助函数中。
- 失败不可能发生时。
- 更聪明的选项无法处理特定情况时。

### 🚨 处理 `unwrap`/`expect` 的替代方式：

* 如果你的 `Result`（或 `Option`）在 `Result::Err` 情况下可以有一个预定义的提前返回值，且不需要知道 `Err` 的值，使用 `let Ok(..) = else { return ... }` 模式，它有助于把函数拍平：
```rust
let Ok(json) = serde_json::from_str(&input) else {
    return Err(MyError::InvalidJson);
}
```
* 如果你的 `Result`（或 `Option`）在 `Result::Err` 情况下需要错误恢复，且不需要知道 `Err` 的值，使用 `if let Ok(..) else { ... }` 模式：
```rust
if let Ok(json) = serde_json::from_str(&input) else {
    ...
} else {
    Err(do_something_with_input(&input))
}
```
* 需要处理 `Option::None` 值的函数，建议返回 `Result<T, E>`，其中 `E` 是 crate 级或模块级错误，如上面的示例所示。
* 最后是 `unwrap_or`、`unwrap_or_else` 或 `unwrap_or_default`：这些函数帮助你为 unwrap 创建管理未初始化值的替代出口。

## 4.3 使用 `thiserror` 处理 crate 级错误

手动派生 Error 既冗长又容易出错，Rust 生态有一个非常好的 crate 可以帮助解决这个问题：`thiserror`。它允许你创建轻松实现 `From` trait 以及错误消息（`Display`）的错误类型，改善开发体验，同时与 `?` 无缝配合并集成 `std::error::Error`：

```rust
#[derive(Debug, thiserror::Error)]
pub enum MyError {
    #[error("Network Timeout")]
    Timeout,
    #[error("Invalid data: {0}")]
    InvalidData(String),
    #[error(transparent)]
    Serialization(#[from] serde_json::Error),
    #[error("Invalid request information. Header: {headers}, Metadata: {metadata}")]
    InvalidRequest {
        headers: Headers,
        metadata: Metadata
    }
}
```

### 错误层级与包装

对于分层系统，最佳实践是使用带 `#[from]` 的嵌套 `enum/struct` 错误：

```rust
use crate::database::DbError;
use crate::external_services::ExternalHttpError;

#[derive(Debug, thiserror::Error)]
pub enum ServiceError {
    #[error("Database handler error: {0}")]
    Db(#[from] DbError),
    #[error("External services error: {0}")]
    ExternalServices(#[from] ExternalHttpError)
}
```

## 4.4 把 `anyhow` 留给二进制程序

`anyhow` 是一个很棒的 crate，对于刚起步、需要快速推进的项目非常有用。然而存在一个转折点，过了那个点它就会痛苦地蔓延到你的整个代码中。鉴于此，`anyhow` 建议只用于**二进制程序**——那里需要符合人体工学的错误处理，且不需要精确的错误类型：

```rust
use anyhow::{Context, Result, anyhow};

fn main() -> Result<()> {
    let content = std::fs::read_to_string("config.json")
        .context("Failed to read config file")?;
    Config::from_str(&content)
        .map_err(|err| anyhow!("Config parsing error: {err}"))
}
```

### 🚨 `Anyhow` 的坑

* 在整个代码库中保持 `context` 和 `anyhow` 字符串的更新，比保持 `thiserror` 消息更新更难，因为你没有单一入口。
* `anyhow::Result` 会抹去调用者可能需要的上下文，因此避免在库中使用它。
* 测试辅助函数使用 `anyhow` 几乎没有问题。

## 4.5 使用 `?` 让错误向上冒泡

优先使用 `?`，而非 `match` 链等冗长替代方案：
```rust
fn handle_request(req: &Request) -> Result<ValidatedRequest, MyError> {
    validate_headers(req)?;
    validate_body_format(req)?;
    validate_credentials(req)?;
    let body = Body::try_from(req)?;

    Ok(ValidatedRequest::try_from((req, body))?)
}
```

> 如果需要错误恢复，使用 `or_else`、`map_err`、`if let Ok(..) else`。要**检查或记录错误**，使用 `inspect_err`。

## 4.6 单元测试应该覆盖错误

虽然许多错误没有实现 PartialEq 和 Eq，使得直接对它们做断言很困难，但可以用 `format!` 或 `to_string()` 检查错误消息，让错误有意义且经过测试验证：

```rust
#[test]
fn error_does_not_implement_partial_eq() {
    let err = divide(10., 0.0).unwrap_err();
    assert_eq!(err.to_string(), "division by zero");
}

#[test]
fn error_implements_partial_eq() {
    let err = process(my_value).unwrap_err();

    assert_eq!(
        err,
        MyError {
            ..
        }
    )
}
```

## 4.7 重要主题

### 自定义错误结构体

有时你不需要用枚举来处理错误，因为你的模块只有一种类型的错误。这可以用 `struct Errors` 解决：

```rust
#[derive(Debug, thiserror::Error, PartialEq)]
#[error("Request failed with code `{code}`: {message}")]
struct HttpError {
    code: u16,
    message: String
}
```

### 异步错误

使用 Tokio 等异步运行时，确保你的错误在需要的地方实现 `Send + Sync + 'static`，特别是在任务中或跨越 `.await` 边界时：

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    ...
    Ok(())
}
```

> 在库中避免使用 `Box<dyn std::error::Error>`，除非确实需要。
