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

### opencode 설정 자동 주입(데모)

docker 모드에서 워크스페이스를 생성하면, 아래 경로에 설정이 자동으로 생성됩니다.

- `~/.config/opencode/opencode.json`

### opencode 실행 엔트리 자동 주입(데모)

docker 모드에서 워크스페이스를 생성하면, 터미널에서 아래 커맨드를 바로 실행할 수 있습니다.

- `opencode`

동작:
- 워크스페이스 이미지에 실제 `opencode` 바이너리가 포함되어 있으면 그대로 실행합니다.
- 아직 포함되어 있지 않으면, **폐쇄망 배포 방식(사내 아티팩트/이미지 빌드 포함)** 안내 메시지를 출력합니다.

원칙:
- **토큰/시크릿은 설정 파일에 저장하지 않음**
- Gateway endpoint만 지정(모델 선택/라우팅은 Gateway 정책으로 통제)

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
- opencode 토큰은 Secret 마운트(`/run/secrets/*`) 또는 환경변수로 주입하는 방식으로 확장 권장

