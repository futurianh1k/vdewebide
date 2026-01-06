#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${RUN_DIR:-/home/ubuntu/vdewebide-demo}"
cd "${RUN_DIR}"

if docker ps >/dev/null 2>&1; then
  docker compose down
else
  sudo -n docker compose down
fi

