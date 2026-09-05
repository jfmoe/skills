# 第 1 章 - 编码风格与惯用法

## 1.1 借用优于克隆

Rust 的所有权系统鼓励**借用**（`&T`）而不是**克隆**（`T.clone()`）。
> ❗ 性能建议

### ✅ 何时使用 `Clone`：

* 你需要修改对象**并且**保留原始对象（不可变快照）。
* 当你持有 `Arc` 或 `Rc` 指针时。
* 当数据跨线程共享时，通常是 `Arc`。
* 避免对非性能关键代码进行大规模重构。
* 缓存结果时（下面是简单示例）：
```rust
fn get_config(&self) -> Config {
    self.cached_config.clone()
}
```
* 当底层 API 期望拥有所有权的数据时。

### 🚨 要避免的 `Clone` 陷阱：

* 在循环内自动克隆 `.map(|x| x.clone)`，应在迭代器末尾调用 `.cloned()` 或 `.copied()`。
* 克隆大型数据结构，如 `Vec<T>` 或 `HashMap<K, V>`。
* 因为糟糕的 API 设计而克隆，而不是调整生命周期。
* 优先使用 `&[T]` 而非 `Vec<T>` 或 `&Vec<T>`。
* 优先使用 `&str` 或 `&String` 而非 `String`。
* 优先使用 `&T` 而非 `T`。
* 克隆引用参数；如果你需要所有权，应在参数中明确让调用者传入。示例：
```rust
fn take_a_borrow(thing: &Thing) {
    let thing_cloned = thing.clone(); // the caller should have passed ownership instead
}
```

### ✅ 优先借用：
```rust
fn process(name: &str) {
    println!("Hello {name}");
}

let user = String::from("foo");
process(&user);
```

### ❌ 避免冗余克隆：
```rust
fn process_string(name: String) {
    println!("Hello {name}");
}

let user = String::from("foo");
process(user.clone()); // Unnecessary clone
```

## 1.2 何时按值传递？（`Copy` trait）

并非所有类型都应按引用（`&T`）传递。如果一个类型**很小**且**复制开销低**，通常**按值传递**更好。Rust 通过 `Copy` trait 使这一点显式化。

### ✅ 何时按值传递，`Copy`：
* 该类型**实现了** `Copy`（`u32`、`bool`、`f32`、小型结构体）。
* 移动该值的开销可以忽略不计。

```rust
fn increment(x: u32) -> u32 {
    x + 1
}

let num = 1;
let new_num = increment(num); // `num` still usable after this point
```

### ❓ 哪些结构体应该是 `Copy`？
* 在以下情况下考虑在你自己的类型上声明 `Copy`：
* 所有字段本身都是 `Copy`。
* 结构体**很小**，最多 2 个（也许 3 个）机器字长的内存或 24 字节（每个字长为 64 位/8 字节）。
* 结构体**表示"纯数据对象"**，不涉及资源所有权（没有堆分配。例如：`Vec` 和 `String`）。

