# 测试味道

在 Review 第 3 步加载。每条味道都是 Quality 未满足的症状。确认它在消耗套件，再改树给出的处置。每一节都要套。

每个命中：味道、测试、错过的 Quality 项、新处置。

## Fragile

**症状。** 保持行为的重构仍迫使改测试。断言跟踪私有字段、内部名字或协作者调用顺序。

**Quality.** Pin behavior.

**保留当。** 实现选择本身就是契约（从缓存提供、查询走索引）。为该保证命名。

## Change-detector

**症状。** mock 和 `verify` / `assert_called_with`，不断言结果。生产和测试的 diff 形状相同。删掉它不会失去任何输入-输出关系。

**Quality.** Pin behavior. Independent oracle.

**保留当。** 真实边界上的交互（邮件已发、恰好扣费一次）本身就是行为。

## Obscure

**症状。** 一条测试里好几段行为、决定结果的数据在场外、巨大 fixture 只用一角、或隔着无关层驱动被测单元。

**Quality.** One behavior. DAMP.

**保留当。** 真实工作流本身就是单元。篇幅是情景。

## Assertion roulette

**症状。** 许多裸断言；失败只报名行号，不报行为。

**Quality.** One behavior.

**保留当。** 对*同一个*结果的几项属性（解析记录上的 name、age、id）是一条规则。

## Erratic

**症状。** 代码没变却时过时不过：顺序、时序、墙上时钟、未播种的随机、共享文件或行、用 sleep 当等待。

**Quality.** Isolated.

**保留当。** 并发或随机就是被测对象，并且测试控制了它（种子、确定调度）。真实系统测试放在慢套件里。

## Duplication

**症状。** 复制的 setup 或字面量，一次契约变更要改许多测试。

**Quality.** DAMP.

**保留当。** 可读的重复让用例一目了然。

## Wrong thing

**症状。** getter、配置字面量、`class_exists`、框架胶水、已被真实调用方锻炼过的工具函数、为推覆盖率而加的测试。

**Quality.** Load-bearing. Coverage.

**保留当。** 可复用的解析器、日期规则或校验函数有可能写错的可枚举情形。监管限额 pin 的是它所保护的行为。
