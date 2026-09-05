# 资源生命周期设计

资源是任何必须获取、随后释放的东西：文件句柄、socket、锁、数据库连接或事务、临时目录、线程或任务、子进程。资源生命周期设计，就是为每一个资源回答：谁创建它、谁关闭它、以及在每一条离开路径上——包括异常路径——它如何被释放。大多数资源泄漏和"连接池耗尽"事故，都是从未被显式回答过的生命周期问题。

## 所有权

每个资源需要恰好一个所有者：负责释放它的代码。所有权含混既是泄漏的根因（每个人都以为别人会关），也是关闭后使用（use-after-close）bug 的根因（一个持有者在另一个还需要它时关掉了它）。

最清晰的规则是：创建资源的代码拥有它并关闭它，且在自己控制的作用域内完成。当一个函数只在自己存活期间需要某个资源时，它应当就地创建、使用并释放它。当资源必须活得比单个函数更长时，所有权上移到更长寿的持有者——应用对象、上下文、池——而该持有者的生命周期就成为资源的生命周期。把一个已打开的资源传入一个*不*拥有它的函数没问题，只要约定清晰：被调方使用它，调用方关闭它。

函数签名可以让所有权显式化。接受一个已打开资源的函数是借用它；自己打开资源的函数是拥有它。两者混用——有时自己开、有时接受传入——正是所有权变得含混、资源发生泄漏的地方。

```python
def write_report(out: TextIO, rows: list[Row]) -> None:
    # borrows out: the caller opened it and the caller closes it
    for row in rows:
        out.write(format_row(row))


def save_report(path: str, rows: list[Row]) -> None:
    # owns the file: opens it, uses it, releases it, all in one scope
    with open(path, "w") as out:
        write_report(out, rows)
```

借用方函数从不调用 `out.close()`；那会释放一个它不拥有的资源，让调用方措手不及。在一个接口上保持"借用还是拥有"的一致性，正是让泄漏易于推理的东西。

## RAII 与上下文管理器

RAII（Resource Acquisition Is Initialization，资源获取即初始化）把释放绑定到作用域结束，而不是绑定到一个你可能忘记的手工清理调用。Python 用上下文管理器协议和 `with` / `async with` 表达这一点：资源在进入时获取、在退出时释放，无论代码块正常返回还是抛出异常。

```python
with open(path) as f:
    data = f.read()
# f is closed here, even if read() raised
```

不要依赖 `__del__` 或 CPython 引用计数来释放文件、锁、事务或连接。析构时机因实现而异、在引用环下失效、且在异常路径上不可靠。让释放显式化并绑定作用域。

## 作用域绑定 vs 动态资源集

对固定的、静态已知的资源集，嵌套的 `with` 语句（或带多个管理器的单个 `with`）是最清晰的表达。当资源*数量*是动态的——每个输入路径开一个文件、获取一组数量不定的连接——用 `contextlib.ExitStack`（或 `AsyncExitStack`），而不是手写嵌套清理栈：

```python
from contextlib import ExitStack


def read_all(paths: list[str]) -> list[str]:
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        return [f.read() for f in files]
```

`ExitStack` 保证每个已进入的资源都按逆序释放，即使中途某次获取失败了。

## 异常路径

清理必须在出错时运行，而这恰恰是它最常被遗漏的时候。优先用 `with` 而非手工 `try/finally`，因为管理器把清理一次性且正确地封装了起来。当你确实要写 `try/finally` 时，释放放在 `finally` 里，而不是 `try` 块之后。自定义上下文管理器的 `__exit__` 不得吞掉异常，除非抑制异常就是它显式、有据可查的用途：从 `__exit__` 返回真值会悄悄隐藏错误。

## 异步资源所有权

异步资源（连接、会话、异步生成器）遵循同样的所有权规则，但使用 `async with` 和 `__aenter__` / `__aexit__`。两个额外的危险：持有资源的异步生成器可能被挂起且永远不再恢复，所以用 `contextlib.aclosing()` 保证其清理运行；由任务拥有的资源只有在该任务被正确 await 或取消时才会释放，所以后台任务需要显式的生命周期管理（见 [async-concurrency.md](./async-concurrency.md)）。

## 应用启动与关闭

最长寿的资源——连接池、客户端、线程池、缓存——由应用本身拥有。在启动时获取它们，在关闭时按逆序释放它们。框架的生命周期钩子（ASGI lifespan、应用工厂、依赖注入作用域）是正确的位置。避免在 import 时获取这些资源：import 时副作用让模块在测试或工具场景下无法安全导入，并把资源生命周期绑到导入顺序而非应用生命周期上（入口结构见 [imperative.md](./imperative.md)）。

## 部分初始化与释放顺序

当按顺序获取多个资源、而其中靠后的某次获取失败时，会出现一种微妙的失败模式。已经打开的资源仍必须被释放——按逆序——即使设置从未完成。手写代码容易在这里出错；"进行到一半"的清理路径是最不可能被测试的路径。

这是优先用 `with` 和 `ExitStack` 而非手工设置的另一个理由：无论设置在何处失败，它们都恰好释放那些成功进入的资源，且按逆序。按依赖顺序获取（先连接，后依附其上的事务），自动的逆序释放就能正确拆除：先事务，后连接。当必须显式安排释放顺序时，规则是后获取的先释放，因为较晚的资源在自己的清理期间可能还依赖较早的资源活着。

## 池化与租借模式

当获取很昂贵时（数据库连接、HTTP 会话），池拥有一组长寿资源，并在一个工作单元的存续期内把它们*租借*给调用方。调用方获取和释放的是租约，而不是资源：通常经由一个在进入时签出资源、退出时归还池的上下文管理器。纪律完全相同：租借的资源有清晰的作用域，并在每一条离开路径上——包括异常——归还池中。泄漏的租约比泄漏的文件更糟，因为它永久缩小池容量直至耗尽。

```python
def handle_request() -> Result:
    with pool.connection() as conn:   # lease on entry, return on exit
        return run_query(conn)
```

同一套 RAII 纪律从单个文件句柄一路扩展到应用级连接池：命名作用域、让释放自动化、永远不依赖垃圾回收器替你完成。
