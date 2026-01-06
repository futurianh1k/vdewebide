# 관리자 포털(Admin Dashboard)

작성일: 2026-01-07

## 1) 목적

관리자 포털은 금융권 VDE 환경에서 **워크스페이스(code-server + opencode 컨셉)** 를
생성/중지/삭제/목록화하는 “운영 UI”의 MVP입니다.

본 MVP는 **외부 JS 빌드 체인 없이** FastAPI가 정적 파일을 서빙하는 구조로 구현했습니다.

## 2) 접속

- URL: `http://localhost:8090/admin`
- 관리자 키(MVP): `X-Admin-Key`
  - 기본값: `dev-admin-key`
  - 환경변수: `ADMIN_API_KEY`

UI 좌측의 Admin Key 입력칸에 키를 넣으면 API 호출에 사용됩니다.

## 3) 워크스페이스 모델(MVP)

워크스페이스는 “사용자가 접속하는 IDE 인스턴스”를 의미합니다.

- **mock 모드(기본)**: 컨테이너를 만들지 않고 상태만 관리합니다.
  - 장점: Docker/K8s 없이도 흐름 검증 가능
- **docker 모드(데모 기본)**: Docker Engine을 통해 code-server 컨테이너를 생성/중지/삭제합니다.
  - 운영에서는 K8s/포털 연동으로 확장 예정

설정:
- `WORKSPACE_PROVISIONER=mock|docker`
- `WORKSPACE_IMAGE` (docker 모드) 기본: `codercom/code-server:4.95.3`
- `WORKSPACE_PASSWORD` (docker 모드) code-server 패스워드

## 4) API 엔드포인트(요약)

모든 `/api/*` 호출은 `X-Admin-Key`가 필요합니다.

- `GET /api/workspaces`: 목록
- `POST /api/workspaces`: 생성
- `POST /api/workspaces/{id}/start`: 시작
- `POST /api/workspaces/{id}/stop`: 중지
- `DELETE /api/workspaces/{id}`: 삭제

## 5) 보안 메모(중요)

MVP의 `ADMIN_API_KEY` 방식은 데모/개발 편의용입니다.
운영/제출 환경에서는 아래로 대체하는 것을 전제로 합니다.

- SSO/Reverse Proxy 인증 + RBAC(tenant/project/workspace scope)
- 관리자 액션은 Audit Log로 기록(누가/언제/무엇을)
- Docker socket 마운트는 운영에서 금지(또는 엄격한 격리/권한 제한 필요)

