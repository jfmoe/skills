---
name: app-competitor-research
description: 在真机上做 iOS/iPadOS App 的竞品调研，产出客观、可追溯的事实记录：新竞品、续测或补测、加一台设备。
disable-model-invocation: true
---

# 真机竞品调研

调研产物只记录竞品**是什么、怎么表现**：界面原文、操作结果、测量值，每条都有来源和证据。评价、建议和取舍不写进产物；分析另外进行，并通过编号引用这里的事实。

分工：

- **主导方**（加载本技能的 agent）：负责规划、开工检查、R0 准备、编写任务书、派任务、审核、处理阻塞、和用户沟通。
- **执行方**：加载 `ios-wda` 技能，按任务书操作真机，写事实文件。通常是 Herdr 面板里的 Codex，也可以是 subagent 或主导方自己。

设备操作只走 `ios-wda`：读控件树、点击、各种手势、密码框输入、转屏、截图、录屏都由它完成。下文的 `wda` 指 ios-wda 技能里的命令。

主导方只在执行方停下的空档里操作设备，并且要先写交接说明（见[协调执行方](references/orchestration.md#中断与交接)）。

## 产物结构

```text
research/
├── README.md               # 调研对象表和记录规范（记录规范从 references/conventions.md 落地）
├── tools/                  # 从本技能 scripts/ 复制，执行方通过这里调用
├── test-materials/         # 素材生成脚本、清单；out/ 是实际使用的素材（LFS），不重新生成覆盖
├── _process/               # 过程材料，第一轮结束、提炼经验后删除
│   ├── briefs/             # 派给执行方的任务书原文
│   ├── notes.md            # 工具观察、卡点、审核意见
│   └── user-followups.md   # 待用户确认或配合的事项
└── <app>/
    ├── README.md           # 概况、环境、覆盖情况、测试数据现状
    ├── INDEX.md            # 事实索引（脚本生成），读事实的入口
    ├── app-store.md, app-store-reviews.md, official.md
    ├── screens.md, settings.md
    ├── features/<模块>.md
    ├── untested.md
    ├── screenshots/<iphone|ipad|app-store>/<前缀>/   # Git LFS；index.md 为生成的证据索引
    ├── recordings/         # 动效录像（LFS）
    └── sources/            # 商店原始响应
```

事实格式、编号前缀、证据命名、设备维度见[记录规范](references/conventions.md)。新建调研时，把它落地成 `research/README.md`。

## 流程

### 0. 开工检查

跟用户确认以下事项，没确认的不开工：
- 调研哪个 App，用哪些设备；
- App 里已有的数据要不要保护；
- 系统权限怎么处理：本地网络通常允许，其他权限记录弹窗原文后选不授予；
- 不付款、不登录第三方账号。

设备和工具逐项核对：
- 每台设备：自动锁定设为"永不"，接上电源，已解锁，App 已安装；
- `wda status` 输出 `ready`、`unlocked`，设备型号正确；
- 执行方能加载 `ios-wda` 技能；执行方是 Codex 时，Herdr 里能找到它的面板，状态是 idle；
- 记下执行方的额度剩余，额度少时提前告知用户。

**完成标准**：以上每一项都有明确结论。用户需要做的事，一次性列给用户。

### 1. R0 准备（主导方）

`research/` 里已经有别的竞品时，`README.md`、`test-materials/`、测试服务直接复用，素材也沿用同一套，同一个检查项在不同竞品之间才能横向对比。这时只做：用本技能的 `scripts/` 更新 `research/tools/`，用 `references/conventions.md` 更新 `research/README.md` 的记录规范，在 `research/README.md` 的调研对象表里加一行，新建 `<app>/`，再做第 2、3、6 步；第 5 步只在新 App 的导入路径没验证过时做。

1. 复制本技能的 `scripts/` 到 `research/tools/`；用 Git LFS 跟踪截图（见[记录规范](references/conventions.md#证据)）。
2. 抓取商店信息：`python3 -I research/tools/app_store_snapshot.py <bundle-id> research/<app>`。它会生成商店信息、版本历史、内购、隐私标签、评论原文，以及商店截图。
3. 抓取官网和条款：网站是前端渲染的，用 forager fetch 读取，写成 `official.md`（前缀 OF）。
4. 准备测试素材：素材要有已知内容，每页印上页码、尺寸、边缘色带等标记，看截图就能客观判断显示结果。漫画和图片阅读类用 `generate_comic_materials.py`；其他品类按同样思路另写生成器。
5. 把素材送上设备。优先用 App 自带的 Wi-Fi 传输或网页上传，在 Mac 上用 curl 上传即可。iCloud Drive 单个文件可以，批量导入实测会报 NSFileProvider 错误。iCloud 里的素材文件夹用通用名字（比如"调研测试素材"），不带竞品名，下一个竞品可以接着用。
6. App 有服务器或网络源时，在 Mac 上搭本地测试服务，见[协调执行方](references/orchestration.md#本地测试服务)。

**完成标准**：商店、官网文件已经生成；素材清单已经提交；素材至少有一条已验证的上传路径。

### 2. R1 广度遍历（执行方）

在主设备上走遍所有可达页面，产出 `screens.md`（页面层级树加 SC 条目）、`settings.md`（选项全集和默认值），这一轮不深测行为。第二台设备不重新遍历，只做对照：逐个 SC 编号标出一致、有差异或未找到，独有的内容追加为新条目，横屏和竖屏都看一遍。任务书模板见[任务书](references/briefs.md#r1-广度遍历)。

**完成标准**：主设备上每个可达入口都有 SC 条目，进不去的写进 `untested.md`；有第二台设备时，每个 SC 编号都有对照结论。

### 3. R2 按模块深测（执行方）

顺序：导入（先把素材装进 App）→ 核心模块 → 书库 → 付费 → 服务器和网络源 → 其他。核心模块是这类 App 的价值所在，比如阅读器、编辑器、播放器，要按小节拆成 2～3 次任务。每个模块开一次新的执行方会话，任务书由"通用要求 + 模块检查项"组成，见[任务书](references/briefs.md)。动画、加载、惯性这些只能靠录屏测，规程见[动效测量](references/motion.md)。

有第二台设备时，每个模块在主设备上测完、审核通过后，紧接着在第二台设备上复核，不要攒到全部模块做完再一起复核：设备可能中途就用不了了。复核任务书见[任务书](references/briefs.md#r2-第二台设备复核)。

**完成标准**：任务书里每个检查项都有对应的事实，或者在 `untested.md` 里写了原因；有第二台设备时，本模块的事实都有复核结论。

### 4. 审核（主导方，每个模块完成后）

逐项核对：
- [ ] 抽查至少 3 条关键事实：按编号找到截图或关键帧，确认图片内容和事实、文件名一致。
- [ ] 测量值写明了录屏方式、精度，以及是否包含人为动作（比如"包含拖动 400ms"）。
- [ ] 没有评价词，证据边界写清了"不能据此……"。
- [ ] 改过的设置已经恢复，或者写明了现状。
- [ ] `untested.md` 已更新：新缺口按需要的配合分组写入；被本模块补上的旧缺口已删掉，或者缩成剩下的部分。
- [ ] 格式符合记录规范：表格五列、口径写在文件开头、同构的结果合并成矩阵表；`build_indexes.py` 已重新运行。
- [ ] 新内容放在所属的主题位置，没有在文件末尾按轮次另开小节；产物里没有过程措辞（见[文件组织](references/conventions.md#文件组织)）。
- [ ] 遗漏的检查项，加进下一段任务书开头的"0. 补测"小节。

小问题主导方直接改，比如措辞、文件名，并在 `notes.md` 记一笔；需要重新测的，派回执行方。

### 5. 第一轮收尾

1. 按[文件组织](references/conventions.md#文件组织)通查产物：重写 `<app>/README.md` 的四节；把 `_process/user-followups.md` 里与 App 测试有关的事项并进 `untested.md`；`untested.md` 里只留现在仍然存在的缺口。
2. 把 `untested.md` 里"需要用户操作""需要用户授权或提供资源"两组，连同 user-followups 里与仓库、设备有关的事项，一次性交给用户。在 `research/README.md` 的调研对象表里更新状态。
3. 从 `notes.md` 提炼对本技能的改进，更新本技能。
4. 清理测试服务，删除 `_process/`。

**完成标准**：`untested.md` 只剩现在仍然存在的缺口；需要用户处理的事项已经交给用户；本技能已更新；`_process/` 已删除，产物已提交。

## 参考

- [记录规范](references/conventions.md)：客观性、事实表格、文件组织与措辞、设备维度、证据。
- [任务书](references/briefs.md)：R1、第二台设备对照与复核、R2 通用要求、各模块检查项。
- [协调执行方](references/orchestration.md)：Herdr 指令、会话管理、阻塞处理、额度用尽、切换设备、本地测试服务。
- [动效测量](references/motion.md)：录屏工具、精度与限制、测量规程、措辞。
