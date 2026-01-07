# 변경 이력 — feature/workspace-image-opencode-bundled

작성일: 2026-01-07  
브랜치: `feature/workspace-image-opencode-bundled`  
변경 성격: **중대한 변화(워크스페이스 표준 이미지 추가 / opencode 바이너리 포함)**

## 1) 내가 요구한 내용

- Plan A: 폐쇄망에서 opencode 바이너리를 **이미지 빌드에 포함**하는 방식으로 진행한다.

## 2) 내가(에이전트) 답한 내용(요약)

- `workspace-base` 이미지에 opencode 바이너리를 포함하도록 빌드 스캐폴딩을 추가한다.
- 폐쇄망 환경을 고려해 아래 2가지 경로를 모두 지원한다:
  - **내부 아티팩트 URL 다운로드 + sha256 검증**
  - **로컬 파일 COPY + sha256 검증**(완전 오프라인 빌드 가능)
- docker-compose에서 Workspace 이미지가 기본으로 사용되도록 연결한다.

## 3) 수정/추가 내용(예정)

- `services/workspace-image/` 추가(Dockerfile + 빌드 스크립트/가이드)
- `docker-compose.yml`: IDE 및 Portal(workspace_image) 기본값을 workspace 이미지로 전환
- 문서: 폐쇄망 빌드 절차, sha256 검증, 운영 승인 포인트 정리

## 4) CI 반영(실수 방지)

- CI에서 `scripts/preflight_opencode_env.sh`를 **테스트 전에 필수 실행**하도록 워크플로우를 추가했다.
  - 목적: `OPENCODE_URL` 설정 시 `OPENCODE_SHA256` 누락/형식 오류를 파이프라인에서 즉시 실패시키기 위함

- CI에서 workspace 이미지 빌드 스모크 테스트를 추가했다(offline COPY 경로):
  - `services/workspace-image`를 빌드하고 `/usr/local/bin/opencode` 존재/실행 여부를 점검
