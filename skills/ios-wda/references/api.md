# WDA 接口速查

`wda` 没有封装的接口，可以直接调：
- `wda get <路径>`、`wda post <路径> '<json>'`、`wda delete <路径>`：路径相对于 `/session/<当前会话>`；结果大时加 `--out 文件`；
- 加上 `--root`：路径相对于服务根地址。
- 返回值是字符串时原样输出（比如 base64、XML），其他类型输出 JSON。
- 路径以 `/` 开头。POST 一定要带 JSON 请求体，没有参数时写 `'{}'`。

坐标都用 point，时长的单位见下表各行。适用版本是 appium/WebDriverAgent v16.x，其他版本，或者接口返回 404 时，以本机源码为准：`$WDA_HOME/WebDriverAgent/WebDriverAgentLib/Commands/`（默认 `~/.local/share/ios-wda/...`）。路由带 `.withoutSession` 的才能用 `--root` 调用。

## 会话内（`/session/<id>` 下）

| 方法和路径 | 请求体 | 作用 |
|---|---|---|
| `GET /window/size` | | 窗口尺寸（point），随横竖屏变化 |
| `GET /source?format=xml` | | 完整控件树。`excluded_attributes=visible,accessible` 能明显加快读取 |
| `POST /elements` | `{"using": "...", "value": "..."}` | 查找元素。`using` 可以是 `class name`（如 `XCUIElementTypeSecureTextField`）、`accessibility id`、`predicate string`（如 `label CONTAINS "保存"`）、`class chain` |
| `POST /element/<eid>/click` | `{}` | 点击元素。`<eid>` 取自 `/elements` 返回结果里每一项的 `ELEMENT` 字段 |
| `POST /element/<eid>/value` | `{"text": "..."}` | 先点中元素，再输入 |
| `POST /element/<eid>/clear` | | 清空输入框 |
| `GET /element/<eid>/attribute/<名>` | | 读取 value、label、enabled、hittable 等属性 |
| `POST /actions` | W3C 指针动作，见下文 | 任意手势，可以多指 |
| `POST /wda/tap` | `{"x", "y"}` | 点击 |
| `POST /wda/doubleTap` | `{"x", "y"}` | 双击 |
| `POST /wda/touchAndHold` | `{"x", "y", "duration": 秒}` | 长按 |
| `POST /wda/dragfromtoforduration` | `{"fromX", "fromY", "toX", "toY", "duration": 秒}` | 按住 duration 秒之后再拖动，适合拖放；做快速滑动请用 `/actions` |
| `POST /wda/keys` | `{"value": ["a", "b"]}` | 往当前焦点输入，安全输入框也可以 |
| `GET` / `POST /orientation` | `{"orientation": "PORTRAIT"}` 或 `"LANDSCAPE"` | 读取或设置屏幕方向 |
| `GET /alert/text`、`GET /wda/alert/buttons` | | 系统弹窗的文字和按钮 |
| `POST /alert/accept` | `{"name": "按钮文字"}` | 点系统弹窗上指定的按钮；不带 name 时点默认按钮 |
| `POST /alert/dismiss` | | 点系统弹窗的取消类按钮 |
| `POST /wda/apps/activate` | `{"bundleId"}` | 把 App 切到前台，不重启 |
| `POST /wda/apps/launch` | `{"bundleId", "arguments": [], "environment": {}}` | 冷启动 App |
| `POST /wda/apps/terminate` | `{"bundleId"}` | 结束 App |
| `POST /wda/apps/state` | `{"bundleId"}` | 1 = 未运行，2 = 后台挂起，3 = 后台运行，4 = 前台 |
| `POST /url` | `{"url": "..."}` | 打开 URL 或 deep link |
| `GET` / `POST /appium/settings` | `{"settings": {...}}` | 会话设置，见下文 |
| `POST /wda/setPasteboard` | `{"content": "<base64>", "contentType": "plaintext"}` | 写入剪贴板 |
| `POST /wda/getPasteboard` | `{"contentType": "plaintext"}` | 读取剪贴板，返回 base64。实测 iPadOS 27 上 WDA 不在前台时返回空：iOS 限制后台读取剪贴板 |
| `POST /wda/pressButton` | `{"name": "home"}` | 按物理按键：`home`、`volumeUp`、`volumeDown`，有操作按钮的机型还有 `action`。只有会话内路径，加 `--root` 会返回 404 |
| `GET /wda/device/info`、`GET /wda/batteryInfo` | | 设备信息（`name` 是脱敏后的值）、电量 |

## 根路径（加 `--root`）

| 方法和路径 | 作用 |
|---|---|
| `GET /status` | 服务是否就绪、WDA 版本、系统版本、当前会话 ID |
| `GET /screenshot` | base64 编码的 PNG，像素尺寸 = point × 屏幕倍数 |
| `GET /wda/activeAppInfo` | 前台 App 的 bundleId、pid |
| `GET /wda/locked`、`POST /wda/lock`、`POST /wda/unlock` | 查询锁屏状态、锁屏、解锁。设置了锁屏密码的设备，unlock 只能点亮屏幕 |
| `POST /wda/homescreen` | 回到主屏幕 |

## W3C 手势

```json
{"actions": [{"type": "pointer", "id": "f0", "parameters": {"pointerType": "touch"}, "actions": [
  {"type": "pointerMove", "duration": 0, "x": 600, "y": 500},
  {"type": "pointerDown", "button": 0},
  {"type": "pause", "duration": 100},
  {"type": "pointerMove", "duration": 250, "x": 200, "y": 500},
  {"type": "pointerUp", "button": 0}]}]}
```

- `duration` 的单位是毫秒。
- 多指手势就在 `actions` 数组里多放几个 pointer，id 各不相同，它们会同时执行。捏合就是两指从中心向外或向内移动。
- 惯性滑动要用短时长、长距离，比如 100ms 内移动 400pt；想让内容停在原地不惯性滚动，就在松手前加一个 pause。

## 常用设置

| 键 | 作用 |
|---|---|
| `snapshotMaxDepth` | 控件树最大深度。默认值较小，深层元素会被截掉，建议设成 50 |
| `waitForIdleTimeout`、`animationCoolOffTimeout` | 动作前等待 App 空闲、等待动画结束的时长。设为 0，动作立即执行 |
| `mjpegServerFramerate`、`mjpegScalingFactor`、`mjpegServerScreenshotQuality` | MJPEG 流的帧率上限、缩放百分比、JPEG 质量 |
| `screenshotQuality` | `/screenshot` 的压缩档位 |
| `maxTypingFrequency` | 输入速度，单位是每分钟字符数 |
| `defaultAlertAction` | 设成 `accept` 或 `dismiss`，系统弹窗会被自动处理。需要亲自查看或处理弹窗时不要设置 |
