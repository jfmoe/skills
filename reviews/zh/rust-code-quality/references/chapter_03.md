# 第 3 章 - 性能思维

性能工作的**黄金法则**：

> 不要猜测，要测量。

Rust 代码通常已经相当快——不要在没有证据的情况下"优化"。只在找到瓶颈之后才优化。

### 良好的第一步
* 构建时使用 `--release` 标志（听起来很基础，但经常听到有人抱怨他们的 Rust 代码比 X 语言的代码慢，而 99% 的情况是因为他们没有使用 `--release` 标志）。
* `$ cargo clippy -- -D clippy::perf` 会给你关于性能最佳实践的重要提示。
* [`cargo bench`](https://doc.rust-lang.org/cargo/commands/cargo-bench.html) 是一个用于创建微基准测试并测试不同代码方案的 cargo 工具。编写一个测试场景，将你的方案与原代码做基准对比，如果你的改进超过 5%，可能就是一个不错的性能提升。
* [`cargo flamegraph`](https://github.com/flamegraph-rs/flamegraph) 是一个强大的 Rust 代码分析器。对于 macOS，[samply](https://github.com/mstange/samply) 可能是开发体验更好的选择。

> #### 关于基准测试的延伸阅读：
> - [How to build a Custom Benchmarking Harness in Rust](https://bencher.dev/learn/benchmarking/rust/custom-harness/)


## 3.1 火焰图（Flamegraph）

火焰图帮助你可视化 CPU 在每个任务上花费了多少时间。

```shell
# Installing flamegraph
cargo install flamegraph

# cargo support provided through the cargo-flamegraph binary!
# defaults to profiling cargo run --release
cargo flamegraph

# by default, `--release` profile is used,
# but you can override this:
cargo flamegraph --dev

# if you'd like to profile a specific binary:
cargo flamegraph --bin=stress2

# Profile unit tests.
# Note that a separating `--` is necessary if `--unit-test` is the last flag.
cargo flamegraph --unit-test -- test::in::package::with::single::crate
cargo flamegraph --unit-test crate_name -- test::in::package::with::multiple:crate

# Profile integration tests.
cargo flamegraph --test test_name

# Run criterion benchmark
# Note that the last --bench is required for `criterion 0.3` to run in benchmark mode, instead of test mode.
cargo flamegraph --bench some_benchmark --features some_features -- --bench

# Run workspace example
cargo flamegraph --example some_example --features some_features
```

> ❗ 始终在启用 `--release` 的情况下运行性能分析，`--dev` 标志不真实，因为它没有启用优化。

结果看起来像一个火焰图，其中：

* `y 轴`显示**栈深度**。看火焰图时，程序的 main 函数会靠近底部，被调用的函数堆叠在其上方，它们调用的函数再堆叠在更上方。

* `每个方块的宽度`显示**该函数**在 CPU 上或作为调用栈一部分的**总时间**。如果一个函数的方块比其他方块宽，说明它每次执行消耗的 CPU 比其他函数多，或者它被调用的次数比其他函数多。

> ❗ **每个方块的颜色**没有意义，是**随机选择**的。

### 🚨 记住
* 粗栈：CPU 使用量大
* 细栈：强度低（开销小）

## 3.2 避免冗余克隆

> 克隆很便宜……**直到它不再便宜**

在 [Borrowing over Cloning](./chapter_01.md#11-borrowing-over-cloning) 和 [Important Clippy lints to respect](./chapter_02.md#23-important-clippy-lints-to-respect) 小节中，我们提到了克隆的影响以及相关的 clippy lint [`redundant_clone`](https://rust-lang.github.io/rust-clippy/master/#redundant_clone)，因此本节将探讨一下"何时传递所有权"。

* 🚨 如果你真的需要克隆，把它留到最后一刻。

### 何时传递所有权？

* 只有当你确实需要一个新的拥有所有权的副本时才 `.clone()`。一些例子：
    * Crate API 设计要求拥有所有权的数据。
    * 重载了 `std::ops`，但仍需要旧数据的所有权：
    ```rust
    use std::ops::Add;

    #[derive(Debug, Copy, Clone, PartialEq)]
    struct Point {
        x: i32,
        y: i32,
    }

    impl Add for Point {
        type Output = Self;

        fn add(self, other: Self) -> Self {
            Self {
                x: self.x + other.x,
                y: self.y + other.y,
            }
        }
    }

    assert_eq!(Point { x: 1, y: 0 } + Point { x: 2, y: 3 },
               Point { x: 3, y: 3 });
    ```
    * 需要做对比快照，或由于 API 的原因你需要数据的多个拥有所有权的实例。
    ```rust
    fn snapshot(a: &MyValue, b:&MyValue) -> MyValueDiff {
        a - b
    }

    impl Sub for MyValue {
        type Output = MyValueDiff;

        fn sub(self, other: Self) -> MyValue {
            ...
        }
    }

    fn main() {
        let mut a = MyValue::default();
        let b = a.clone();

        a.magical_update();
        println!("{:?}", snapshot(&a, &b));
    }
    ```
* 你持有引用计数指针（`Arc`、`Rc`）。
* 你有小型结构体，大到不适合 `Copy`，但克隆开销和 `std::collections` 相当。一个例子是 HTTP 客户端，如 `hyper_util::client::legacy::Client`，克隆它就可以共享连接池。
* 你有需要按拥有权修改的链式结构体修改器，一些 **builder** 要求拥有所有权的修改，但大多数自定义 builder 可以用 `pub fn with_xyz(&mut self, value: Xyz) -> &mut Self` 实现。
```rust
// Inline `HashMap` insertion extension

fn insert_owned(mut self, key: K, value: V) -> Self {
    self.insert(key, value);
    self
}
```
* 所有权也是建模业务逻辑/状态的好方式。例如：
```rust
let not_validated: String = ...;// some user source
let validated = Validate::try_from(not_validated)?;
// Technically that `try_from` maybe didn't need ownership, but taking it lets us model intent
```

### 何时**不**传递所有权？

* 优先采用接受引用的 API 设计（`fn process(values: &[T])`），而不是接受所有权（`fn process(values: Vec<T>)`）。
* 如果你只需要对元素的读访问，优先使用 `.iter` 或切片：
```rust
for item in &some_vec {
    ...
}
```
* 你需要修改由另一个线程拥有的数据时，使用 `&mut MyStruct`。

### 对"可能拥有"的数据使用 `Cow`

有时你实际上并不需要拥有所有权的数据，但从 API 的角度看并不明确，这时使用 [`std::borrow::Cow`](https://doc.rust-lang.org/std/borrow/enum.Cow.html) 是高效处理这种情况的方式：

```rust
use std::borrow::Cow;

fn hello_greet(name: Cow<'_, str>) {
    println!("Hello {name}");
}

hello_greet(Cow::Borrowed("Julia"));
hello_greet(Cow::Owned("Naomi".to_string()));
```

## 3.3 栈 vs 堆：对大小保持敏感！

### ✅ 好的实践

* 让小型类型（`impl Copy`、`usize`、`bool` 等）**留在栈上**。
* 避免按值传递或转移巨大类型（`> 512 字节`）的所有权。优先按引用传递（例如 `&T` 和 `&mut T`）。
* 递归数据结构在堆上分配：
```rust
enum OctreeNode<T> {
    Node(T),
    Children(Box<[Node<T>; 8]>),
}
```
* 小型类型按值返回：实现了 `Copy` 或克隆开销低的类型按值返回是高效的（例如 `struct Vector2 {x: f32, y: f32}`）。

### ❗ 注意

* 只有当基准测试证明有益时才使用 `#[inline]`——Rust 在**没有**提示的情况下已经很擅长内联了。
* 避免大规模栈分配，把它们装箱。例如 `let buffer: Box<[u8; 65536]> = Box::new(..)` 会先在栈上分配 `[u8; 65536]` 然后再装箱；一种非 const 的解决方案是 `let buffer: Box<[u8]> = vec![0; 65536].into_boxed_slice()`。
* 对于大型 `const` 数组，考虑使用 [smallvec crate](https://docs.rs/smallvec/latest/smallvec/)，它的行为像数组，但足够聪明，能把大数组分配到堆上。

## 3.4 迭代器与零成本抽象

Rust 迭代器是惰性的，但最终会被编译成非常高效的紧凑循环，只在被消费时才会执行。链式调用 `.filter()`、`.map()`、`.rev()`、`.skip()`、`.take()`、`.collect()` 通常不会产生额外开销，编译器能够很好地推断如何优化它们。
* 处理集合时优先使用`迭代器`而非手动 `for` 循环，编译器能比手动写法更好地优化它们。
* 调用 `.iter()` 只创建对原集合的**引用**，这允许你持有同一集合的多个迭代器。

#### ❗ 避免创建中间集合，除非确实需要：

* 假设 `process` 接受一个`迭代器`。
* ❌ 差——无用的中间集合：
```rust
let doubled: Vec<_> = items.iter().map(|x| x * 2).collect();
process(doubled);
```
* ✅ 好——传递迭代器（`fn process(arg: impl Iterator<Item = T>)`）：
```rust
let doubled_iter = items.iter().map(|x| x * 2);
process(doubled_iter);
```
