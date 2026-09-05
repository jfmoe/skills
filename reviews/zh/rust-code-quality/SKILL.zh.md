---
name: rust-code-quality
description: 编写、修改和审查地道（idiomatic）Rust 代码的指南，涵盖使用 Tokio 的生产级异步 Rust，包括任务、通道、取消、错误处理和并发控制。在创建或修改 Rust 代码、审查 Rust diff、分支或 PR 时使用，也可在其他 skill 需要进行 Rust 代码质量审查时使用。
---

## 最佳实践参考

在编写、修改或审查 Rust 之前，在同一轮对话中阅读所有相关章节。在实现变更或提供审查反馈时参考以下文件：

- [Chapter 1 - Coding Styles and Idioms](references/chapter_01.md)：借用 vs 克隆、`Copy`、`Option`/`Result`、内存分配、迭代器、注释、导入
- [Chapter 2 - Clippy and Linting](references/chapter_02.md)：Clippy 配置、重要 lint、工作区 lint 设置
- [Chapter 3 - Performance Mindset](references/chapter_03.md)：性能分析、避免冗余克隆、栈 vs 堆、零成本抽象
- [Chapter 4 - Error Handling](references/chapter_04.md)：`Result` vs panic、`thiserror` vs `anyhow`、错误层级
- [Chapter 5 - Automated Testing](references/chapter_05.md)：测试命名、断言、文档测试、集成测试、快照测试
- [Chapter 6 - Generics and Dispatch](references/chapter_06.md)：静态分发 vs 动态分发、trait 对象
- [Chapter 7 - Type State Pattern](references/chapter_07.md)：编译期状态安全、何时使用
- [Chapter 8 - Comments vs Documentation](references/chapter_08.md)：注释、文档注释、rustdoc
- [Chapter 9 - Understanding Pointers](references/chapter_09.md)：线程安全、`Send`/`Sync`、指针类型
- [Chapter 10 - Async Rust Patterns](references/chapter_10.md)：Tokio 任务、通道、错误、关闭、异步 trait、流、资源管理

审查 Rust 代码时，请对照每个相关章节检查代码质量。

## 快速参考

### 借用与所有权

- 优先使用 `&T` 而非 `.clone()`，除非确实需要转移所有权
- 在函数参数中使用 `&str` 而非 `String`，使用 `&[T]` 而非 `Vec<T>`
- 小型 `Copy` 类型可以按值传递
- 当所有权不明确时使用 `Cow<'_, T>`

### 错误处理

- 对可能失败的操作返回 `Result<T, E>`；在生产代码中避免 `panic!`
- 除非可以证明失败不可能发生，否则在测试之外避免使用 `unwrap()`/`expect()`
- 库错误使用 `thiserror`，应用层错误使用 `anyhow`
- 错误传播优先使用 `?` 而非 match 链

### 性能

- 先测量再优化，并对 release 构建进行基准测试
- 避免在循环中克隆以及不必要的中间集合
- 当迭代器能改善组合性和清晰度时优先使用迭代器
- 使用性能分析和基准测试来验证性能变更

### Lint

运行项目的 lint 命令。当项目没有现成命令时，从以下命令开始：

```shell
cargo clippy --all-targets --all-features --locked -- -D warnings
```

关键 lint：

- `redundant_clone`
- `large_enum_variant`
- `needless_collect`
- `clone_on_copy`

优先使用有正当理由的 `#[expect(clippy::lint)]`，而非宽泛的 `#[allow(...)]`。

### 测试

- 测试命名要有描述性
- 每个测试聚焦一个行为
- 测试错误和边界情况
- 使用文档测试展示公共 API 示例
- 快照用于复杂的结构化输出，而非简单值

### 泛型与分发

- 当具体类型已知时，优先使用泛型和静态分发
- 当需要运行时多态或异构集合时，使用 `dyn Trait`
- 在 API 边界处装箱（Box），而不是在实现内部过早装箱

### 类型状态（Type State）

当"让非法状态不可表示"能防止真实 bug 时，使用类型状态模式。当它只会增加泛型复杂度时，避免使用。

### 文档

- 使用 `//` 注释说明不明显的原因、安全性约束和变通方案
- 使用 `///` 和 `//!` 编写公共 API 和模块文档
- 在相关处记录错误、panic 和安全性契约
- 将可执行的 TODO 链接到已跟踪的 issue

### 异步 Rust

- 使用 `JoinSet` 或收集 `JoinHandle` 来持有派生的任务
- 使用 `tokio::select!` 进行 future 竞争和可感知取消的控制流
- 任务间通信优先使用通道；根据语义选择 `mpsc`、`broadcast`、`oneshot` 或 `watch`
- 使用信号量或缓冲流限制并发
- 使用 `CancellationToken` 传播取消，并定义优雅关闭
- 永远不要阻塞异步运行时，或在 `.await` 期间持有阻塞锁
- 不要无界地派生任务，也不要忽略任务和通道错误
- 使用 `tracing` 为异步操作添加埋点
