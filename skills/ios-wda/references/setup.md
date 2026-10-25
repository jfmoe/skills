# 首次配置与故障

## 首次配置

每台 Mac 做一次；以后换设备，从第 3 步开始。

1. **Mac（用户操作）**：
   - 需要 git（`setup` 用）和 ffmpeg（`record` 用）。`wda doctor` 会检查这两项。
   - 安装完整的 Xcode，启动一次，接受许可协议。只装 Command Line Tools 不够。
   - 在 Xcode → Settings → Accounts 里登录 Apple 账户，免费的 Personal Team 就够用。
   - 登录、密码、验证码都由用户本人完成。
2. **设备（用户操作）**：
   - 用数据线连接 Mac，解锁，点"信任此电脑"。
   - 打开"设置 → 隐私与安全性 → 开发者模式"，按提示重启并确认。找不到这个入口时，先在 Xcode 的 Devices and Simulators 里完成设备配对。
   - "设置 → 开发者"里如果有"启用 UI 自动化"，把它打开。
   - 需要长时间操作时，把"设置 → 显示与亮度 → 自动锁定"设为"永不"，并接上电源。
3. **确认设备**：运行 `wda devices`。目标设备那一行要显示 `connected` 和 `devmode=enabled`，并记下第二列的 UDID。
4. **确认团队**：运行 `wda teams`，它从本机的开发证书里读出 Team ID。如果没有输出，说明 Mac 上还没有开发证书：`setup` 用了 `-allowProvisioningUpdates`，通常会自动申请证书；申请失败的话，让用户在 Xcode 的 Accounts → Manage Certificates 里手动新建一张。
5. **构建**：
   ```
   wda setup --udid <UDID> --team <TEAM_ID> --bundle-id com.<你的标识>.WebDriverAgentRunner
   ```
   运行时设备要保持连接并解锁。这条命令会先保存配置，再从 GitHub 浅克隆固定 tag 的 `appium/WebDriverAgent`（默认 tag 写在脚本的 `DEFAULT_REF` 里），最后构建并签名。在 M 系列 Mac 上大约 20 秒。它可以重复运行，已经保存的参数下次不用再写。
   - bundle ID 必须是用户自己的团队能签名的，不要照搬别人的。
   - 免费团队在一台设备上最多装 3 个开发 App。如果设备上已经装过别的 WDA，沿用它的 bundle ID，就不会多占一个名额。
   - 本机端口默认是 8100 和 9100。被占用时，加上 `--port`、`--mjpeg-port` 换成别的端口。
6. **启动**：运行 `wda start`。第一次安装后，设备可能提示开发者不受信任：让用户进入"设置 → 通用 → VPN 与设备管理"，点开自己的开发者条目并选择信任（这一步设备要联网），然后再运行一次 `start`。
7. **验收**：`wda status` 输出 `ready`；再运行 `wda shot` 截图，用 Read 查看，确认截到的就是设备当前的画面。

## 日常维护

- **免费团队 7 天过期**：免费团队的描述文件 7 天后过期，runner 会启动失败。重新运行 `wda setup`，再 `wda start`。
- **换设备**：运行 `wda setup --udid <新设备的 UDID>`，再 `wda start`。
- **同时操作两台设备**：每台设备用一个单独的 `WDA_HOME` 和一组不同的端口。之后每次调用 `wda` 都带上对应的 `WDA_HOME`。
- **升级 WDA**：运行 `wda setup --ref vX.Y.Z`。可用的 tag 用 `git ls-remote --tags https://github.com/appium/WebDriverAgent.git` 查。

## 故障表

先看 `wda doctor` 的输出，再看 `~/.local/share/ios-wda/logs/` 下的 `runner.log`、`build.log`、`forward.log`。

| 现象 | 原因 | 处理 |
|---|---|---|
| doctor 显示 `usb: not visible`，或 devices 显示 `unavailable` | 没插线、设备锁屏太久进入了休眠，或者设备还没信任这台 Mac | 让用户插线、解锁、点信任，然后运行 `start` |
| `start` 或自动恢复时报 `runner not ready (runner exited)` | runner 启动后又退出了 | 看报错里附带的日志末尾，按下面几行处理 |
| `start` 或自动恢复时报 `runner not ready (runner still running but not serving)` | xcodebuild 进程还在，但服务一直没起来，常见于设备锁屏或者在等信任 | 让用户解锁，并看设备上有没有弹窗，然后 `stop` 再 `start`。也可以用 `start --timeout 300` 多等一会儿 |
| `start` 或自动恢复时报 `forward exited` | 本机端口被占用，或者 usbmuxd 不可用 | 报错里会附上 forward.log。端口冲突就用 `setup --port N --mjpeg-port M` 换端口；不要杀掉不知道是谁的进程 |
| doctor 显示 `runner started elsewhere` | 设备上的 WDA 是别的工具或者之前的会话启动的 | 可以直接用。只是 `stop` 停不掉它；需要换成本技能的构建时，先停掉原来启动它的程序 |
| `runner.log` 末尾是 `TEST EXECUTE FAILED` | 设备锁屏了；或者另一个 xcodebuild 测试进程抢占了 XCTest | 先运行 `status`：如果已经有可用的服务，直接用。否则让用户解锁，然后运行 `start` |
| 用 AVFoundation 做 USB 屏幕采集，约 20 秒后 WDA 断开 | USB 屏幕采集会切换设备的 USB 配置，XCTest 连接因此中断 | 改用 `wda record`。确实需要 60fps 时，每次只录 10 秒以内，录完运行 `start` |
| 报 `Not authorized for performing UI testing actions` 或 `XCTDaemonErrorDomain Code=41` | 没开 UI 自动化，或者设备处于锁屏状态 | 让用户打开"启用 UI 自动化"并解锁设备，然后运行 `stop`，再运行 `start` |
| 报 `requires a development team` 或 `No Account for Team` | Xcode 里没有登录账户，或者 Team ID 填错了 | 让用户在 Xcode 里登录；用 `teams` 核对 Team ID |
| 报 `maximum number of apps for free development profiles` | 免费团队在这台设备上已经装满 3 个开发 App | 由用户决定删掉哪一个；或者沿用设备上已有 WDA 的 bundle ID |
| 报 `bundle identifier cannot be registered` | 这个 bundle ID 已经被别的团队注册了 | 换成自己的 bundle ID |
| 设备提示开发者不受信任或无法验证 | 这是第一次装这个开发者签名的 App | 在"VPN 与设备管理"里信任这个开发者，操作时设备要联网 |
| 用了约 7 天后突然无法启动 | 免费团队的描述文件过期了 | 运行 `setup`，再运行 `start` |
| 报 device support 或平台版本不匹配 | Xcode 版本比设备上的 iOS 旧 | 升级 Xcode |
| 接口返回 404 或 `unknown command` | 不同版本的 WDA 接口有差异 | `status` 里能看到 WDA 版本号，对照这个版本的源码确认接口 |
| 控件树为空，截图显示"正在从 Mac 使用此 iPhone" | Mac 的 iPhone 镜像正在占用设备 | 退出 iPhone 镜像，然后解锁设备 |
