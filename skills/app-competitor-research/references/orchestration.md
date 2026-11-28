# 协调执行方

本文件讲执行方是 Codex、由主导方在 Herdr（herdr-core，命令 `hc`）里启动的情况。`hc` 的用法以 `hc --skill` 为准，开工前读一遍。执行方是 subagent 时，把任务书原文作为它的 prompt；阻塞处理、交接、切换设备、测试服务几节照样适用。

主导方要运行在 herdr-core 的终端里（`$HC_TERMINAL_ID` 已设置），它启动的执行方终端才是它的子终端。开工检查时在调研仓库里开一个试探终端：`hc run --bg --name codex-probe --cwd <调研仓库> codex --no-daemon`，`hc read codex-probe --lines 0` 看屏幕；出现目录信任这类启动弹窗时问用户。确认 `hc get codex-probe` 里出现了状态，再 `hc kill codex-probe`、`hc rm codex-probe`。一直没有状态时，等待对它无效，不能当执行方，告诉用户。Codex 必须带 `--no-daemon`，否则它执行的命令跑在 hc 之外。

执行方要在 Herdr 窗口里让用户看得到：从 `hc get "$HC_TERMINAL_ID"` 的 labels 读出主导方所在的 `herdr.space`，再给执行方定一个新的标签页 ID（`tb` 加 32 位十六进制，如 `tb$(openssl rand -hex 16)`），整个调研都用这一个。

## 派任务和终端

- **一个模块一个终端**：每次派单（R1、每个 R2 模块或小节、第二台设备对照、整理）都启动一个新的执行方终端，任务随启动一起给出：

  ```bash
  hc run --bg --name <终端名> --cwd <调研仓库> --outlive-parent --label herdr.space=<主导方的 space> --label herdr.tab=<执行方的标签页 ID> codex --no-daemon "<一句话：轮次、当前设备、读取哪份任务书>"
  ```

  终端名用 `r1`、`r2-import`、`r2-reader-1`、`tidy` 这类名字（小写字母、数字、`-`、`_`，最多 32 个字符）。进度靠文件延续（任务书、事实文件、notes.md），不依赖上下文记忆。两个标签让执行方显示在窗口的独立标签页里，`--bg` 只是让命令立即返回。不要先启动空的 Codex 再发任务，启动中的 Agent 可能丢掉输入。`--outlive-parent` 让主导方的会话意外退出时，执行方和它正在做的测试不跟着结束。
