# 변경 이력 — feature/portal-frontend-backend

작성일: 2026-01-07  
브랜치: `feature/portal-frontend-backend`  
변경 성격: **신기능(관리자 포털: 프론트+백엔드) / 워크스페이스 관리**

## 1) 내가 요구한 내용

- 프론트엔드와 백엔드를 만들고, 관리자 대시보드를 만든다.
- “Cursor 웹 기반 admin site” 느낌의 UI를 참고하여 구성한다.
- 가장 중요한 기능은 **워크스페이스 관리**이며, 워크스페이스는 **code-server + opencode.ai** 컨셉이다.

## 2) 내가(에이전트) 답한 내용(요약)

- 폐쇄망을 고려해 외부 빌드 체인 없이 동작하는 **Portal(FastAPI + 정적 프론트)** 로 시작한다.
- Portal은 워크스페이스를 생성/중지/삭제/목록화한다.
- 실제 워크스페이스 생성은 환경에 따라 달라지므로, MVP에서는
  - Docker 엔진이 사용 가능한 경우: Docker provisioner로 컨테이너 기반 워크스페이스 생성
  - 그렇지 않은 경우: Mock provisioner로 상태만 관리(추후 K8s/포털 연동으로 확장)
  을 지원하도록 설계한다.

## 3) 수정/추가 내용 요약(예정)

- `services/portal` 추가(FastAPI)
  - `/admin` 관리자 대시보드(정적 HTML/JS/CSS)
  - `/api/workspaces` CRUD 및 start/stop 액션
  - Provisioner 추상화(mock/docker)
- `docker-compose.yml`에 portal 서비스 추가(로컬 데모)
- 최소 테스트(Portal API)

