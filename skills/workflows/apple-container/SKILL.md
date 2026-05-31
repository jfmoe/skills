---
name: apple-container
description: 'Use when the user mentions apple container, the `container` CLI, migrating from Docker to apple container, or running OCI containers natively on macOS. Also trigger when the user wants to run containers on Mac without Docker Desktop, troubleshoots `container run`/`container build` commands, or discusses launchd-based container orchestration on macOS.'
---

# Apple Container CLI

Apple's native container runtime for macOS. Runs OCI-compatible Linux containers using Apple's virtualization framework — no Docker Desktop needed.

**Requirements:** macOS 26+ (some networking features require macOS 26)

## Install & First-Time Setup

```bash
brew install container

# 1. Start the system service
container system start

# 2. Install the Linux kernel (required, only once)
container system kernel set --recommended

# 3. Enable inter-container DNS (required for multi-container setups, needs sudo)
sudo container system dns create local
container system property set dns.domain local
```

Step 2 is mandatory — without a kernel, `container run` fails. Step 3 requires **both** commands; omitting `property set dns.domain` leaves DNS non-functional even though the domain was created.

## Docker → Apple Container Migration

The CLI is intentionally Docker-compatible in syntax. Most commands map directly:

| Docker                  | Apple Container                             | Notes                                                       |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| `docker run`            | `container run`                             | Same flags: `-d`, `--rm`, `--name`, `-p`, `-v`, `-e`, `-it` |
| `docker build`          | `container build`                           | Same: `-t/--tag`, `-f/--file`, `--build-arg`, `--target`    |
| `docker ps`             | `container list` / `container ls`           | `-a` for all                                                |
| `docker exec`           | `container exec`                            | Same: `-it`, `-e`, `-w`                                     |
| `docker stop`           | `container stop`                            | Adds `--all` flag                                           |
| `docker rm`             | `container delete` / `container rm`         | Adds `--all` flag                                           |
| `docker logs`           | `container logs`                            | Same: `-f`, `-n`                                            |
| `docker images`         | `container image list`                      |                                                             |
| `docker pull`           | `container image pull`                      |                                                             |
| `docker push`           | `container image push`                      |                                                             |
| `docker tag`            | `container image tag`                       |                                                             |
| `docker rmi`            | `container image delete`                    |                                                             |
| `docker cp`             | `container copy` / `container cp`           |                                                             |
| `docker inspect`        | `container inspect`                         |                                                             |
| `docker stats`          | `container stats`                           | Adds `--no-stream`                                          |
| `docker volume create`  | `container volume create`                   |                                                             |
| `docker volume rm`      | `container volume delete`                   |                                                             |
| `docker network create` | `container network create`                  | macOS 26+                                                   |
| `docker login`          | `container registry login`                  |                                                             |
| `docker logout`         | `container registry logout`                 |                                                             |
| `docker system prune`   | `container prune` + `container image prune` | Separate commands                                           |
| `docker compose`        | _(not available)_                           | No Compose equivalent yet                                   |

## Common Workflows

### Build and run a web server

```bash
container build --tag web-app --file Dockerfile .
container run --name web-app --detach --rm -p 8080:80 web-app
```

### Interactive shell in a container

```bash
container run -it --rm ubuntu:latest /bin/bash
# Or exec into running container:
container exec -it my-container sh
```

### Mount volumes

```bash
# Bind mount
container run -v /host/path:/container/path my-image

# Named volume
container volume create my-data
container run -v my-data:/data my-image
```

### Local DNS (access containers by name)

Both commands are required — omitting `property set` leaves DNS non-functional:

```bash
sudo container system dns create local
container system property set dns.domain local
# Now access containers at: http://<container-name>.local
container run --name my-app -d --rm nginx
open http://my-app.local
```

### Push to registry

```bash
container registry login registry.example.com
container image tag my-app registry.example.com/team/my-app:latest
container image push registry.example.com/team/my-app:latest
```

### Resource limits

```bash
container run --cpus 2 --memory 1024 my-image
```

### Environment variables

