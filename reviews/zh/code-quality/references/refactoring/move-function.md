# 搬移函数

## 是什么

搬移函数把一个函数（或方法）从一个模块或类搬到另一个更合适的归属处。程序的结构反映其行为住在哪里；随着理解的加深，行为常常被证明坐错了位置。搬移函数就是你纠正这一点的方式：把代码放到它所操作的数据旁边，放到与它一同变化的其他代码旁边。

```python
# before: account.py reaches into a rate table it doesn't own
class Account:
    def overdraft_charge(self):
        if self.type.is_premium:
            base = 10
            return base + max(0, self.days_overdrawn - 7) * 0.85
        return self.days_overdrawn * 1.75

# after: the charge rule lives with the account type that defines it
class AccountType:
    def overdraft_charge(self, days_overdrawn):
        if self.is_premium:
            return 10 + max(0, days_overdrawn - 7) * 0.85
        return days_overdrawn * 1.75
```

## 该搬移的信号

- **依恋情结。** 最清晰的信号：一个函数使用另一个对象的数据多于使用自己的。对付 [feature-envy.md](./feature-envy.md) 中那个坏味道的办法通常就是搬移函数；把行为搬到它所渴求的数据所属的对象上。这遵循 GRASP 中的信息专家（Information Expert）思想：把行为放到信息所在之处（[`skills/code-quality/references/design-principles/grasp.md`](../design-principles/grasp.md)）。
- **耦合方向。** 当模块 A 中的一个函数重度依赖模块 B 却几乎不依赖自己所在的模块时，依赖箭头正在与代码的位置打架。把函数搬到 B 可以理顺依赖图、降低耦合。
- **共同变化。** 当一个函数总是与另一个模块里的代码一起变化——你总是在同一次提交里编辑它们——它们多半属于彼此。这是 [shotgun-surgery.md](./shotgun-surgery.md) 的信号，指向合并。

## 安全地搬移

先确定函数需要从当前上下文中得到什么。如果它只用目标方的数据，搬移是干净的。如果它两边都沾，你可能需要先拆分它（提炼属于别处的部分，然后只搬那部分），或把剩余上下文作为参数传入。检查这个函数调用了什么、什么调用了它：搬移可能反转一个依赖或制造一个环，而这本身就是关于这次搬移是否正确信息。

每一步都保持行为并跑测试；见 [safe-refactoring.md](./safe-refactoring.md)。在 Python 里还要更新 import，并留意新位置引入的循环 import 风险。

## 迁移期间维持旧 API

当函数属于一个公开的或被广泛使用的接口时，不要一次性弄断调用方。把函数体搬到新家，然后在旧位置留一个转发到新位置的委托函数。这暂时是一个[薄包装函数](./thin-wrapper-function.md)，这没关系；它存在的意义是在调用方迁移期间保持旧 API 稳定。一旦每个调用方都指向新位置（用 `rg` 找到它们），删掉委托。如需弃用窗口期，在旧路径上标记警告，让调用方知道要更新。

## 什么时候不要搬移

如果一个函数真实地、均衡地使用来自多个对象的数据，可能不存在唯一的更优归属：强行搬移只是迁移了耦合。而如果"更优归属"是一个应当保持无行为的纯数据对象（DTO、ORM 行、配置对象），把行为搬进去会违反那条边界；这条线划在哪里见 `tell-dont-ask.md`。
