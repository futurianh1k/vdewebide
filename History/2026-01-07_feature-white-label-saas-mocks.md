# 변경 이력 — feature/white-label-saas-mocks

작성일: 2026-01-07  
브랜치: `feature/white-label-saas-mocks`  
변경 성격: **중대한 변화(독립형 White-label SaaS 코어를 위한 Mock SSO/JWT, Upstream Auth, DLP Policy, Workspace Lifecycle 도입)**

## 1) 내가 요구한 내용

- 고객 시스템 상세 정보가 없는 상태에서 질문(SSO/JWT, upstream auth, DLP, workspace lifecycle)에 답을 확정할 수 없으니,
  **독립형(white-label SaaS) 솔루션**을 먼저 만들고,
  이후 고객 연동은 별도로 고려한다.
- 이를 위해 아래 항목에 대한 **mock 코드 및 API 엔드포인트**를 만든다:
  - SSO/JWT
  - Upstream Auth
  - DLP Policy
  - Workspace Lifecycle

## 2) 내가(에이전트) 답한 내용(요약)

- 독립형 구성을 위해 “Identity Provider(IdP)” 성격의 mock 서비스를 추가하여 JWT 발급 + JWKS 제공을 구현한다.
- Gateway는 JWKS 기반 JWT 검증 모드로 동작 가능하도록 기본 설정/예시를 제공한다.
- Mock Upstream은 Gateway의 upstream auth(static bearer 등)를 검증할 수 있도록 인증 요구 모드를 제공한다.
- DLP 정책은 “관리 API(예: ops/admin)”로 조회/갱신 가능하게 하고, 실제 요청 처리에는 즉시 반영되도록 만든다(운영형은 추후 승인/배포 체계로 확장).
- Workspace lifecycle은 Portal의 workspace CRUD를 확장해 tenant/project/user 같은 SaaS 기본 엔터티를 포함하고, API/테스트로 보증한다.

## 3) 수정/추가 내용(예정)

- `services/idp/`: mock SSO/JWT(IdP) 서비스(FastAPI)
- `services/gateway/`: JWT(JWKS) 검증 구성 예시 + (옵션) 정책 관리(ops/admin) 엔드포인트
- `services/mock_upstream/`: upstream auth 요구/검증 모드 추가
- `services/portal/`: tenant/project/user 포함 lifecycle API 스캐폴딩 및 UI/테스트 보강
- `docker-compose.yml`: idp 서비스 추가 및 연결 예시
- 테스트: 위 mock 기능에 대한 최소 단위 테스트 추가

## 4) 이번 브랜치에서 반영된 내용(완료)

- **Mock IdP 추가**
  - `services/idp`: `/.well-known/jwks.json`, `/token` 구현 + 테스트
  - `docker-compose.yml`에 `idp` 서비스 추가(8083)
- **Gateway 확장(Mock 운영 API)**
  - `/ops/dlp/rules` GET/PUT: DLP rules 조회/갱신 + 즉시 반영
  - `/ops/upstream/auth` GET/PUT: upstream auth 모드(none/static_bearer) 조회/갱신
  - dev 편의: `JWT_DEV_MODE=true`에서 `Bearer dev-admin` 토큰 허용(ops 테스트/데모용)
  - 권한: `/ops/*`는 admin role로 authorize 되도록 보강
- **Mock Upstream 확장**
  - `REQUIRE_UPSTREAM_AUTH=true`일 때 `UPSTREAM_EXPECTED_BEARER` 검증(없으면 401) + 테스트
- **Portal 확장**
  - tenant/project/user mock API 추가: `/api/tenants`, `/api/projects`, `/api/users` + 테스트
- **문서**
  - `docs/WHITE_LABEL_SAAS.md`: 독립형 mock 계약/흐름 정리
  - `docs/ENV_EXAMPLE.md`: 독립형 옵션(JWT 검증/Upstream auth) 추가

- **PoC 데모 UX**
  - Portal에 “PoC 자동 생성(tenant/project/user/workspace 1세트)” 버튼 및 API(`/api/poc/bootstrap`)를 추가하여 시연 시간을 단축

- **개발 도구**
  - 개발 환경에서 Portainer를 사용할 수 있도록 `docker-compose.yml`에 `portainer` 서비스를 추가
