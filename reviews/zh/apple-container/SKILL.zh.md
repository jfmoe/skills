---
name: apple-container
description: '用于 Apple Container CLI 的设置、操作、故障排查、macOS 上的 Docker 迁移，或基于 launchd 的容器编排。'
---

# Apple Container CLI

使用已安装的 CLI 及其对应版本的官方文档，操作 Apple 在 macOS 上提供的 Linux 容器。依赖版本的命令语法、平台要求和功能可用性，以这些来源为准。

## 确认环境

1. 运行 `command -v container`、`container --version`、`sw_vers` 和 `uname -m`。如果尚未安装 CLI，先核查官方安装要求，再通过用户偏好的包管理器安装。
2. 阅读 `container --help` 及相关子命令的 `--help`。可用命令和参数以本机帮助为准，行为和限制查阅对应发布版本的文档。
3. 对于依赖服务的操作，检查 `container system status`。按需启动服务，保留启动错误以便诊断。

确认已安装版本、宿主机兼容性及所需命令支持后继续。如果本机帮助与文档冲突，说明差异，并在依赖该操作前验证其行为。

## 查找对应版本的参考资料

从[官方仓库](https://github.com/apple/container)和[发布页面](https://github.com/apple/container/releases)开始。选择与 `container --version` 对应的标签，再打开下列相关文件。这些路径均相对于所选标签；`main` 可能描述尚未发布的行为。如果路径发生变化，在所选版本的目录树中查找替代文件。开发版本有提交号时使用对应提交，并说明剩余的不确定性。

| 任务 | 所选标签中的官方来源 |
| --- | --- |
| 安装与宿主机要求 | `README.md` |
| 命令语法 | `docs/command-reference.md` |
| 系统默认值与配置 | `docs/container-system-config.md` |
| DNS、端口与自定义网络 | `docs/networking.md` |
| 宿主机服务与 SSH 转发 | `docs/host-integration.md` |
| 架构选择与 Rosetta | `docs/multiplatform-images.md` |
| 持久化存储 | `docs/volumes.md` |
| 长期运行的 Linux 虚拟机 | `docs/container-machine.md` |
| Kubernetes，本机帮助提供该入口时 | `docs/kubernetes.md` |

只阅读任务所需的参考资料。升级或调查行为变化时，核查发布说明。

## 初始化与配置

- 编写首次启动脚本前，检查 `container system start --help`。启动过程可以提示安装内核；支持时，`container system start --enable-kernel-install` 可在无需交互提示的情况下安装缺失的内核。显式安装或更新内核时使用 `container system kernel set --recommended`，无需每次启动后重复执行。
- 修改配置前先读取现有内容。对于使用 TOML 的版本，编辑 `~/.config/container/config.toml` 中的相关键，保留无关配置节。合并到已有表中；盲目追加另一个 `[dns]` 表会导致文件无效。
- 按文档规定的生命周期应用配置。必须重启服务时，先检查正在运行的工作负载并考虑中断影响。支持时，通过 `container system property list` 验证生效值。

服务健康且所需工作负载成功启动后，初始化才算完成；仅成功写入配置还不够。

## 网络

分别处理每条通信路径：

- **Mac 到容器：** 使用发布端口或可达的容器 IP。如需 DNS 名称，按对应版本的网络指南配置服务的 DNS 域和 Mac 的解析器。
- **容器到容器：** 核查网络归属，并从发起调用的容器内测试解析。使用 `[dns] domain` 的版本通过该配置注册完整域名；`container system dns create <domain>` 配置 Mac 的解析器。二者服务于不同的调用方。
- **容器到 Mac：** 查阅宿主机集成指南。如果使用 `container system dns create --localhost`，在修改宿主机网络前核查文档中关于包过滤、重启和 Private Relay 的影响。

全新本地 DNS 设置应统一使用指南中的示例域，例如 `test`。除非任务要求变更，否则保留已有且正常工作的域。使用 TOML 配置时，合并以下内容：

```toml
[dns]
domain = "test"
```

按对应指南应用配置；需要宿主机名称解析时，通过 `sudo container system dns create test` 配置宿主机解析器。

不要假设自定义网络支持 Docker Compose 式的裸服务名解析。检查该版本的网络限制。在支持的网络上使用文档规定的完整域名，或检查目标容器在共享网络上的 IP。以 JSON 解析 `container inspect`，选择目标网络，不要假设第一个地址就是所需地址。重建容器后重新检查地址。

只有预期调用方能解析或寻址目标，并访问其应用端口后，才算完成网络验证。仅宿主机访问成功不能证明容器间连通。

## Docker 迁移与持久工作负载

- 根据本机帮助逐项转换所需操作。命令名称相似不代表参数、JSON 结构、Docker API 兼容性或生命周期行为相同。对于依赖 Docker socket 的工具，核查其实际集成要求。
- 选择编排方式前，检查当前 Compose 和重启策略支持。如果已安装版本缺少所需行为，使用脚本或 launchd 任务处理服务就绪、依赖、应用健康和持久数据。区分登录时启动与应用崩溃后恢复；单独设置 `RunAtLoad` 不提供崩溃恢复。
- 对于 launchd 任务，通过 `command -v container` 确定可执行文件位置，使用绝对路径或显式 PATH。在任务所属用户的上下文中测试。为就绪检查设置等待上限，并保留失败输出。
- 修改挂载前，检查卷内容及镜像文档规定的数据目录要求。如果 ext4 卷中的 `lost+found` 阻碍初始化，配置受支持的子目录存储应用数据。保留已有数据；数据库已经初始化时，遵循镜像的迁移流程。
- 跨架构执行时显式选择目标镜像架构，例如在支持时使用 `container run --arch amd64 ...` 或 `--platform linux/amd64`。单独核查 Rosetta 要求；`--rosetta` 本身不选择镜像架构。
- 通过检查资源状态、仅处理预期的资源不存在情况，实现可重复执行的清理。保留权限、服务和存储错误，不要用 `|| true` 掩盖所有失败。

## 验证与完成

按任务需要实际验证应用响应、真实调用方的连通性、数据持久性或重启恢复。失败时检查容器和服务日志。仅构建成功或服务健康不能证明应用正常。

仅移除本任务创建的临时资源。执行大范围停止、删除或清理操作前，检查受影响资源并确认范围。报告已安装版本、完成的变更、执行的检查及尚未解决的限制。
