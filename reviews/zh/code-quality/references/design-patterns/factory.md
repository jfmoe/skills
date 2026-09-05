# 工厂方法

## 意图

把对象创建与使用对象的代码解耦。调用方按意图索取产品（"给我一个这个格式的解析器"），而不指名具体类、也不需要知道它如何组装。

## 它解决的问题

构造逻辑容易泄漏进调用方：选哪个具体类、如何验证输入、如何装配依赖、应用什么默认值。当同一个 `if kind == ...: return SomeClass(...)` 块出现在好几个地方时，对构造的一次修改就意味着编辑每个调用点。工厂方法把这个决定集中到一处并给它一个名字。

## 结构

在四人帮的经典形式中，`Creator` 声明一个返回 `Product` 的工厂方法，子类覆写它来决定具体产品。参与者是抽象创建者、具体创建者、产品接口和具体产品。

在 Python 中，完整的层级很少是合适的形状。"创建者"通常是普通函数、`classmethod` 或注册表查找。只有当框架把创建步骤定义为扩展点、而你的子类确实需要覆写它时，"子类覆写方法"的形式才赢得其位置。

## 何时使用

- 具体类型取决于运行时值：文件格式、协议名、配置项、插件名。
- 构造涉及你不想在调用点重复的验证、依赖装配或默认策略选择。
- 今天就有多个真实实现，或有一个确认的扩展点（插件、入口点）。

## 何时不使用

- 只有一个实现且构造很简单：直接调构造函数。
- 一行 `if` 或直接实例化就够了。把它包进抽象创建者层级是为没有变化的东西加间接。
- 凡构建对象的东西都命名为 `Factory`，稀释这个概念直到毫无意义。

## 失败模式

- Java 风格的抽象创建者/具体创建者树，而一个函数就够——迫使读者穿过好几层子类只为找到一个 `return`。
- 工厂函数悄悄吞掉未知类型并返回默认值，隐藏了配置错误。改为抛出清晰的领域错误。
- 工厂长出副作用（日志、I/O、注册），使构造不再纯净或可预测。

## Python 示例

优先用普通工厂函数：

```python
def make_parser(kind: str) -> Parser:
    match kind:
        case "json":
            return JsonParser()
        case "yaml":
            return YamlParser()
        case _:
            raise UnknownParserError(kind)
```

对于配置或插件驱动的创建，注册表让工厂对扩展开放而无需编辑分发：

```python
_PARSERS: dict[str, Callable[[], Parser]] = {}

def register_parser(kind: str, factory: Callable[[], Parser]) -> None:
    _PARSERS[kind] = factory

def make_parser(kind: str) -> Parser:
    try:
        return _PARSERS[kind]()
    except KeyError as exc:
        raise UnknownParserError(kind) from exc
```

`classmethod` 替代构造函数（`Model.from_dict`、`datetime.fromtimestamp`）是 Python 最常见的工厂形式：类自己拥有构建自身的命名方式。

## 与其他模式的关系

[abstract-factory.md](./abstract-factory.md) 把这个想法扩展到必须一起变化的整族产品。[builder.md](./builder.md) 处理复杂的分步构造，而不是选哪个类。当产品由一个同时驱动后续行为的运行时值选出时，这个选择可能真的属于 [strategy.md](./strategy.md)。当创建随参数类型变化时，`functools.singledispatch` 是相关的 Python 机制。