- **确认已开工**：启动后 `hc get <终端名>` 一直没有状态时，先 `hc read <终端名>` 看屏幕，多半停在启动弹窗上，按[阻塞处理](#阻塞处理)办。报错的发送也可能已经送达，先读再决定是否重发。
- **等待**：派完后继续做不依赖它的事；无事可做时运行 `hc wait --children any`。执行方一轮结束、`blocked`、`error` 或退出时它返回，用户给你发消息时也返回。返回 `timeout` 只是例行回报，接着等，不要用 sleep 或轮询代替。
- **读结果**：返回后先 `hc get <终端名>` 看状态，再 `hc read <终端名> --lines 40` 读回复。`done` 表示这一轮结束，读回复判断是完成还是在提问；`blocked` 表示它在等人处理，见[阻塞处理](#阻塞处理)；`error` 先读屏幕找原因；屏幕显示 `429` 或额度用完的提示时，见[中断与交接](#中断与交接)。
- **同一模块内续接**：审核要求补测、回答执行方的提问，都用 `hc send <终端名> "<指令>"` 发给这个模块的终端，再照上面等待。模块审核通过后 `hc kill <终端名>`、`hc rm <终端名>` 关掉它。只清理自己启动的终端：`hc ls` 里还有用户的其他工作。
- **主导方会话恢复后**：上下文被压缩或会话恢复时，先用 `hc ls` 和 `hc get <终端名>` 核对执行方的实际状态，再发消息。主导方换到了新终端时，原来的执行方不再是它的子终端，改用 `hc wait <终端名>` 等待。

## 阻塞处理

`hc get` 显示 `blocked` 时（通常 `kind` 是 `permission`，即 Codex 的权限确认框），`hc send` 会拒绝发送。读屏幕，把弹窗原文和选项转给用户，由用户决定；不要用 `send --force` 绕过权限决定。

执行方在回复里提问时，直接 `hc send` 回答。它停在选项界面上、需要回答选项以外的内容时，先 `hc interrupt <终端名>` 中断当前回合，再用 `hc send` 发一条新指令说明怎么处理、怎么继续，上下文不受影响。

下表是执行方在设备和环境上遇到的阻塞：

| 阻塞 | 处理 |
|---|---|
| 系统权限弹窗 | 按任务书里的权限策略处理；首次遇到时补进 r2-common.md |
| 设备锁屏（`wda status` 显示 `LOCKED`，或报错末尾带 `device LOCKED`） | 只能用户解锁。用户不在时，让执行方把剩下的项写进 untested.md 后收尾，不再操作设备 |
| WDA 连不上且自动恢复失败 | 主导方按 ios-wda 的故障表处理；需要用户插线、信任或重新签名时，记进 user-followups.md |
| App 内部的密码或 PIN 设置页 | 执行方点关闭；要不要设测试密码，记进 user-followups.md 等用户决定 |
| 需要服务器或账号 | 主导方搭本地服务，或者记进 user-followups.md |

## 中断与交接

额度用尽（429）时：
1. 执行方的终端保持不关。按用户指定的间隔设后台计时器（比如 `sleep 7200`，后台运行），时间到了用 `hc send <终端名>` 发一条短指令，试探执行方能不能回复；用户说额度已经重置时，直接撤掉计时器。
2. 空档期间主导方可以用 `wda` 操作设备，比如做校准、复核。操作前，先 `wda shot` 保存中断时的界面作为证据，写 `_process/handoff-<模块>.md`：中断时的界面、已完成和未完成的检查项、主导方改了哪些状态（进度、设置、WDA 配置）。
3. 恢复时用 `hc send <终端名>` 让执行方先读交接说明，再继续原来的任务书；原来的终端已经退出时，按[派任务和终端](#派任务和终端)启动一个新终端，派单指令里写明先读交接说明。

## 切换设备

同一时间只连一台设备做测试。换到另一台设备时：
1. 等执行方这一轮结束（需要提前停时用 `hc interrupt <终端名>`），主导方运行 `wda stop`。
2. 运行 `wda setup --udid <新设备的 UDID>`（UDID 用 `wda devices` 查），再运行 `wda start`。第一次在新设备上安装时，可能要用户去"VPN 与设备管理"里信任开发者。
3. 用 `wda status` 确认型号、锁屏状态和前台 App 后，再派任务；派单指令里写明当前设备。

两台设备要同时保持可用时，按 ios-wda 的说明给每台设备单独设 `WDA_HOME` 和端口，并在任务书里写明执行方要带哪个 `WDA_HOME`。

## 本地测试服务

服务器或网络源类的功能，在 Mac 上搭一个本地服务，内容就用测试素材。设备需要先授予 App 本地网络权限。

- WebDAV（端口 8090，用户名 test，密码 test1234）和 HTTP 直链（端口 8091）：`hc run --bg --no-parent --name sources research/tools/serve_sources.sh <素材目录>`。`--no-parent` 让它不算主导方的子终端，不干扰 `hc wait --children any`。
- Komga：用 Apple container 运行：

  ```bash
  container run -d --name <名称> -m 4G -c 4 -e JAVA_TOOL_OPTIONS=-Xmx3g -p 0.0.0.0:25600:25600 -v /tmp/komga-config:/config -v <素材目录>:/data gotson/komga:latest
  ```

  约 1 分钟后可用。先 `POST /api/v1/claim`（请求头带 X-Komga-Email、X-Komga-Password）创建管理员，再 `POST /api/v1/libraries` 建书库。派任务前，用 `GET /api/v1/books?size=200` 确认每本书的 `media.status` 都是 READY（故意损坏的素材是 ERROR）。默认 2GB 内存下，超大图生成缩略图时会内存溢出，后台任务卡死，后面的书一直是 UNKNOWN；执行方会把这种环境故障当成 App 的行为记录下来。
- 在 Mac 上用 curl 验证局域网地址时加 `--noproxy '*'`：本机有代理环境变量时，不加会返回代理的 503。
- SMB 需要在 Mac 的系统设置里配置共享，由用户决定。
- 调研结束时清理：停掉并删除容器，`hc kill sources`、`hc rm sources` 结束服务，删除临时配置目录。
