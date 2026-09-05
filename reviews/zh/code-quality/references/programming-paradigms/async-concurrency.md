# 异步与并发

并发让程序同时在几件事上取得进展。Python 里的异步并发（`async`/`await`、`asyncio`）是若干模型之一；它通过在 `await` 点挂起，在单线程上交错许多 I/O 密集型任务。它不是并行，也不是免费的：它把你的代码劈进一个"有颜色的"世界，异步函数只能从其他异步函数里被 await。核心设计问题不是"我怎么把这个变成异步"，而是"每个并发任务是否有清晰的所有者、生命周期和错误处理策略"。

## 结构化并发

现代异步设计中最重要的思想是结构化并发：一组相关的任务共享单一作用域，而该作用域在其中每个任务都完成之前不会退出。`asyncio.TaskGroup`（Python 3.11+）是标准工具，是 Trio 中"nursery"的结构对应物。

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(u)) for u in urls]
    return [t.result() for t in tasks]
```

`async with` 块在所有子任务完成之前不会完成。如果任何任务抛错，组会取消其余任务并传播错误。这给并发代码提供了与普通代码块相同的保证：当你离开作用域时，你启动的东西没有任何还在后台运行。任务有清晰的所有者（组）和清晰的寿命（块）。

## 取消与超时

取消以 `CancelledError` 的形式在任务内部、它的下一个 `await` 处抛出。它是控制流机制的一部分，不是可以吞掉的普通错误。如果你为了执行清理而捕获它，之后要重新抛出：压制它会破坏超时、`TaskGroup` 关闭，以及整个系统的取消传播。

```python
try:
    await do_work()
except asyncio.CancelledError:
    await cleanup()
    raise  # always re-raise
```

超时用 `asyncio.timeout()`（3.11+）或 `wait_for` 表达，它们在期限过后取消被包装的操作。设计长时间运行的操作时，要让它们有规律地到达 `await` 点，否则取消无法生效。

## 错误传播

在 `TaskGroup` 里，多个任务可能同时失败，所以错误以 `ExceptionGroup` 的形式浮现。用 `except*` 处理：

```python
try:
    async with asyncio.TaskGroup() as tg:
        ...
except* ValueError as eg:
    ...
```

普通的线性流程不需要 `except*`；单个被 await 的协程正常抛出单个异常。只在真正可能发生并发失败的地方才动用异常组。

## 背压

当生产者跑过消费者时，无界排队会变成无界内存增长。背压是把生产者降速到消费者速率的机制。用有界队列（`asyncio.Queue(maxsize=...)`）让满队列阻塞生产者，或用信号量给并发在途工作设上限。为背压而设计，正是"负载下优雅降级的扇出"与"耗尽内存或下游连接限制的扇出"之间的分野。

```python
sem = asyncio.Semaphore(10)  # at most 10 requests in flight at once


async def fetch_limited(url: str) -> Response:
    async with sem:
        return await fetch(url)


async def fetch_all(urls: list[str]) -> list[Response]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_limited(u)) for u in urls]
    return [t.result() for t in tasks]
```

没有信号量，10 万个 URL 的列表会同时打开 10 万个 socket，耗尽文件描述符或远端服务器的限制。上限把"同时全部"变成"一次十个"，这就是背压为你买来的东西。

## 异步资源所有权

在任务内部获取的资源，只有在任务完成或被干净取消时才会释放，所以异步资源必须用 `async with` 拥有，并在取消路径上也清理。持有资源的异步生成器需要 `contextlib.aclosing()` 来保证其终结，因为被挂起的生成器否则可能永远不再恢复。这是 [resource-lifecycle.md](./resource-lifecycle.md) 的异步面孔。

## 异步何时有益、何时有害

对有许多并发操作的 I/O 密集型工作，异步是正确工具：网络请求、数据库查询、大量同时连接、向多个服务的扇出。单线程把时间花在等待 I/O 上，异步让它重叠这些等待。

当工作是 CPU 密集型时，异步增加成本而无收益：重计算会阻塞单个事件循环、饿死其他所有任务；那种情况用进程或线程。对简单的顺序脚本它也是开销：如果没有并发可利用，异步只增加有色函数约束和一个要管理的运行时。不要因为异步时髦就把代码库异步化；要因为它有真实的 I/O 并发可利用才异步化。

## 常见错误

- **发后即忘。** 调用 `create_task()` 却不保留引用、也没有组。任务可能在半空被垃圾回收，它的异常凭空消失。每个任务都需要一个所有者。
- **未处理的任务异常。** 一个异常从未被取走的裸任务会无声失败。`TaskGroup` 在设计上解决了这一点；单独的任务需要显式的 `add_done_callback` 处理或 await。
- **阻塞事件循环。** 在协程里调用同步阻塞 I/O（`requests.get`、`time.sleep`、阻塞式数据库驱动）会冻结其他所有任务。用异步等价物，或用 `asyncio.to_thread()` 把阻塞调用推到线程。
- **吞掉 `CancelledError`**：上文已述；它会悄悄破坏整个取消系统。

贯穿线：当每个任务都有所有者和作用域时，并发是可管理的。结构化并发、诚实的取消和背压，是你防止"许多事同时发生"变成"许多你再也无法交代的事"的手段。
