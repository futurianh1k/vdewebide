#!/usr/bin/env bash
set -euo pipefail

# 데모 실행 스크립트
# - Snap docker 환경에서 /data* 경로 접근이 막히는 경우를 우회하기 위해 /home/ubuntu로 복제 후 실행
# - 도커 소켓 권한 이슈가 있으면 sudo로 docker compose 실행

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${RUN_DIR:-/home/ubuntu/vdewebide-demo}"

echo "[run_demo] src: ${SRC_DIR}"
echo "[run_demo] run: ${RUN_DIR}"

mkdir -p "${RUN_DIR}"
rsync -a --delete --exclude '.git' --exclude '.venv' "${SRC_DIR}/" "${RUN_DIR}/"

cd "${RUN_DIR}"

if docker compose version >/dev/null 2>&1; then
  :
else
  echo "[run_demo] docker compose not found" >&2
  exit 1
fi

if docker ps >/dev/null 2>&1; then
  echo "[run_demo] docker permission OK"
  docker compose up --build
else
  echo "[run_demo] docker permission denied -> using sudo"
  sudo -n docker compose up --build
fi

