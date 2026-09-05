# 访问者（Visitor）

访问者模式把操作与它们所作用的对象结构分离。它让你可以在不修改一组固定节点类型的情况下，为它们定义新操作。每个节点类型实现一个 `accept(visitor)` 方法，调用访问者对应的 `visit_*` 方法，从而实现双重分发。

当类型集合稳定但操作集合频繁变化时，这个模式最有价值。它反转了通常的权衡：新增操作容易（新增一个访问者类），但新增节点类型需要更新所有现有访问者。

## 结构

- 元素（节点类型）：声明 `accept(visitor)`。
- 具体元素（ConcreteElement）：通过调用 `visitor.visit_concrete_element(self)` 实现 `accept`。
- 访问者（接口）：为每种元素类型声明一个 `visit_*` 方法。
- 具体访问者（ConcreteVisitor）：用操作特有的逻辑实现每个 `visit_*`。

## 何时适合这个模式

- 节点类型层级稳定。新类型很少出现。
- 针对结构的新操作很常见。
- 操作需要访问具体类型，而不想用 `isinstance` 级联。
- 操作逻辑不应污染数据类。
- 存在多个独立的遍历关注点（lint、变换、序列化、美化打印）。

## 何时不适合这个模式

- 节点类型频繁变化。每个新类型都迫使更新所有访问者。
- 结构简单到单个递归函数或 `match`/`case` 就够。
- 只有一两个操作。accept/visit 的仪式不增加任何清晰度。
- 语言支持模式匹配或 `singledispatch`，使双重分发不再必要。
- 操作不需要完整的具体类型；一个公共接口方法就够了。

## 常见实现问题

**遍历职责。** 谁来走树：访问者、节点的 accept 方法、还是外部迭代器？在一个结构内保持一致。混用策略会导致节点被访问两次或被跳过。

**返回值。** 经典访问者用无返回值的 visit 加累积状态。对于每次访问都产出一个值的函数式遍历，考虑从 visit 方法返回值，而不是修改访问者。

**默认处理。** 为未知节点类型提供 `visit_default` 或 `generic_visit`。没有它，新增节点类型会静默跳过访问而不是报错。这在不断演化的树中尤其重要。

**组合子节点。** 对树结构，决定 `accept` 是自动递归进子节点，还是需要显式的访问者逻辑。自动递归方便但可能隐藏遍历顺序；显式遍历让访问者控制深度优先还是广度优先，并允许剪枝。

## Python 示例

Python 的 `ast.NodeVisitor` 是实用的访问者变体，而不是经典的基于 `accept()` 的双重分发形式。AST 节点不实现 `accept()`；`NodeVisitor.visit()` 分发到 `visit_<NodeType>`，而 `generic_visit()` 负责走子节点：

```python
import ast


class DefinitionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.names.append(node.name)
        self.generic_visit(node)


tree = ast.parse("""
class User:
    def display_name(self):
        return "Ada"
""")

collector = DefinitionCollector()
collector.visit(tree)

assert collector.names == ["User", "display_name"]
```

AST 节点保持不变，而访问者在它们之上新增了一个操作。在特化方法中调用 `generic_visit()` 会继续遍历该节点的子节点；省略它就会剪掉那棵子树。

## 与策略的关系

[策略](./strategy.md)在稳定调用点之后变化算法。访问者在稳定类型层级之上变化操作。策略是按调用点的；访问者是按节点类型族的。如果你只有一个作用于许多类型的操作，访问者可能过度；[策略](./strategy.md)或一个普通函数就够了。
