---
name: test-layers
description: 把测试放在能证明其规则的最便宜一层。在写测试、审查或裁剪套件、或判断脆弱、变更检测器、过 mock 的测试时使用。
---

# Test Layers

一条测试在一层（**layer**）上 *pin* 一条**规则**（**rule**），并带独立 **oracle**。写测试 → Write。审查套件 → Review。

## Write

1. 写出规则（哪条 bug 会 *red*）和 oracle。完成：两者都已写下。
2. 走 [tree](#tree)。只在该层写一条。完成：测试落在选定的层。
3. 套每一条 [Quality](#quality)。完成：每一条都成立。

## Review

1. 按实际 *starts* 的东西给范围内每条测试打标（in-process、HTTP、子进程、数据库、浏览器）。完成：每条都有标签。
2. 走 [tree](#tree)。处置：`keep` / `demote` / `native+fixture` / `delete`。完成：每条都有处置，并写明层和规则。
3. 套 [smells](references/smells.md) 中每一条。完成：每条味道都查过；每个命中写明味道、测试、错过的 Quality 项、新处置。
4. `demote` 和 `delete` 先提案，同意后再改。完成：提案集合与处置一致。

## Tree

```text
这条测试 pin 哪条规则？
  更便宜的一层已经 pin 了同一输入类、失败模式和 oracle？
    是 → 停
    否 → 真正的失败出现在哪？
          同进程逻辑                               → in-process
          进程、信号、线、崩溃、冻输入             → boundary
          第三方引擎原生结果                       → native
```

**in-process.** 单元的公共 API；fake 下一跳 I/O。计算、排队、映射、校验。

**boundary.** 把那条进程、线或 OS 事实真正跑起来。少。HTTP 鉴权、杀进程/崩溃隔离、需要 JS 或可视状态的浏览器旅程。

**native.** 对引擎做一次真正的 execute。字段映射用夹具。

从 **in-process** 起。规则本身就是边界或原生引擎结果时再升级。

## Quality

每一条都套。

**Pin behavior.** 在公共接口上断言返回值、错误和可见副作用。内部调用顺序仅当该顺序本身就是契约（只扣一次费、从缓存提供）；为该保证命名。

**Independent oracle.** 字面量、规格或算过的例子。把生产公式用两遍是同一次计算，不是检查。

**DAMP.** 输入和期望留在正文。只抽出会迫使许多测试同步改结构的重复。

**One behavior.** 一条测试一条规则，以保证命名。共享 setup 和断言 → 一张表。不同失败模式 → 分开。生产代码并不分支的输入留在表里。

**Isolated.** 任意顺序，同一结果。在边界注入时钟、种子和 I/O。Flake 隔离或修好。

**Load-bearing.** 测团队可能写错的东西。框架、配置字面量、getter 由它们驱动的行为覆盖。

**Coverage.** 从未执行的代码是线索。运算符翻转时会红的断言才 pin 住规则。

**Delete with evidence.** 同一 oracle、同一输入类、没有多抓一种故障。相同的行覆盖仍可能藏着两个 oracle。

## Examples

- 队列 / 并发上限 → in-process（打桩计算槽）。
- 超时能杀掉计算；崩溃不留半截行 → boundary（真进程）。
- 领域对象 → JSON → in-process（夹具）。
- HTTP 鉴权 → boundary（一条真实请求）。handler 里的计算 → in-process。
- 需要 JS 的浏览器旅程 → boundary。
