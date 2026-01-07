FROM codercom/code-server:4.95.3

# Plan A: opencode 바이너리 포함
# - 폐쇄망 환경을 위해 2가지 경로 지원:
#   1) build-arg OPENCODE_URL 다운로드 + sha256 검증
#   2) build context의 opencode/opencode COPY + sha256 검증(opencode/opencode.sha256)

USER root

ARG OPENCODE_URL=""
ARG OPENCODE_SHA256=""

# code-server 베이스는 /bin/sh가 pipefail 미지원인 경우가 있어 bash로 고정
SHELL ["/bin/bash", "-lc"]

# COPY 경로(오프라인)
COPY opencode/ /opt/opencode/

RUN set -euo pipefail; \
    mkdir -p /usr/local/bin; \
    if [ -n "${OPENCODE_URL}" ]; then \
      echo "[workspace-image] download opencode from internal artifact"; \
      apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*; \
      curl -fsSL "${OPENCODE_URL}" -o /usr/local/bin/opencode; \
      if [ -z "${OPENCODE_SHA256}" ]; then echo "OPENCODE_SHA256 is required when OPENCODE_URL is set" >&2; exit 2; fi; \
      echo "${OPENCODE_SHA256}  /usr/local/bin/opencode" | sha256sum -c -; \
    else \
      echo "[workspace-image] use local opencode from build context"; \
      if [ ! -f /opt/opencode/opencode ]; then echo "/opt/opencode/opencode missing (place file under services/workspace-image/opencode/opencode)" >&2; exit 2; fi; \
      if [ ! -f /opt/opencode/opencode.sha256 ]; then echo "/opt/opencode/opencode.sha256 missing" >&2; exit 2; fi; \
      cp /opt/opencode/opencode /usr/local/bin/opencode; \
      (cd /usr/local/bin && sha256sum -c /opt/opencode/opencode.sha256); \
    fi; \
    chmod 0755 /usr/local/bin/opencode; \
    chown root:root /usr/local/bin/opencode

USER coder

