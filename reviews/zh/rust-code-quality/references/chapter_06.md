# 第 6 章 - 泛型、动态分发与静态分发

> 能用静态就用静态，必须用动态才用动态

Rust 允许你用两种方式处理多态代码：
* **泛型 / 静态分发**：编译期，按使用点单态化（monomorphization）。
* **Trait 对象 / 动态分发**：运行时 vtable，单一实现。

理解这些权衡能让你写出更快、更小、更灵活的代码。

## 6.1 [泛型](https://doc.rust-lang.org/book/ch10-00-generics.html)

每种编程语言都有高效处理概念重复的工具。在 Rust 中，泛型就是这样一种工具：它是具体类型或其他属性的抽象占位符。我们可以在不知道编译和运行时代码中实际填充什么的情况下，表达泛型的行为或泛型之间的关系。

我们使用泛型为函数签名或结构体等条目创建定义，然后可以将这些定义用于许多不同的具体数据类型。我们先看看如何使用泛型定义函数、结构体、枚举和方法。泛型还可以用于实现类型状态模式（Type State Pattern），并将结构体的功能约束到特定预期类型上。关于类型状态的更多内容见[第 7 章](./chapter_07.md)。

[通过示例学习泛型](https://doc.rust-lang.org/rust-by-example/generics.html)。

### 泛型的性能

你可能会想，使用泛型类型参数是否有运行时开销。好消息是，使用泛型类型不会让你的程序比使用具体类型时运行得更慢。Rust 通过在编译期对使用泛型的代码执行单态化来实现这一点。单态化是通过填入编译时使用的具体类型，把泛型代码变成特定代码的过程。编译器检查泛型参数的所有出现位置，为泛型代码被调用时使用的具体类型生成代码。

## 6.2 静态分发：`impl Trait` 或 `<T: Trait>`

静态分发本质上是泛型的受限版本——带 trait 约束的泛型。在编译期，它能够检查你的泛型是否满足所声明的 trait。

### ✅ 最适合的场景：
* 你想要**零运行时开销**，为此付出编译期开销。
* 你需要**紧凑循环或高性能**。
* 你的类型在**编译期已知**。
* 你在处理**单次使用的实现**（单态化）。

### 🏎️ 示例：使用泛型的高性能函数
```rust
fn specialized_sum<T: MyTrait, U: Iterator<Item = T>>(iter: U) -> T {
    iter.map(|x| x.random_mapping()).sum()
}

// or, equivalent, more modern
fn specialized_sum<T: MyTrait>(iter: impl Iterator<Item = T>) -> T {
    iter.map(|x| x.random_mapping()).sum()
}
```

这会为每个使用点编译成**专门的机器代码**，快速且可内联。

## 6.3 动态分发：`dyn Trait`

动态分发通常与某种指针或引用一起使用，如 `Box<dyn Trait>`、`Arc<dyn Trait>` 或 `&dyn trait`。

### ✅ 最适合的场景：
* 你确实需要运行时多态。
* 你需要在一个集合中**存储不同的实现**。
* 你想**用稳定的接口抽象内部实现**。
* 你在编写**插件式架构**。

> ❗ 这更接近面向对象语言中的做法，可能伴随不小的开销。它可以完全避免泛型，并允许你混合实现了相同 trait 的类型。

### 🚚 示例：异构集合

```rust
trait Animal {
    fn greet(&self) -> String;
}

struct Dog;
impl Animal for Dog {
    fn greet(&self) -> String {
        "woof".to_string()
    }
}

struct Cat;
impl Animal for Cat {
    fn greet(&self) -> String {
        "meow".to_string()
    }
}

fn all_animals_greeting(animals: Vec<Box<dyn Animal>>) {
    for animal in animals {
        println!("{}", animal.greet())
    }
}
```

## 6.4 权衡总结

| | 静态分发（impl Trait） | 动态分发（dyn Trait） |
|------------------- |------------------------------ |---------------------------------- |
| 性能 | ✅ 更快，可内联 | ❌ 更慢：vtable 间接调用 |
| 编译时间 | ❌ 更慢：单态化 | ✅ 更快：共享代码 |
| 二进制体积 | ❌ 更大：按类型生成代码 | ✅ 更小 |
| 灵活性 | ❌ 僵硬，一次一个类型 | ✅ 可在集合中混合类型 |
| 在 trait fn() 中使用 | ❌ trait 必须是对象安全的 | ✅ 可用于 trait 对象 |
| 错误信息 | ✅ 更清晰 | ❌ 被擦除的类型可能让错误信息费解 |

* 当你控制调用点且追求性能时，优先使用泛型/静态分发。
* 当你需要抽象、插件或混合类型时，使用动态分发。🚨 有运行时开销。
* 如果不确定，先用泛型并加 trait 约束——当灵活性比速度更重要时再用 `Box<dyn Trait>`。

> 优先使用静态分发，直到你的 trait 需要隐藏在指针之后。

## 6.5 动态分发的最佳实践

动态分发 `Ptr<dyn Trait>` 是一个强大的工具，但也有显著的性能权衡。只有当**类型擦除或运行时多态**必不可少时才应该使用它。了解何时需要 trait 对象很重要：

### ✅ 何时使用动态分发：

* 你需要在集合中存放异构类型：
```rust
fn all_animals_greeting(animals: Vec<Box<dyn Animal>>) {
    for animal in animals {
        println!("{}", animal.greet())
    }
}
```

* 你想要运行时插件或可热插拔的组件。
* 你想对调用者抽象内部实现（库设计）。


### ❌ 何时避免动态分发：

* 你控制着具体类型。
* 你在编写性能关键路径上的代码。
* 你可以用其他方式表达相同的逻辑，同时保持简单，例如泛型。

## 6.6 🚨 Trait 对象的人体工学

* 当不需要所有权时，优先使用 `&dyn Trait` 而非 `Box<dyn Trait>`。
* 跨线程共享访问使用 `Arc<dyn Trait>`。
* 如果 trait 有返回 `Self` 的方法，就不要使用 `dyn Trait`。
* **避免过早装箱**。不要在结构体内部装箱，除非你确信它有益或是必需的（递归结构）。
```rust
// ✅ Use generics when possible
struct Renderer<B: Backend> {
    backend: B
}

// ❌ Premature Boxing
struct Renderer {
    backend: Box<dyn Backend> // Boxing too early
}
```
* 如果你必须在公共 API 中暴露 `dyn trait`，在边界处装箱，而不是在内部。
* **对象安全（Object Safety）**：只有对象安全的 trait 才能创建 `dyn Trait`：
    * 它**没有泛型方法**。
    * 它不要求 `Self: Sized`。
    * 所有方法签名使用 `&self`、`&mut self` 或 `self`。
    ```rust
    // ✅ Object Safe
    trait Runnable {
        fn run(&self);
    }

    // ❌ Not Object Safe
    trait Factory {
        fn create<T>() -> T; // generic methods are not allowed
    }
    ```
