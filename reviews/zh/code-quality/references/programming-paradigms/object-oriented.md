# 面向对象编程

## 是什么

面向对象编程把状态、行为和不变量组织进对象，并通过它们的协作表达系统行为。对象把数据和允许施加其上的操作捆绑在一起，理想情况下还保证数据保持有效——其不变量在每一次公开操作中都成立。Python 完整支持 OO 但不强制：函数、模块和纯数据都是一等备选。

当一个概念拥有长寿命的身份、必须保持一致的内部状态、以及一组属于一体的操作时，OO 提供的价值最大。对一次性计算或数据整形，它提供的价值最小——那里函数或纯记录更清晰。

## 背后的假设

- 当一个概念有持久的身份、内部状态、不变量和相关行为时，把它建模为对象能把保护这些不变量的逻辑收在一处。
- 对象的接口应当表达*意义*，而不是暴露其内部存储布局。
- 继承用于建模真实的子类型关系或框架扩展点；实现复用更适合用组合。

## 什么时候适合

- 领域实体、值对象、资源对象、外部客户端、策略对象、插件对象。
- 必须维护不变量的对象：状态机、货币金额、时间区间、权限规则、有界缓冲区。
- 有显而易见生命周期的对象：连接池、事务、缓存、任务运行器。
- 多态：一个接口背后的若干实现，运行时选择——不过在 Python 里，一个 `Protocol` 加普通函数常常能以更少的仪式表达这一点。

"这该是个对象吗"的检验是：把数据和它的操作捆绑在一起，是否*保护了一条否则就是人人有责的不变量*。一个拒绝把两种货币相加的 `Money` 类型，或一个拒绝以 `end < start` 构造的 `DateRange`，挣得了自己的类，因为保证住在一处，没有调用方能绕过它：

```python
@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("end must not precede start")

    def overlaps(self, other: "DateRange") -> bool:
        return self.start <= other.end and other.start <= self.end
```

系统里每个 `DateRange` 按构造即有效，而重叠规则与它所操作的数据住在一起。对比之下，一个纯字典 `{"start": ..., "end": ...}` 的有效性必须由每个调用方重新检查。

## 常见错误

- **万物皆类。** 简单的纯计算和数据变换被硬塞进不持有任何状态的类。一模块的函数更清晰。
- **贫血模型。** `Manager`、`Service` 和 `Helper` 类吸走了所有行为，而"领域对象"退化成一袋子公开字段。数据和支配它的规则被拆开了——恰与 OO 的目的相反。见 [tell-dont-ask](../design-principles/tell-dont-ask.md)。
- **深继承。** 子类化被用来共享实现而非替换行为。每加一层都增加 MRO 复杂度和隐藏耦合。优先组合；见 [composition-over-inheritance](../design-principles/composition-over-inheritance.md)。
- **Java/C++ 仪式移植。** 为每次协作都引入接口、抽象基类和工厂层，而 Python 本来用一个函数、一个小 `Protocol` 或一个 `dataclass` 就够了。

贫血模型的陷阱值得具体看看。贫血版本把一条规则散落在每个调用方：

```python
# Anemic: the rule "cannot withdraw more than balance" lives in callers
@dataclass
class Account:
    balance: int

def withdraw(account: Account, amount: int) -> None:
    if amount > account.balance:      # every caller must remember this
        raise ValueError("insufficient funds")
    account.balance -= amount
```

封装版本自己拥有规则，于是没有调用方能违反它：

```python
@dataclass
class Account:
    _balance: int

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

差别不在风格。第一种形式里，一个忘记检查的新调用方就会弄坏余额；第二种里，不变量无法被绕过。这就是 [tell-dont-ask](../design-principles/tell-dont-ask.md) 原则的实践。

## 与其他范式的关系

一个有不变量的长寿对象，常常最好与 [state-machine.md](./state-machine.md) 搭配来管理其生命周期。其方法内部的决策*逻辑*仍可以是纯的，并推向 [functional-core.md](./functional-core.md)。"更多 OO"永远不是目标；目标是把状态、不变量和行为放到它们所属的边界上。