```bash
container run -e KEY=value --env-file .env my-image
```

### Networking between containers (macOS 26+)

Requires DNS setup first (see Install & First-Time Setup above).

```bash
container network create my-net
container run --name db --network my-net -d postgres
container run --name app --network my-net -d my-app
# app can reach db at hostname "db" (resolves as db.local)
```

## Docker Migration Pitfalls

### Volumes use ext4 → `lost+found` breaks some images

Named volumes are ext4-formatted and contain a `lost+found` directory at the mount root. Images that expect an empty mount point (e.g., PostgreSQL) will fail:

```
initdb: error: directory "/var/lib/postgresql/data" exists but is not empty
```

**Fix:** Set the data directory to a subdirectory within the volume:

```bash
container run -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
```

This applies to any image that checks for an empty mount point (MySQL `datadir`, etc.).

### No restart policy ([#286](https://github.com/apple/container/issues/286))

Apple Container has no `--restart` flag. Containers do not survive system reboots or crashes. Use a macOS launchd plist with `RunAtLoad` to auto-start containers at login.

### No Compose ([Discussion #194](https://github.com/apple/container/discussions/194))

No built-in equivalent to `docker compose`. Multi-container orchestration requires a shell script that handles: network/volume creation, startup order, health-check waits, and DSN wiring.

### System service doesn't auto-start ([#158](https://github.com/apple/container/issues/158))

`container system start` must run before any container commands work. After a reboot, the service is not running. Management scripts should include an `ensure_system` guard:

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

### `container inspect` JSON differs from Docker

Do not use `grep` to extract fields from `container inspect` output — escaping differences (e.g., backslashes in IP addresses) cause subtle bugs. Use proper JSON parsing:

```bash
# Good
container inspect my-container | python3 -c "
import sys,json
print(json.load(sys.stdin)[0]['networks'][0]['ipv4Address'].split('/')[0])
"

# Bad — fragile, breaks on escaped characters
container inspect my-container | grep -o '"ipv4Address":"[^/]*' | cut -d'"' -f4
```

### Watchtower / Docker-socket-dependent tools don't work

Tools like Watchtower that rely on `/var/run/docker.sock` cannot function in Apple Container. Replace with a launchd plist that periodically runs `container image pull` + recreates the container.

### launchd scripts need explicit PATH

macOS launchd does not inherit the user's shell PATH. Scripts invoked by launchd must set PATH explicitly, or `container` (installed at `/opt/homebrew/bin/container`) won't be found:

```bash
#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
```

### `set -euo pipefail` and cleanup commands

`container stop` / `container delete` return non-zero for non-existent containers. With `set -e`, this aborts the script. Always append `|| true`:

```bash
container stop my-app 2>/dev/null || true
container delete my-app 2>/dev/null || true
```

## Key Differences from Docker

1. **No daemon** — uses macOS launchd services (`container system start/stop`)
2. **Apple Virtualization** — runs a real Linux VM per container, not a shared daemon
3. **No Compose** — orchestrate with scripts or use individual commands
4. **DNS requires setup** — `sudo container system dns create <domain>` + `container system property set dns.domain <domain>`
5. **Rosetta support** — run x86_64 images on arm64: `container run --rosetta ...`
6. **SSH forwarding** — `container run --ssh ...` forwards host SSH agent
7. **Socket publishing** — `container run --publish-socket host:container` for Unix sockets
8. **Builder is separate** — BuildKit runs in its own container (`container builder start/stop`)

## System Management

```bash
container system status          # Check service health
container system version         # Show CLI and API versions
container system df              # Disk usage
container system logs --last 5m  # Recent service logs
container system kernel set --recommended  # Update kernel
```

## Cleanup

```bash
container stop --all             # Stop all running containers
container delete --all           # Remove all containers
container image prune --all      # Remove unused images
container volume prune           # Remove unused volumes
container network prune          # Remove unused networks
```

## Further Reference

For the complete command reference with all flags and options, fetch:
https://raw.githubusercontent.com/apple/container/refs/heads/main/docs/command-reference.md
