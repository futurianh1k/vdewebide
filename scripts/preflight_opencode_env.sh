#!/usr/bin/env bash
set -euo pipefail

# Preflight check for Plan A workspace image build args
# - OPENCODE_URL set  => OPENCODE_SHA256 must be set and 64-hex
# - OPENCODE_URL empty => offline copy mode (no sha256 check required here)

OPENCODE_URL="${OPENCODE_URL:-}"
OPENCODE_SHA256="${OPENCODE_SHA256:-}"

if [ -z "${OPENCODE_URL}" ]; then
  echo "[preflight] OPENCODE_URL is empty -> offline COPY mode (services/workspace-image/opencode/)"
  exit 0
fi

if [ -z "${OPENCODE_SHA256}" ]; then
  echo "[preflight] ERROR: OPENCODE_URL is set but OPENCODE_SHA256 is empty." >&2
  echo "          Set OPENCODE_SHA256 to the 64-hex sha256 of the opencode binary." >&2
  exit 2
fi

if ! [[ "${OPENCODE_SHA256}" =~ ^[0-9a-fA-F]{64}$ ]]; then
  echo "[preflight] ERROR: OPENCODE_SHA256 must be a 64-hex string." >&2
  echo "          got: ${OPENCODE_SHA256}" >&2
  exit 2
fi

echo "[preflight] OK: OPENCODE_URL + OPENCODE_SHA256 look valid."

