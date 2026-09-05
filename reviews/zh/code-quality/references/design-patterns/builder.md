# 构建器（Builder）

## 意图

把复杂对象的构造与其最终表示分离，使同一个构造过程可以分步驱动、沿途验证，或被复用来产生不同的输出。

## 它解决的问题

有些对象用一次构造函数调用来创建很别扭：许多可选参数、分阶段进行的构造、来自多个来源的输入、或依赖字段组合的验证。把这些全塞进一个构造函数会产生长长的参数列表、望远镜式构造函数、以及与赋值纠缠的验证逻辑。构建器给组装过程一个自己的、有名字的家，在那里它可以被测试和复用。

## 结构与参与者

经典形式有一个**指挥者（director）**对着一个**构建器**接口驱动一系列步骤；**具体构建器**累积状态并产出**产品**。实践中指挥者常常塌缩成一个普通函数，构建器则是任何累积部分状态的东西。

## 何时使用

- 对象有许多可选参数或若干种合法的构造形状。
- 构造分阶段进行，阶段之间有中间验证。
- 同一个构造过程必须产出不同表示（HTML、PDF、JSON）：这是构建器的经典正当性。
- 组装逻辑本身值得独立于产品被命名、测试和复用。

## 何时不使用

- 一个带命名字段和默认值的记录已经说得很清楚。在简单值对象上套流式构建器是纯粹的仪式。
- schema 或模型类型已经从原始数据给了你经过验证的构造。
- 构建器藏着一堆调用顺序重要却不被强制的可变状态：那比单一构造函数更难推理。

## 失败模式

- 流式构建器在必填步骤尚未运行时就调用 `build()` 会产出半初始化的产品。在 `build()` 里验证，或把必填字段做成构造函数参数。
- 可变构建器状态在产品之间被共享或复用，把一次构建泄漏进下一次。
- 构建器复制了产品的不变量而不是委托给产品自己的验证，于是两者渐行渐远。

## Rust 示例

在 Rust 中，构建器可以通过消费自身的链式方法累积构造选项，然后用 `build()` 产出最终值：

```rust
struct RequestBuilder {
    endpoint: String,
    timeout_ms: u64,
    retries: u8,
}

impl RequestBuilder {
    fn new(endpoint: impl Into<String>) -> Self {
        Self {
            endpoint: endpoint.into(),
            timeout_ms: 1_000,
            retries: 0,
        }
    }

    fn timeout_ms(mut self, value: u64) -> Self {
        self.timeout_ms = value;
        self
    }

    fn retries(mut self, value: u8) -> Self {
        self.retries = value;
        self
    }

    fn build(self) -> Request {
        Request {
            endpoint: self.endpoint,
            timeout_ms: self.timeout_ms,
            retries: self.retries,
        }
    }
}

let request = RequestBuilder::new("https://example.com")
    .timeout_ms(2_000)
    .retries(3)
    .build();
```

## 与其他模式的关系

[factory.md](./factory.md) 一步决定造*哪个*类；构建器处理分好几步的复杂*如何组装*。[abstract-factory.md](./abstract-factory.md) 常用构建器来构造它的各个产品。原型（Prototype）路线——克隆一个模板再改几个字段——是另一种选择，适合你主要需要相对现有对象的小改动、而不是全新的分阶段构造时。