❗**Rust 数组是在栈上分配的。** 这意味着如果其元素类型是 `Copy`，数组就可以被复制，但它会在程序栈上分配，很容易导致栈溢出。更多内容见 [Chapter 3 - Stack vs Heap](./chapter_03.md#33-stack-vs-heap-be-size-smart)

供参考，各基本类型的字节大小：

#### 整数：

| 类型 | 大小 |
|------------- |---------- |
| i8 u8 | 1 字节 |
| i16 u16 | 2 字节 |
| i32 u32 | 4 字节 |
| i64 u64 | 8 字节 |
| isize usize | 取决于架构 |
| i128 u128 | 16 字节 |

#### 浮点数：

| 类型 | 大小 |
|---------- |---------- |
| f32 | 4 字节 |
| f64 | 8 字节 |


#### 其他：

| 类型 | 大小 |
|---------- |---------- |
| bool | 1 字节 |
| char | 4 字节 |


### ✅ 适合派生 `Copy` 的结构体：
```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: f32,
    y: f32,
    z: f32
}
```

### ❌ 不适合派生 `Copy` 的结构体：
```rust
#[derive(Debug, Clone)]
struct BadIdea {
    age: i32,
    name: String, // String is not `Copy`
}
```

### ❓ 哪些枚举应该是 `Copy`？
* 如果你的枚举只是标签和原子值。
* 枚举的载荷全部是 `Copy`。
* **❗枚举的大小取决于其最大成员。**

### ✅ 适合派生的枚举
```rust
#[derive(Debug, Copy, Clone)]
enum Direction {
    North,
    South,
    East,
    West,
}
```

## 1.3 处理 `Option<T>` 和 `Result<T, E>`
Rust 1.65 引入了一种更好的方式，用 `let Some(x) = … else { … }` 或 `let Ok(x) = … else { … }` 安全地解包 Option 和 Result 类型，适用于你有默认 `return` 值、或默认 else 分支为 `continue`、`break` 的场景。当缺失的情况是**预期且正常**、而非异常时，它允许提前返回。

### ✅ 何时对 Option 和 Result 使用各种模式匹配
* 当你想对内部类型 `T` 和 `E` 做模式匹配时使用 `match`
```rust
match self {
    Ok(Direction::South) => { … },
    Ok(Direction::North) => { … },
    Ok(Direction::East) => { … },
    Ok(Direction::West) => { … },
    Err(E::One) => { … },
    Err(E::Two) => { … },
}

match self {
    Some(3|5) => { … }
    Some(x) if x > 10 => { … }
    Some(x) => { … }
    None => { … }
}
```

* 当你的类型被转换为更复杂的形式时使用 `match`，例如 `Result<T, E>` 变成 `Result<Option<T>, E>`。
```rust
match self {
    Ok(t) => Ok(Some(t)),
    Err(E::Empty) => Ok(None),
    Err(err) => Err(err),
}
```

* 当发散代码（diverging code）不需要了解失败的模式匹配，也不需要额外计算时，使用 `let PATTERN = EXPRESSION else { DIVERGING_CODE; }`：
```rust
let Some(&Direction::North) = self.direction.as_ref() else {
    return Err(DirectionNotAvailable(self.direction));
}
```

* 当你想跳出或继续模式匹配时，使用 `let PATTERN = EXPRESSION else { DIVERGING_CODE; }`
```rust
for x in self {
    let Some(x) = x else {
        continue;
    }
}
```

* 当 `DIVERGING_CODE` 需要额外计算时，使用 `if let PATTERN = EXPRESSION else { DIVERGING_CODE; }`：
```rust
if let Some(x) = self.next() {
    // computation
} else {
    // computation when `None/Err` or not matched
}
```

❗**如果你不关心 `Err` 分支的值，请使用 `?` 将 `Err` 传播给调用者。**

### ❌ 糟糕的 Option/Result 模式匹配：

* Result 与 Option 之间的转换（优先使用 `.ok()`、`.ok_or()` 和 `.ok_or_else()`）
```rust
match self {
    Ok(t) => Some(t),
    Err(_) => None
}
```

* 当发散代码只是默认值或预先计算的值时，使用 `if let PATTERN = EXPRESSION else { DIVERGING_CODE; }`（应优先使用 `let PATTERN = EXPRESSION else { DIVERGING_CODE; }`）：
```rust
if let Some(values) = self.next() {
    // computation
    (Some(..), values)
} else {
    (None, Vec::new())
}
```

* 在测试之外使用 `unwrap` 或 `expect`：
```rust
let port = config.port.unwrap();
```

## 1.4 防止过早分配

在处理 `or`、`map_or`、`unwrap_or`、`ok_or` 这类函数时，要考虑它们在需要内存分配时的特殊情况——比如创建新字符串、创建集合，甚至调用管理某些状态的函数——因此它们可以替换为对应的 `_else` 版本：

### ✅ 好的用法

```rust
let x = None;
assert_eq!(x.ok_or(ParseError::ValueAbsent), Err(ParseError::ValueAbsent));

let x = None;
assert_eq!(x.ok_or_else(|| ParseError::ValueAbsent(format!("this is a value {x}"))), Err(ParseError::ValueAbsent));


let x: Result<_, &str> = Ok("foo");
assert_eq!(x.map_or(42, |v| v.len()), 3);


let x : Result<_, String> = Ok("foo");
assert_eq!(x.map_or_else(|e|format!("Error: {e}"), |v| v.len()), 3);

let x = "1,2,3,4";
assert_eq!(x.parse_to_option_vec.unwrap_or_else(Vec::new), Ok(vec![1, 2, 3, 4]));
```

### ❌ 坏的用法

```rust
let x : Result<_, String> = Ok("foo");
assert_eq!(x.map_or(format!("Error with uninformed content"), |v| v.len()), 3);

let x = "1,2,3,4";
assert_eq!(x.parse_to_option_vec.unwrap_or(Vec::new()), Ok(vec![1, 2, 3, 4])); // could be replaced with `.unwrap_or_default`

let x = None;
assert_eq!(x.ok_or(ParseError::ValueAbsent(format!("this is a value {x}"))), Err(ParseError::ValueAbsent));
```

### 映射错误

处理 `Result::Err` 时，有时需要记录日志并将错误转换为更抽象或更详细的错误，这可以通过 `inspect_err` 和 `map_err` 完成：

```rust
let x = Err(ParseError::InvalidContent(...));

x
    .inspect_err(|err| tracing::error!("function_name: {err}"))
    .map_err(|err| GeneralError::from(("function_name", err)))?;
```

## 1.5 迭代器、`.iter` vs `for`

首先我们需要理解每种方式的基本循环。考虑以下问题：我们需要对 0 到 10 之间的所有偶数加 1 后求和：

* `for`：
```rust
let mut sum = 0;
for x in 0..=10 {
    if x % 2 == 0 {
        sum += x + 1;
    }
}
```

* `iter`：
```rust
let sum: i32 = (0..=10)
    .filter(|x| x % 2 == 0)
    .map(|x| x + 1)
    .sum();
```

> 两个版本做的事情相同，都正确且地道，但各自在不同场景下表现更好。

### 何时优先使用 `for` 循环
* 当你需要**提前退出**（`break`、`continue`、`return`）时。
* **带副作用的简单迭代**（例如日志、IO）
    * 日志也可以在迭代器中通过 `inspect` 和 `inspect_err` 函数正确完成。
* 当可读性比简洁性或链式调用更重要时。

#### 示例：
```rust
for value in &mut value {
    if *value == 0 {
        break;
    }
    *value += fancy_equation();
}
```

### 何时优先使用迭代器循环（`.iter()` 和 `.into_iter()`）
* 当你在`转换集合`或 `Option`/`Result` 时。
* 你可以**优雅地组合多个步骤**。
* 不需要提前退出。
* 你需要通过 `.enumerate` 支持带索引的值。
```rust
let values: Vec<_> = vec.into_iter()
    .enumerate()
    .filter(|(_index, value)| value % 2 == 0)
    .map(|(index, value)| value % index)
    .collect()
```
* 你需要使用集合函数，如 `.windows` 或 `chunks`。
* 你需要合并来自多个数据源的数据，且不想分配多个集合。
* 迭代器可以与 `for` 循环结合：
```rust
for value in vec.iter().enumerate()
    .filter(|(index, value)| value % index == 0) {
    // ...
}
```

> #### ❗记住：迭代器是惰性的
>
> * `.iter`、`.map`、`.filter` 在你调用消费器（如 `.collect`、`.sum`、`.for_each`）之前不做任何事。
> * **惰性求值**意味着迭代器链在编译时会被融合成一个循环。

### 🚨 要避免的反模式

* 不要不做格式化就链式调用。应让每个链式函数独占一行并正确缩进（`rustfmt` 会处理好这一点）。
* 如果链式调用让代码不可读，就不要链式调用。
* 避免不必要地收集/分配一个集合（例如 vector），随后又在更大的操作或另一次迭代中将其丢弃。
* 除非你需要集合的所有权，否则优先使用 `iter` 而非 `into_iter`。
* 对内部类型实现了 `Copy` 的集合（如 `Vec<i32>`），优先使用 `iter` 而非 `into_iter`。
* 数字求和时优先使用 `.sum` 而非 `.fold`。`.sum` 是专门为求和优化的，编译器知道可以在这一点上做优化，而 fold 有一个需要在每一步应用的黑盒闭包。如果你需要基于某个初始值求和，直接在表达式中加上即可：`let my_sum = [1, 2, 3].sum() + 3`。

## 1.6 注释：提供上下文，而非制造杂乱

> "注释是解释为什么（why），而不是什么（what）或如何（how）"

写得好的 Rust 代码，配合有表现力的类型和良好的命名，往往不言自明。许多高质量代码库依赖**很少或没有注释**也能蓬勃发展。这是件好事。

不过，仍然存在**仅靠代码不够的时刻**——当存在性能怪癖、外部约束或不明显的权衡，需要给读者一点提示时。在这些情况下，一条简洁的注释可以避免数小时的抓耳挠腮或翻找 git 历史。

### ✅ 好的注释

* 安全性考虑：
```rust
// SAFETY: We have checked that the pointer is valid and non-null. @Function xyz.
unsafe { std::ptr::copy_nonoverlapping(src, dst, len); }
```

* 性能怪癖：
```rust
// This algorithm is a fast square root approximation
const THREE_HALVES: f32 = 1.5;
fn q_rsqrt(number: f32 ) -> f32 {
    let mut i: i32 = number.to_bits() as i32;
    i = 0x5F375A86_i32.wrapping_sub(i >> 1);
    let y = f32::from_bits(i as u32);
    y * (THREE_HALVES - (number * 0.5 * y * y))
}
```

* 清晰的代码胜过注释。然而，当"为什么"不明显时，直截了当地说出来——或给出链接：
```rust
// PERF: Generating the root store per subgraph caused high TLS startup latency on MacOS
// This works as a caching alternative. See: [ADR-123](link/to/adr-123)
let subgraph_tls_root_store: RootCertStore = configuration
    .tls
    .subgraph
    .all
    .create_certificate_store()
    .transpose()?
    .unwrap_or_else(crate::services::http::HttpClientService::native_roots_store);
```

### ❌ 坏的注释

* 大段文字式的解释：冗长的注释和多行注释
```rust
// Lorem Ipsum is simply dummy text of the printing and typesetting industry.
// Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
// when an unknown printer took a galley
fn do_something_odd() {
    …
}
```
> 如果是在描述函数，优先使用 `/// doc` 文档注释。

* 本可以更好地用函数表达的注释，或者显而易见的注释
```rust
fn computation() {
    // increment i by 1
    i += 1;
}
```

### ✅ 拆分长函数，而不是给它们写注释

如果你发现自己在写一段长注释来解释函数中的"是什么"、"怎么做"或"每一步"，那可能是时候拆分了。建议是重构。这不仅有利于可读性，也有利于可测试性：

#### ❌ 不要这样：
```rust
fn process_request(request: T) {
    // We first need to validate request, because of corner case x, y, z
    // As the payload can only be decoded when they are valid
    // Then we can perform authorization on the payload
    // lastly with the authorized payload we can dispatch to handler
}
```

#### ✅ 推荐这样
```rust
fn process_request(request: T) -> Result<(), Error> {
    validate_request_headers(&request)?;
    let payload = decode_payload(&request);
    authorize(&payload)?;
    dispatch_to_handler(payload)
}

#[cfg(test)]
mod tests {
    #[test]
    fn validate_request_happy_path() { ... }

    #[test]
    fn validate_request_fails_on_x() { ... }

    #[test]
    fn validate_request_fails_on_y() { ... }

    #[test]
    fn decode_validated_request() { ... }

    #[test]
    fn authorize_payload_xyz() { ... }
}
```

让**结构**和**命名**取代解说，并用**测试作为活文档**来增强文档。

### 📝 TODO 不是注释——要正确跟踪它们

避免在代码中留下悬而未决的 `// TODO: Lorem Ipsum` 注释。取而代之：
* 把它们变成 Jira 或 GitHub Issues。
* 如有需要，为避免日后困惑，在代码中引用 issue，并在 issue 中引用代码。

```rust
// See issue #123: support hyper 2.0
```

这有助于保持代码整洁，并确保任务不会被遗忘。

### 注释作为活文档

把注释称为"活文档"时有几个坑：
* 代码会演进。
* 上下文会变化。
* 注释会过时。
* 太多长注释会让人们不愿去读。
* 团队会不敢删除无关的注释。

如果你发现一条注释，**不要盲目相信它**。结合上下文阅读。如果它是错的或过时的，修复或删除它。一条误导性的注释比没有注释更糟糕。

> 注释应该让你不安——它们像过时的测试一样，要求反复验证。

当需要更深入的论证时，优先：
* **链接到设计文档或 ADR**——业务逻辑适合放在设计文档中，性能权衡适合放在 ADR 中。
* 把运行时示例和用法文档移到 Rust 文档中，即 `/// doc comment`，这样它们可以被 `cargo doc` 等工具测试并保持更新。

> 文档注释与文档测试，`///` 和 `//!`，见 [Chapter 8 - Comments vs Documentation](./chapter_08.md)

## 1.7 use 声明——"导入"

不同语言对导入排序有不同方式，在 Rust 生态中，[标准方式](https://github.com/rust-lang/rustfmt/issues/4107)是：

- `std`（`core`、`alloc` 也归在此类）。
- 外部 crate（你的 Cargo.toml `[dependencies]` 中的内容）。
- 工作区 crate（工作区成员 crate）。
- 本模块的 `super::`。
- 本模块的 `crate::`。

```rust
// std
use std::sync::Arc;

// external crates
use chrono::Utc;
use juniper::{FieldError, FieldResult};
use uuid::Uuid;

// crate code lives in workspace
use broker::database::PooledConnection;

// super:: / crate::
use super::schema::{Context, Payload};
use super::update::convert_publish_payload;
use crate::models::Event;
```

一些企业解决方案选择把自己的核心包放在 `std` 之后，这样所有以企业名开头的外部包都位于其他包之前：

```rust
// std
use std::sync::Arc;

// enterprise external crates
use enterprise_crate_name::some_module::SomeThing;

// external crates
use chrono::Utc;
use juniper::{FieldError, FieldResult};
use uuid::Uuid;

// crate code lives in workspace
use broker::database::PooledConnection;

// super:: / crate::
use super::schema::{Context, Payload};
use super::update::convert_publish_payload;
use crate::models::Event;
```

一种不必手动控制导入排序的方法是在你的 `rustfmt.toml` 中使用以下参数：

```toml
reorder_imports = true
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

> 截至 Rust 1.88 版本，需要在 nightly 下执行 rustfmt 才能正确地重新排序代码：`cargo +nightly fmt`。
