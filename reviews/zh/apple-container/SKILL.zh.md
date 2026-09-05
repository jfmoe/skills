---
name: apple-container
description: '当用户提到 apple container、`container` CLI、从 Docker 迁移到 apple container，或在 macOS 上原生运行 OCI 容器时使用。当用户想在 Mac 上不使用 Docker Desktop 运行容器、排查 `container run`/`container build` 命令问题，或讨论基于 launchd 的 macOS 容器编排时也应触发。'
---

# Apple Container CLI

Apple 为 macOS 提供的原生容器运行时。基于 Apple 的虚拟化框架运行 OCI 兼容的 Linux 容器——无需 Docker Desktop。

**要求：** 仅限 macOS 26。Apple 不支持更早的 macOS 版本（它依赖 macOS 26 的虚拟化/网络特性）。

> **版本说明（1.0.0+）：** `container system property get`/`set` 已被**移除**。系统配置现在存放在 TOML 文件 `~/.config/container/config.toml` 中。下文的 DNS 设置反映了这一点；旧文档中展示的 `container system property set dns.domain ...` 已经过时，会执行失败。

## 安装与首次设置

```bash
brew install container

# 1. 启动系统服务
container system start

# 2. 安装 Linux 内核（必需，仅需一次）
container system kernel set --recommended

# 3. 启用容器间 DNS（多容器场景必需，需要 sudo）
sudo container system dns create local

# 4. 通过 TOML 配置将其设为默认域（替代旧的 `property set`）
mkdir -p ~/.config/container
cat >> ~/.config/container/config.toml <<'EOF'
[dns]
domain = "local"
EOF

# 5. 重启服务以使配置生效
container system stop && container system start
```

第 2 步是强制性的——没有内核，`container run` 会失败。DNS 需要**同时**完成 `dns create` 命令（第 3 步）和 `config.toml` 中的 `[dns] domain` 条目（第 4 步）；仅创建域会使解析功能不可用。使用 `container system property list` 验证配置。

## Docker → Apple Container 迁移

该 CLI 在语法上有意与 Docker 兼容。大多数命令可直接对应：

| Docker                  | Apple Container                             | 备注                                                       |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| `docker run`            | `container run`                             | 相同参数：`-d`、`--rm`、`--name`、`-p`、`-v`、`-e`、`-it` |
| `docker build`          | `container build`                           | 相同：`-t/--tag`、`-f/--file`、`--build-arg`、`--target`    |
| `docker ps`             | `container list` / `container ls`           | `-a` 显示全部                                                |
| `docker exec`           | `container exec`                            | 相同：`-it`、`-e`、`-w`                                     |
| `docker stop`           | `container stop`                            | 新增 `--all` 参数                                           |
| `docker rm`             | `container delete` / `container rm`         | 新增 `--all` 参数                                           |
| `docker logs`           | `container logs`                            | 相同：`-f`、`-n`                                            |
| `docker images`         | `container image list`                      |                                                             |
| `docker pull`           | `container image pull`                      |                                                             |
| `docker push`           | `container image push`                      |                                                             |
| `docker tag`            | `container image tag`                       |                                                             |
| `docker rmi`            | `container image delete`                    |                                                             |
| `docker cp`             | `container copy` / `container cp`           |                                                             |
| `docker save`           | `container image save`                      | 导出镜像为 tar                                              |
| `docker load`           | `container image load`                      | 从 tar 导入镜像                                             |
| `docker export`         | `container export`                          | 导出容器文件系统为 tar                                      |
| `docker inspect`        | `container inspect`                         |                                                             |
| `docker stats`          | `container stats`                           | 新增 `--no-stream`                                          |
| `docker volume create`  | `container volume create`                   |                                                             |
| `docker volume rm`      | `container volume delete`                   |                                                             |
| `docker network create` | `container network create`                  | macOS 26+                                                   |
| `docker login`          | `container registry login`                  |                                                             |
| `docker logout`         | `container registry logout`                 |                                                             |
| `docker system prune`   | `container prune` + `container image prune` | 拆分为独立命令                                              |
| `docker compose`        | _（不可用）_                                | 尚无 Compose 等价功能                                       |

## 常用工作流

### 构建并运行 Web 服务器

```bash
container build --tag web-app --file Dockerfile .
container run --name web-app --detach --rm -p 8080:80 web-app
```

### 在容器中使用交互式 shell

```bash
container run -it --rm ubuntu:latest /bin/bash
# 或者 exec 进入运行中的容器：
container exec -it my-container sh
```

### 挂载卷

```bash
# 绑定挂载
container run -v /host/path:/container/path my-image

# 命名卷
container volume create my-data
container run -v my-data:/data my-image
```

### 本地 DNS（按名称访问容器）

两步都是必需的——只创建域而不配置 `[dns] domain` 条目会使 DNS 不可用：

```bash
sudo container system dns create local
# 在 ~/.config/container/config.toml 中设置默认域（替代已移除的 `property set`）：
#   [dns]
#   domain = "local"
container system stop && container system start   # 重启以应用
# 现在可以通过以下地址访问容器：http://<container-name>.local
container run --name my-app -d --rm nginx
open http://my-app.local
```

### 推送到镜像仓库

```bash
container registry login registry.example.com
container image tag my-app registry.example.com/team/my-app:latest
container image push registry.example.com/team/my-app:latest
```

### 资源限制

```bash
container run --cpus 2 --memory 1024 my-image
```

### 环境变量

```bash
container run -e KEY=value --env-file .env my-image
```

