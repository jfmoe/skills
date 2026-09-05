# 薄包装 / 琐碎辅助函数

## 是什么

薄包装是这样的函数：整个函数体只是转发给另一个函数、重命名一次调用、或包装一个表达式，不添加任何语义价值。它不隐藏复杂度、不建立边界、不执行不变量。它只是增加了一个名字和一层。

```python
def get_user_name(user):
    return user.name  # adds nothing the caller couldn't see

def fetch_data(url):
    return requests.get(url)  # renames one call, hides nothing
```

坏味道不是"这个函数很短"。大量短函数是优秀的；一个捕获了领域概念的、命名良好的单行函数（`is_eligible_for_refund`）挣得出自己的存在价值。坏味道在于*新增意义的缺失*：包装付出了一个名字、一次跳转和一个栈帧的代价，却没有任何回报。

这种坏味道在 agent 生成的代码里大量出现——"消除重复"或"提升可读性"的条件反射制造出一大堆各自只转发一次调用的单行辅助函数。结果是你得追着许多定义才能读懂的代码，而直接读原来内联的表达式本会更清晰。它与 `duplicated-code.md` 和 [`skills/code-quality/references/design-principles/dry.md`](../design-principles/dry.md) 中描述的"错误的 DRY"失败模式密切相关。

## 什么时候包装是有价值的

当包装在转发之外做了真实工作时，它挣得自己的位置：

- **不稳定实现之上的稳定接口。** 如果被包装的库、API 或内部模块可能变化，包装能把变化局部化。这是适配器（Adapter）思想；见 `skills/code-quality/references/design-patterns`。这里一个看似薄的包装，是一个接口很小的深模块。
- **测试接缝。** 一个为让调用方能对着假实现测试、或为让依赖可被注入而存在的函数，即使函数体琐碎，也提供了一个替换边界。见 [`skills/code-quality/references/design-principles/dependency-inversion.md`](../design-principles/dependency-inversion.md)。
- **横切关注点。** 添加日志、重试、缓存、指标或事务边界的包装确实增加了行为。这些是装饰器，不是薄包装。
- **有名字的领域概念。** 包装一个布尔表达式的 `requires_tax_review(order)` 让规则可搜索，并给它唯一的家。名字本身*就是*价值。

## 什么时候它们是噪音

- 只有一个调用方且没有抽象边界：内联它。
- 包装名字是被包装调用的同义词（用 `fetch_data` 包 `requests.get`），没有增加领域意义。
- 它把参数原样转发给一个名字同样清晰的函数。
- 它存在只是因为某条风格规则说"要提炼函数"，而不是因为有读者受益。

解法是 [inline-function.md](./inline-function.md)：把函数体折回调用方，删掉包装。

## 如何判断

问：如果我删掉这个函数、把它的函数体内联到每个调用点，代码会更难理解或更难修改吗？如果答案是否定的，它就是薄包装。如果移除它会让调用方暴露于不稳定的依赖、打散一条领域规则、或弄断一个测试接缝，那它在做真实的工作；保留它。检验标准是它守护的边界，而不是它的行数。
