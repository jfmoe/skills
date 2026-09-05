# 装饰器模式

本文档涵盖四人帮（GoF）的*结构型*装饰器模式：包装一个对象以增加行为。

## 意图

通过把对象包进另一个共享相同接口的对象，动态地给它附加额外职责。装饰器为扩展行为提供了子类化之外的灵活替代，而且可以在运行时组合和叠放。

## 它解决的问题

你有一个组件，以及几个可能加到它上面的可选、独立的行为：缓冲、压缩、加密、指标、重试。为每种组合做子类会爆炸：`BufferedCompressedStream`、`BufferedEncryptedStream`，等等。装饰器让每个行为成为自己的包装器，遵守组件的接口并委托给被包装对象。你在运行时按情况所需的任何顺序和组合，通过嵌套包装器来组合想要的行为。

## 结构与参与者

- **组件（Component）**：原始对象及其装饰器共享的接口。
- **具体组件**：被装饰的基础对象。
- **装饰器（Decorator）**：持有一个 Component、实现 Component，并委托给被包装对象，在委托前后增加行为。
- **具体装饰器**：各自增加一项职责。

因为每个装饰器都实现同一个 Component 接口并持有一个 Component，装饰器和基础对象可以互换，并能任意嵌套。`Compress(Encrypt(FileStream(path)))` 本身就是一个 `Component`。

## 何时使用

- 你需要在运行时组合独立的行为，组合或顺序可变。
- 这些行为是横切且稳定的：日志、缓存、重试、认证、验证、指标、事务边界。
- 为每种组合做子类会让类数量爆炸。

## 何时不使用

- 只有一个固定行为要加、且没有运行时组合；一个普通 `@decorator` 函数，或者干脆内联这个行为，比对象装饰器层级更简单。
- 增加的行为需要资源生命周期（获取/释放）。上下文管理器比装饰器更清晰地表达建立与拆除。
- 你拿起装饰器是为了添加真正的业务逻辑。装饰器应保持薄；业务规则属于组件。

## 失败模式

- **隐藏的控制流**：叠放的装饰器模糊了执行顺序、异常在哪里被捕获、时间花在哪里。深栈难以调试。
- **丢失的元数据**：忘记 `functools.wraps` 会破坏 `__name__`、文档字符串和签名。
- **行为漂移**：装饰器悄悄改变组件的契约（返回类型、抛出的错误），使包装过和未包装的对象不再可互换。
- **性能意外**：每层增加一个调用帧、可能还有 I/O；指标加重试加缓存的栈可能比操作本身还贵。

## Python 示例

Python 把函数当作一等对象，还有专门的 `@decorator` 语法，因此函数装饰器直接表达了同样的包装思想：

```python
def with_metrics(handler: Handler) -> Handler:
    @functools.wraps(handler)
    async def wrapped(request: Request) -> Response:
        with timer("handler.duration"):
            return await handler(request)
    return wrapped

@with_metrics
async def handle_request(request: Request) -> Response:
    return await process(request)
```

## 与其他模式的关系

[adapter.md](./adapter.md) 改变接口。装饰器保持同一接口并增加行为。代理（Proxy）也用相同接口包装，但它控制的是*访问*——如惰性加载或权限——而不是丰富行为。结构上它们几乎相同，差别在意图。链式装饰器类似流水线；顺序化的请求处理见责任链（Chain of Responsibility）。当行为是资源生命周期时，优先用上下文管理器而非装饰器。