### 容器间网络（macOS 26+）

需要先完成 DNS 设置（见上文"安装与首次设置"）。

```bash
container network create my-net
container run --name db --network my-net -d postgres
container run --name app --network my-net -d my-app
# app 可以通过主机名 "db" 访问 db（解析为 db.local）
```

## Docker 迁移陷阱

### 卷使用 ext4 → `lost+found` 会破坏某些镜像

命名卷采用 ext4 格式，挂载点根目录下包含一个 `lost+found` 目录。期望挂载点为空的镜像（例如 PostgreSQL）会失败：

```
initdb: error: directory "/var/lib/postgresql/data" exists but is not empty
```

**修复：** 将数据目录设置为卷内的子目录：

```bash
container run -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
```

这适用于任何检查挂载点是否为空的镜像（MySQL 的 `datadir` 等）。

### 没有重启策略 ([#286](https://github.com/apple/container/issues/286))

Apple Container 没有 `--restart` 参数。容器无法在系统重启或崩溃后存活。可使用带有 `RunAtLoad` 的 macOS launchd plist 在登录时自动启动容器。

### 没有 Compose（[Discussion #194](https://github.com/apple/container/discussions/194)）

没有 `docker compose` 的内置等价功能。多容器编排需要一个 shell 脚本来处理：网络/卷创建、启动顺序、健康检查等待以及 DSN 连接配置。

### 系统服务不会自动启动 ([#158](https://github.com/apple/container/issues/158))

任何容器命令生效之前都必须先运行 `container system start`。重启后服务不会运行。管理脚本应包含一个 `ensure_system` 保护逻辑：

```bash
ensure_system() {
    if ! container list &>/dev/null; then
        container system start 2>/dev/null || true
        local i=0
        while [ $i -lt 30 ]; do
            container list &>/dev/null && return 0
            sleep 1; i=$((i + 1))
        done
        return 1
    fi
}
```

### `container inspect` 的 JSON 与 Docker 不同

不要用 `grep` 从 `container inspect` 输出中提取字段——转义差异（例如 IP 地址中的反斜杠）会导致隐蔽的 bug。请使用正规的 JSON 解析：

```bash
# 好的做法
container inspect my-container | python3 -c "
import sys,json
print(json.load(sys.stdin)[0]['networks'][0]['ipv4Address'].split('/')[0])
"

# 坏的做法——脆弱，遇到转义字符会出错
container inspect my-container | grep -o '"ipv4Address":"[^/]*' | cut -d'"' -f4
```

### Watchtower 等依赖 Docker socket 的工具不可用

像 Watchtower 这样依赖 `/var/run/docker.sock` 的工具在 Apple Container 中无法工作。可替换为定期运行 `container image pull` 并重建容器的 launchd plist。

### launchd 脚本需要显式设置 PATH

macOS launchd 不会继承用户的 shell PATH。由 launchd 调用的脚本必须显式设置 PATH，否则找不到 `container`（安装在 `/opt/homebrew/bin/container`）：

```bash
#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
```

### `set -euo pipefail` 与清理命令

`container stop` / `container delete` 对不存在的容器会返回非零状态。在使用 `set -e` 时，这会中止脚本。务必追加 `|| true`：

```bash
container stop my-app 2>/dev/null || true
container delete my-app 2>/dev/null || true
```

## 与 Docker 的关键差异

1. **无守护进程** —— 使用 macOS launchd 服务（`container system start/stop`）
2. **Apple 虚拟化** —— 每个容器运行一个真实的 Linux VM，而非共享守护进程
3. **无 Compose** —— 使用脚本或单独命令进行编排
4. **DNS 需要手动设置** —— `sudo container system dns create <domain>` 加上 `~/.config/container/config.toml` 中的 `[dns] domain = "<domain>"` 条目（旧的 `container system property set dns.domain` 已在 1.0.0 中移除）
5. **Rosetta 支持** —— 在 arm64 上运行 x86_64 镜像：`container run --rosetta ...`
6. **SSH 转发** —— `container run --ssh ...` 转发宿主机 SSH agent
7. **Socket 发布** —— `container run --publish-socket host:container` 用于 Unix socket
8. **构建器独立** —— BuildKit 在自己的容器中运行（`container builder start/stop`）
9. **TOML 配置（1.0.0+）** —— 系统配置存放在 `~/.config/container/config.toml`，包含 `[build]`、`[container]`、`[dns]`、`[kernel]`、`[network]`、`[registry]`、`[vminit]` 等配置节。`container system property list` 可查看当前值；没有 `get`/`set`。
10. **`container machine`（1.0.0+）** —— 管理与宿主机集成更紧密的长期 Linux VM，区别于每个容器的临时 VM（`container machine create/run/list/stop/delete`）。

## 系统管理

```bash
container system status          # 检查服务健康状态
container system version         # 显示 CLI 和 API 版本
container system df              # 磁盘使用情况
container system logs --last 5m  # 最近的服务日志
container system kernel set --recommended  # 更新内核
container system property list   # 显示当前配置（来自 config.toml）；1.0.0+ 中没有 get/set
container system dns list        # 列出已配置的 DNS 域
```

## 清理

```bash
container stop --all             # 停止所有运行中的容器
container delete --all           # 删除所有容器
container image prune --all      # 删除未使用的镜像
container volume prune           # 删除未使用的卷
container network prune          # 删除未使用的网络
```

## 延伸阅读

获取包含所有参数和选项的完整命令参考：
https://raw.githubusercontent.com/apple/container/refs/heads/main/docs/command-reference.md
