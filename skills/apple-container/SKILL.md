---
name: apple-container
description: 'Use for Apple Container CLI setup, operation, troubleshooting, Docker migration on macOS, or launchd-based container orchestration.'
---

# Apple Container CLI

Use the installed CLI and its matching official documentation to operate Apple's Linux containers on macOS. Keep version-dependent command syntax, platform requirements, and feature availability in those sources.

## Establish the environment

1. Run `command -v container`, `container --version`, `sw_vers`, and `uname -m`. If the CLI is absent, check the official installation requirements before installing through the user's preferred package manager.
2. Read `container --help` and the relevant subcommand's `--help`. Use local help for available commands and flags; use the matching release documentation for behavior and limitations.
3. For operations needing the service, inspect `container system status`. Start it if needed; preserve startup errors for diagnosis.

Proceed when the installed version, host compatibility, and required command support are established. If local help and documentation disagree, report the mismatch and verify the operation before relying on it.

## Find the matching reference

Start at the [official repository](https://github.com/apple/container) and [releases](https://github.com/apple/container/releases). Select the tag matching `container --version`, then open the relevant file below. These paths are relative to that tag; `main` may describe unreleased behavior. If a path moved, locate its replacement in the selected tree. For a development build, use its commit when available and state any remaining uncertainty.

| Task | Official source in the selected tag |
| --- | --- |
| Installation and host requirements | `README.md` |
| Command syntax | `docs/command-reference.md` |
| System defaults and configuration | `docs/container-system-config.md` |
| DNS, ports, and custom networks | `docs/networking.md` |
| Host services and SSH forwarding | `docs/host-integration.md` |
| Architecture selection and Rosetta | `docs/multiplatform-images.md` |
| Persistent storage | `docs/volumes.md` |
| Long-lived Linux machines | `docs/container-machine.md` |
| Kubernetes, when exposed by local help | `docs/kubernetes.md` |

Read only the references needed for the task. Check release notes when upgrading or investigating a behavior change.

## Initialize and configure

- Inspect `container system start --help` before scripting first startup. Startup can offer kernel installation; where supported, `container system start --enable-kernel-install` handles a missing kernel without an interactive prompt. Use `container system kernel set --recommended` for an explicit kernel install or update, rather than repeating it after every start.
- Read the existing configuration before changing it. For TOML-based releases, edit the relevant keys in `~/.config/container/config.toml`, preserving unrelated sections. Merge into an existing table; blindly appending another `[dns]` table makes the file invalid.
- Apply configuration changes using the documented lifecycle. Before a required service restart, inspect running workloads and account for the interruption. Where supported, verify effective values with `container system property list`.

Initialization is complete when the service is healthy and the requested workload starts successfully; a successful configuration write alone is insufficient.

## Networking

Treat each communication path separately:

- **Mac to container:** use a published port or a reachable container IP. For DNS names, configure the service's DNS domain and the Mac's resolver as described in the matching networking guide.
- **Container to container:** verify network membership and test resolution from the calling container. On releases using `[dns] domain`, this registers qualified names; `container system dns create <domain>` configures the Mac's resolver. These serve different callers.
- **Container to Mac:** consult the host integration guide. If using `container system dns create --localhost`, check its documented packet-filter, restart, and Private Relay effects before changing host networking.

For a fresh local DNS setup, use the guide's example domain, such as `test`, consistently. Preserve an existing working domain unless the task requires changing it. With TOML configuration, merge:

```toml
[dns]
domain = "test"
```

Follow the matching guide to apply it and configure the host resolver with `sudo container system dns create test` when host name resolution is needed.

Do not assume Docker Compose-style bare service names resolve on custom networks. Check the release's networking limitations. Use a documented qualified name on a supported network, or inspect the destination container's IP on the shared network. Parse `container inspect` as JSON and select the intended network; avoid assuming the first address is correct. Recheck addresses after recreating containers.

Networking is verified only after the intended caller resolves or addresses the destination and reaches its application port. Host-only success does not prove container-to-container connectivity.

## Docker migration and persistent workloads

- Translate each required operation using local help. Similar command names do not guarantee identical flags, JSON schemas, Docker API compatibility, or lifecycle behavior. Verify any tool that depends on a Docker socket against its actual integration requirements.
- Check current Compose and restart-policy support before choosing orchestration. If the installed version lacks the required behavior, use a script or launchd job that handles service readiness, dependencies, application health, and persistent data. Distinguish startup at login from recovery after an application crash; `RunAtLoad` alone does not provide crash recovery.
- For launchd jobs, resolve the executable with `command -v container` and use its absolute path or an explicit PATH. Test in the job's user context. Use bounded readiness checks and retain failure output.
- Inspect volume contents and the image's documented data-directory contract before changing mounts. If an ext4 volume's `lost+found` prevents initialization, configure a supported subdirectory for application data. Preserve existing data and follow the image's migration procedure for an already initialized database.
- Select the intended image architecture explicitly for cross-architecture execution, for example `container run --arch amd64 ...` or `--platform linux/amd64` when supported. Check Rosetta requirements separately; `--rosetta` alone does not select the image architecture.
- Make cleanup idempotent by checking resource state and handling only expected absence. Keep permission, service, and storage errors visible instead of masking all failures with `|| true`.

## Verify and finish

Exercise the requested behavior: application response, connectivity from the real caller, data persistence, or recovery after restart, as applicable. Inspect container and service logs when it fails. Build-only or service-only success is not proof of application health.

Remove only disposable resources created for this task. Inspect the affected resources and confirm scope before broad stop, delete, or prune operations. Report the installed version, changes made, checks performed, and any unresolved limitations.
