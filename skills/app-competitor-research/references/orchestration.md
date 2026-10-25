# 协调执行方

执行方是 Herdr 面板里的 Codex。先运行 `herdr agent list`，找到 agent 是 codex、cwd 是调研仓库的那个面板，记下它的 pane ID。Herdr 的完整用法见 herdr 技能。

## 派任务和会话

- 每个模块开一次新会话：`herdr agent prompt <pane> "/new"`。会弹出 worktree 选择框，`herdr agent send-keys <pane> enter` 选"当前目录"。进度靠文件延续（任务书、事实文件、notes.md），不依赖会话记忆。
- 派单要放后台等待：`herdr agent prompt <pane> "<一句话：轮次、当前设备、读取哪份任务书>" --wait --timeout 10800000`，用 Bash 的后台模式运行，完成时会收到通知。
- 派出约 15 秒后，用 `herdr agent get <pane>` 确认状态是 `working`。
- 返回时先看状态，再用 `herdr agent read <pane> --source recent-unwrapped --lines 40` 读回复。`done` 表示完成；`blocked` 表示它在等人回答；`idle` 并且显示 `429` 表示额度用完了。

## 阻塞处理

执行方停下来提问时，选项界面里没法回答自定义内容。做法：先 `send-keys <pane> esc` 中断当前回合，再用 `agent prompt` 发一条新指令说明怎么处理、怎么继续。上下文不受影响。

| 阻塞 | 处理 |
|---|---|
| 系统权限弹窗 | 按任务书里的权限策略处理；首次遇到时补进 r2-common.md |
| 设备锁屏 `phone_locked` | 只能用户解锁。用户不在时，让执行方把剩下的项写进 untested.md 后收尾，不再操作设备 |
| App 内部的密码或 PIN 设置页 | 主导方用 `wda.py` 点关闭；要不要设测试密码，记进 user-followups.md 等用户决定 |
| PUA 拒绝输入安全密码框（`not_editable: secure_field`） | 只用于任务书给出的测试服务密码：先点密码框获得焦点，再 `wda.py post /wda/keys '{"value":["t","e",...]}'`，用 `post /elements '{"using":"class name","value":"XCUIElementTypeSecureTextField"}'` 核对圆点数。截图里不显示圆点属正常。写进 r2-common.md，执行方可自行处理 |
| 需要服务器或账号 | 主导方搭本地服务，或者记进 user-followups.md |

## 中断与交接

额度用尽（429）时：
1. 按用户指定的间隔设后台计时器（比如 `sleep 7200`，后台运行），时间到了先发一条短指令试探执行方能不能回复；用户说额度已经重置时，直接撤掉计时器。
2. 空档期间主导方可以操作设备，比如做校准、复核。操作前，先截图保存中断时的界面作为证据，写 `_process/handoff-<模块>.md`：中断时的界面、已完成和未完成的检查项、主导方改了哪些状态（进度、设置、WDA 配置）。
3. 恢复时让执行方先读交接说明，再继续原来的任务书。

## WDA 直连

iPhone Use 的 PUA 工具没有长按、双击、捏合、转屏，可以用 `research/tools/wda.py` 直接调用 WDA：

```bash
python3 -I research/tools/wda.py post /wda/touchAndHold '{"x":90,"y":240,"duration":1}'
python3 -I research/tools/wda.py post /wda/doubleTap '{"x":683,"y":512}'
python3 -I research/tools/wda.py post /orientation '{"orientation":"PORTRAIT"}'
python3 -I research/tools/wda.py post /actions '{"actions":[<两条 touch pointer：pointerMove → pointerDown → pause 100 → pointerMove 600ms → pointerUp>]}'
python3 -I research/tools/wda.py shot /tmp/now.png
```

- 坐标单位是设备的点，不是截图像素。`touchAndHold` 的 duration 单位是秒，W3C actions 的单位是毫秒。
- 脚本会持有和 PUA 相同的操作锁，锁被占用时直接失败，不会和 PUA 抢设备。
- 接口返回成功不代表手势生效，每次都要看下一张截图。
- 没有执行方会话时，可以用插件的命令行入口管理服务：`python3 ~/.codex/plugins/cache/iphone-use-local/iphone-use/<版本>/scripts/phone.py pua_setup '{"action":"start"}'`，然后执行 `pua_ready '{"recover":true,"screenshot":false}'`。WDA 断开后这样重启，App 的状态不受影响。

## 本地测试服务

服务器或网络源类的功能，在 Mac 上搭一个本地服务，内容就用测试素材。设备需要先授予 App 本地网络权限。

- WebDAV（端口 8090，用户名 test，密码 test1234）和 HTTP 直链（端口 8091）：`research/tools/serve_sources.sh <素材目录>`，用 Bash 的后台模式运行。
- Komga：用 Apple container 运行：

  ```bash
  container run -d --name <名称> -p 0.0.0.0:25600:25600 -v /tmp/komga-config:/config -v <素材目录>:/data gotson/komga:latest
  ```

  约 1 分钟后可用。先 `POST /api/v1/claim`（请求头带 X-Komga-Email、X-Komga-Password）创建管理员，再 `POST /api/v1/libraries` 建书库。
- 在 Mac 上用 curl 验证局域网地址时加 `--noproxy '*'`：本机有代理环境变量时，不加会返回代理的 503。
- SMB 需要在 Mac 的系统设置里配置共享，由用户决定。
- 调研结束时清理：停掉并删除容器，结束服务进程，删除临时配置目录。
