# 函数式核心，命令式外壳

## 是什么

函数式核心、命令式外壳（Functional Core, Imperative Shell）是由 Gary Bernhardt 推广的一种架构。它把程序拆成遵循不同规则的两层。*核心*持有纯决策逻辑：给定输入数据，它计算输出数据，不产生任何副作用——没有 I/O、没有时钟读取、没有随机性、没有网络、没有数据库、没有全局变更。*外壳*是与外部世界对话的薄命令式层：它读输入、调用核心决定该发生什么，然后执行核心所要求的副作用。

其洞见在于：让代码难测、难推理的，几乎从不是算术或分支；而是对环境的依赖。一个决定订单*能否*发货的函数容易测试；一个既做决定、又扣银行卡、写一行数据、发一封邮件的函数则不然。把环境推到边缘，有意思的逻辑就变成纯的、完备的、极易测试的。

这不是官方的 Python 概念，但它与 Python 的多范式风格、以及 [imperative.md](./imperative.md) 中描述的入口边界纪律天然组合。

## 背后的假设

- 系统中测试代价高的部分是副作用和环境耦合，而不是计算。
- 一旦副作用被推到边界，核心就能用"纯数据进、纯数据出"来测试：没有 mock、没有夹具、没有打补丁的时钟。
- 外壳仍然需要真实的设计投入，因为事务、重试、错误处理、日志和资源生命周期都住在那里。

## 收益

- **可测试性。** 核心测试是基于示例的：传数据，断言返回的数据。没有 I/O 搭建、没有 mock 框架，快速且确定。这是最大的一笔回报。
- **可推理。** 纯函数的行为完全由其参数决定。你可以孤立地理解它，不用追踪它触碰了什么全局状态或外部服务。
- **可组合性。** 纯函数干净地组合：一个的输出喂给下一个，没有隐藏的顺序约束。不纯的步骤由外壳显式地编排一次。

## 什么时候应用

凡是有意思的决策能与执行它的动作分开的地方，都可以应用：

- 领域规则：定价、资格、权限检查、状态转换（见 [state-machine.md](./state-machine.md)，其中 `(state, event) -> new_state` 的 reducer 就是教科书式的函数式核心）。
- 输入触及持久化之前的校验与规范化。
- 变换规则为纯、只有读写两端不纯的数据变换管道。
- CLI 与请求处理器：外壳解析参数或 HTTP、组装依赖、调用纯规划器；核心返回一个决策或一份待做工作的描述。

一个有用的形态是让核心返回副作用的*描述*（一串命令、一个事件、一个类型化结果），让外壳去执行它们。核心决策；外壳行动。

```python
# core: pure, no I/O; trivial to test with data in, data out
def plan_discount(cart: Cart, customer: Customer) -> DiscountPlan:
    if customer.tier == "gold" and cart.total > 100:
        return DiscountPlan(percent=15, reason="gold-large-order")
    return DiscountPlan(percent=0, reason="none")


# shell: imperative, owns I/O, transactions, logging
def apply_discount(cart_id: str, customer_id: str) -> None:
    cart = repo.load_cart(cart_id)          # I/O
    customer = repo.load_customer(customer_id)  # I/O
    plan = plan_discount(cart, customer)    # pure decision
    repo.save_discount(cart_id, plan)       # I/O
    logger.info("applied %s", plan.reason)  # I/O
```

`plan_discount` 的测试构造一个 `Cart` 和 `Customer`，调用函数，断言返回的 `DiscountPlan`：没有数据库、没有 mock、没有打补丁的时钟。折扣规则的每个分支都能用一行 setup 触及。相比之下，外壳用少数几个集成测试来测，或者薄到读一遍就能验证。

## 什么时候严格纯化适得其反

- **I/O 密集的胶水代码。** 全部职责就是在两个系统间搬运字节的代码，几乎没有可抽取的纯决策。硬套函数式核心会产生一个空心核心和一个藏住真实复杂度的肥胖外壳。
- **简单 CRUD。** 当操作是"读行、改字段、写行"时，没有值得隔离的有意义的决策。直接的命令式函数比人为的拆分更清晰。
- **拷贝代价高的数据。** 严格纯化禁止变更，于是天真的核心可能反复拷贝大结构。当该代价占主导时，允许在其余部分仍纯的函数内部做局部变更，或在这条接缝上放宽纯性。
- **贫血核心。** 如果拆分给你留下一堆不再说领域语言的微小纯函数迷宫，你是用清晰换了教条。让核心保持用领域术语表达。

要警惕的失败模式是外壳薄到事务、错误处理和可观测性无处安放、渗漏回框架回调里。外壳是真实的一层，不是包装。

## 边界画在哪里

画好这条线是全部技艺所在。接缝恰在"基于手头已有数据做出决策"的位置。先把决策需要的一切读进来，在核心中决策，然后按决策行动；不要把读和决策交织在一起，因为每拉到逻辑中间的一次读取，都会把环境拖回核心。

一个常见的精进是让核心返回*描述*效果的数据，而不是裸值：

```python
# core returns a description of what should happen: still pure
def plan_effects(order: Order, now: datetime) -> list[Effect]:
    if order.is_overdue(now):
        return [ChargeLateFee(order.id), NotifyCustomer(order.id, "overdue")]
    return []


# shell interprets the descriptions: the only place effects actually fire
def process(order_id: str) -> None:
    order = repo.load(order_id)
    for effect in plan_effects(order, datetime.now(tz=UTC)):
        execute(effect)
```

现在连*选择*执行哪些效果都可以在任何一个都不执行的情况下测试：断言返回的列表。外壳缩小成一个哑解释器，而有意思的分支全在核心。这与 [state-machine.md](./state-machine.md) 的 reducer 返回 `(next_state, actions)` 时是同一个形状。

时钟——`datetime.now(tz=UTC)`——在外壳读取，并作为 `now` *传入*核心。正是这一步移动，让依赖时间的规则保持纯粹、测试时确定。

## 与其他范式的互动

- 直接建立在 [imperative.md](./imperative.md) 之上：外壳*就是*命令式编排层，有意保持薄。
- 纯核心是 [data-oriented.md](./data-oriented.md) 思想得到回报的地方：纯数据进，纯数据出。
- 对生命周期逻辑，核心中的纯 reducer 加一个执行效果的外壳，是构建 [state-machine.md](./state-machine.md) 最干净的方式。
