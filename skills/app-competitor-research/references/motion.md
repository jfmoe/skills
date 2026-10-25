# 动效测量

截图只能看到静态结果。动画、惯性、回弹、加载过程中有没有空白，要录屏后逐帧分析。

## 工具

| 方式 | 命令 | 精度 | 限制 |
|---|---|---|---|
| WDA MJPEG（默认） | `python3 -I research/tools/record_mjpeg.py <秒> <out.mp4>` | 约 20fps，每帧约 50ms，局部 40～120ms | 瓶颈在设备端截屏，调缩放比例也不能提速；不影响操作通道 |
| USB 屏幕采集 | 先 `swiftc -O research/tools/record_device.swift -o /tmp/record_device`，再 `/tmp/record_device record <设备名片段> <秒> <out.mov>` | 约 59fps，每帧约 17ms | 开始录制后约 20 秒，WDA 的 XCTest 连接会断开，需要重启服务。单次录制不超过 10 秒，只在需要精确比较时用 |

分析：`uv run --with numpy python -I research/tools/analyze_motion.py <录像> --frames <目录> [--mark <秒>]`。它会输出：
- 运动段：开始时间、结束时间、时长、帧数；
- 空白帧：几乎没有细节的纯色帧；
- 关键帧：每个运动段的 start、mid、end 三张。

USB 采集需要通过 CoreMediaIO 开启屏幕采集设备，`startRunning` 之后等约 2 秒再录，脚本已经处理好了。终端第一次使用时可能要授予摄像头权限。

## 规程

1. 在后台启动录屏，等 2～3 秒，再用 PUA 或 `wda.py` 执行动作，等录屏结束。
2. 每个测量项重复 3 次，每次的值都写下来。
3. 事实写成"画面从开始变化到静止约 N ms（MJPEG 约 50ms 精度，3 次：a / b / c）"，并写明是否包含人为动作，例如"包含按住 100ms 和拖动 400ms"。点击类动作通常不包含手指动作。
4. 录像放在 `recordings/<前缀>/`（Git LFS 入库），文件名以编号开头；关键帧复制到 screenshots，文件名同样以编号开头；每段的时间戳写进 `<前缀>-measurements.md`，事实里只写结论值。
5. 运动段把手指操作和动画混在一起时，如实写出口径。分析结果不合理时，在 notes.md 里写清楚，不要硬凑。

## 测不了的项

- **点击响应延迟**：`record_mjpeg.py` 会输出 `movie_t0_epoch`，配合 `--mark` 能算出从发出动作到画面变化的时间。但 WDA 合成一次点击就要约 0.5～0.8 秒，远大于 App 自身的耗时，所以只能在同一条件下互相比较，不能写成 App 的响应时间。
- **松手瞬间**：录像里没有触点信息，惯性、回弹的"松手后"时长分不出来。写总时长，并注明包含了拖动。
- **帧率、掉帧、内存、解码耗时**：需要 Instruments 或开发者工具，写进 untested.md。
- **120Hz 细节**：两种录屏都最高 60fps，更细的差异测不出来。

## 交叉验证参考

iPad Pro 12.9（第 5 代），点击翻页（仿真效果）：USB 采集测得 233 / 233 / 267ms，MJPEG 测得 280ms，两者吻合。
