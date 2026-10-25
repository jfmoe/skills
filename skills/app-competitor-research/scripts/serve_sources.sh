#!/bin/sh
# Serve a test-material directory on the LAN for source and download tests:
# WebDAV on 8090 (user test / password test1234) and plain HTTP on 8091.
# Usage: serve_sources.sh <materials-dir>
set -eu
dir=$(cd "$1" && pwd)
config=$(mktemp -t wsgidav).yaml
cat > "$config" <<YAML
host: 0.0.0.0
port: 8090
provider_mapping:
  "/": "$dir"
http_authenticator:
  domain_controller: null
  accept_basic: true
  accept_digest: false
  default_to_digest: false
simple_dc:
  user_mapping:
    "*":
      "test":
        password: "test1234"
YAML
python3 -m http.server 8091 --bind 0.0.0.0 --directory "$dir" &
http_pid=$!
trap 'kill $http_pid; rm -f "$config"' EXIT INT TERM
uvx --from wsgidav --with cheroot wsgidav --config "$config"
