# 提炼函数

## 是什么

提炼函数取一段代码片段，把它变成自己专属的有名字的函数，并用一次调用替换该片段。它是最常用的重构，也是对付[长函数](./long-function.md)的主要手段。Fowler 的指导原则关乎*意图*：如果你不得不花力气弄清一块代码在做什么，就把它提炼成一个以*做什么*而非*怎么做*命名的函数。名字承载意义，函数体容纳机制。

```python
# before
def print_owing(invoice):
    outstanding = 0
    for order in invoice.orders:
        outstanding += order.amount
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")

# after
def print_owing(invoice):
    outstanding = calculate_outstanding(invoice)
    print_details(invoice, outstanding)
```

## 什么时候提炼

- **一个内聚的阶段。** 完成更大序列中一个可识别步骤的代码块：校验输入、计算总额、格式化输出。把每个阶段抽出来，能把一堵代码墙变成可读的摘要。这与拆分阶段（Split Phase）搭配使用。
- **一个有名字的概念。** 一个值得命名的、有领域意义的条件或计算：`is_overdue(invoice)` 比裸露的日期比较更易读，而且这个名字可以被搜索到。
- **一项策略。** 可能变化或被复用的逻辑——比如评分规则或重试策略——适合成为一个可以传来传去、可以替换的函数。见 `skills/code-quality/references/design-patterns` 中的策略模式（Strategy）。
- **混合抽象层次。** 当高层意图和底层机制并排出现时，把机制提炼出去能让调用方恢复一致的层次。

## 为提炼出的函数命名

命名是这次重构的意义所在。以结果或意图命名：`calculate_outstanding`，而不是 `loop_orders`。如果你找不到好名字，这是一个信号：这个片段不是一个内聚的单元——要么你抓错了边界，要么代码在提炼之前需要重新思考。好名字让调用点读起来像一句话。

## 参数决策

传入函数需要的东西，返回它产出的东西。偏好短小的参数列表。如果你发现自己传入了许多总是一起出现的值，那是数据泥团；考虑引入一个小对象（见 `primitive-obsession.md`）而不是一个长签名。避免传入让函数二选一的标志位；那通常意味着一个函数里藏着两个函数。

## 保持行为

提炼不得改变可观察行为。留意那些在片段内部被修改、之后又被使用的变量；它们要变成返回值，或者——如果有好几个——就是边界选错了的信号。留意在代码进入独立函数后不再成立的提前返回、`break` 和 `continue`。提炼后跑测试；见 [safe-refactoring.md](./safe-refactoring.md)。IDE 的"提炼方法"能机械而安全地处理其中大部分。

## 什么时候不要提炼

- 代码内联着已经很清晰，且以单一抽象层次阅读。
- 提炼会产生一个[薄包装函数](./thin-wrapper-function.md)：名字只是复述一个表达式、只有一个调用方、没有边界的函数。
- 片段与周围状态缠结，提炼出的签名会有许多参数和许多返回值。先解开缠结，或重新考虑接缝。

提炼是可逆的：如果后来的阅读表明提炼带来的是遮蔽而非澄清，用 [inline-function.md](./inline-function.md) 把它折回去。
