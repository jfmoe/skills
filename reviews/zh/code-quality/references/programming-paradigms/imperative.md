# 命令式 / 过程式编程

## 是什么

命令式编程把计算描述为一系列改变状态的语句：读输入、改变量、调外部系统、处理错误、写输出。过程式编程是同一个模型，只是组织成按顺序调用的过程（函数）。这是表达程序最古老也最直接的方式，与机器实际执行的方式紧密对应。

把命令式代码当作低级或不够讲究而不屑一顾，是错误的。真实世界充满有序的副作用——打开文件、读取、变换内容、写回、提交事务——而命令式风格是表达这个序列的诚实、可读的方式。目标不是消灭命令式代码，而是让它待在自己该待的地方，并阻止业务规则与它缠在一起。

## 背后的假设

- 有些逻辑本质上是顺序的：每一步依赖前一步的效果。
- 副作用应当*可见*——按顺序铺开，而不是藏在层层抽象后面。
- 对短脚本、入口点和接线层，直接的线性流程通常比过早的架构更可维护。

## 什么时候适合

- CLI 入口、一次性脚本、迁移、运维工具。
- 应用启动：依赖接线、配置加载、日志初始化。
- I/O 编排：协调一个事务、按必需顺序调用多个外部系统、安排读写次序。
- 几乎任何程序的最外层——必须真正在世界上*做*事的那部分。

健康的命令式入口读起来像一份食谱；每一步命名一个阶段，副作用按顺序可见：

```python
def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config_path)
    configure_logging(config.log_level)
    client = build_client(config)
    try:
        result = run_job(client, config)  # decision logic lives here, takes plain data
    except JobError as exc:
        logging.getLogger(__name__).error("job failed: %s", exc)
        return 1
    write_report(result, args.output)
    return 0
```

注意入口*没有*做什么：它不自己计算结果。它编排 I/O，并把实际决策委托给 `run_job`——后者不需要真实客户端就能测试。

## 什么时候变成问题

- 核心业务规则与 I/O 交织在一个长函数里，于是没有数据库、时钟或网络就无法测试规则。
- 复杂状态变化没有边界，经由全局变量或一个到处传的易变字典渗漏过每一层。
- 错误处理散落在流程各处，无法作为一个单元复用或推理。
- 函数长到读者无法装进脑子，唯一的结构是自上而下的顺序。
- "再加一个标志就好"的参数不断累积，直到过程被一打布尔值驾驶着隐藏分支；这是不同的操作被合并进了一个序列的信号。

当你看到这些信号时，问题通常不是"太命令式"，而是"命令式用错了地方"：本应收进可测试之物的决策逻辑待错了位置。修复很少是让代码整体上不那么命令式；而是把*决策*的部分与*行动*的部分分开。

考虑一个把两者交织在一起的函数：

```python
def process(order_id: int) -> None:
    row = db.fetch_order(order_id)          # I/O
    if row.status == "paid" and row.total > 100:   # decision
        discount = row.total * 0.1          # decision
        db.apply_discount(order_id, discount)   # I/O
        mailer.send(row.email, "discount applied")  # I/O
```

这条规则（已支付且超过 100 的订单打九折）没有数据库和邮件器就无法测试。把决策抽出来，它就变成一个可以用纯值测试的纯函数，而命令式外壳只保留 I/O：

```python
def compute_discount(order: Order) -> Decimal:   # pure, trivially testable
    if order.status == "paid" and order.total > 100:
        return order.total * Decimal("0.1")
    return Decimal(0)

def process(order_id: int) -> None:              # thin imperative shell
    order = db.fetch_order(order_id)
    discount = compute_discount(order)
    if discount:
        db.apply_discount(order_id, discount)
        mailer.send(order.email, "discount applied")
```

## 过程式分解

过程式风格不只是"一个长函数"。它的纪律是把流程分解成具名过程，各自处于单一抽象层次。好的过程读起来像一串名字讲出故事的调用；你不用深入其中任何一个就能理解流程。当你发现自己在给一块代码加注释做标签（`# now validate the records`）时，那块代码通常想变成一个具名函数（`validate_records(...)`）。注释会腐烂；函数名则每次都被读者检验。

让每个过程保持在一个抽象层次。在同一函数里混合高层编排（`run_job`）和底层字节摆弄，会迫使读者不断切换高度。把细节下推到它们自己的过程里，让调用方保持为可读的摘要。

## 与函数式核心 / 命令式外壳的关系

最干净的解法是保留命令式风格，但把它限制在薄薄的外层。这就是 [functional-core.md](./functional-core.md) 的命令式外壳：外壳编排 I/O、事务、重试和日志；核心接受纯数据、应用规则、返回纯数据。外壳有意保持命令式；有序的副作用就住在那里。你移出去的是决策，而不是编排。

这也连接到 [data-oriented.md](./data-oriented.md)（外壳传给核心的数据）和 [resource-lifecycle.md](./resource-lifecycle.md)（外壳如何获取与释放它编排的资源）。
