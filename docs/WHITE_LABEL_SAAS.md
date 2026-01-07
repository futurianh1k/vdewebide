# White-label SaaS (독립형) 모드 — Mock 계약(SSO/JWT, Upstream Auth, DLP Policy, Workspace Lifecycle)

고객 시스템(SSO/인증서/정책/조직 구조) 상세 정보가 없더라도,
**독립형으로 동작 가능한 “화이트라벨 SaaS 코어”**를 먼저 만들기 위한 Mock 계약/API를 제공합니다.

## 1) 구성요소

- **Mock IdP** (`services/idp`)
  - JWT 발급: `POST /token`
  - JWKS 제공: `GET /.well-known/jwks.json`
- **AI Gateway** (`services/gateway`)
  - JWKS 기반 JWT 검증 가능(`JWT_JWKS_URL`, `JWT_ISSUER`, `JWT_AUDIENCE`)
  - DLP pre-check + (옵션) streaming incremental DLP
  - (Mock) 운영용 정책/설정 엔드포인트: `/ops/*`
- **Mock Upstream** (`services/mock_upstream`)
  - (옵션) Upstream 인증 요구/검증: `REQUIRE_UPSTREAM_AUTH=true` + `UPSTREAM_EXPECTED_BEARER`
- **Admin Portal** (`services/portal`)
  - workspace CRUD + (mock) tenant/project/user lifecycle API

## 2) 실행

```bash
docker compose up --build
```

- Portal: `http://localhost:8090/admin`
- Gateway: `http://localhost:8081`
- Mock Upstream: `http://localhost:8082`
- Mock IdP: `http://localhost:8083`

## 3) SSO/JWT Mock (IdP)

JWT 발급:

```bash
TOKEN=$(curl -sS -X POST http://localhost:8083/token \\
  -H 'Content-Type: application/json' \\
  -d '{"sub":"u1","tid":"t1","pid":"p1","wid":"w1","role":"admin","iss":"vde-idp","aud":"vde-gateway"}' | \\
  python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')
```

Gateway 호출(예: chat):

```bash
curl -sS http://localhost:8081/v1/chat \\
  -H "Authorization: Bearer $TOKEN" \\
  -H 'Content-Type: application/json' \\
  -d '{"messages":[{"role":"user","content":"hi"}]}'
```

참고:
- `docker-compose.yml` 기본값은 빠른 데모를 위해 `JWT_DEV_MODE=true`입니다.
- JWKS 검증 모드로 테스트하려면 `JWT_DEV_MODE=false`로 실행하고 위처럼 IdP 토큰을 사용하세요.

## 4) Upstream Auth Mock (Gateway ↔ Upstream)

목적: **Workspace 사용자 토큰을 upstream으로 전달하지 않고**, upstream 전용 인증을 적용했는지 검증.

1) mock upstream이 bearer를 요구하도록 켜기:

```bash
export REQUIRE_UPSTREAM_AUTH=true
export UPSTREAM_EXPECTED_BEARER=upstream-dev-token
```

2) gateway가 upstream에 static bearer를 붙이도록 켜기:

```bash
export UPSTREAM_AUTH_MODE=static_bearer
export UPSTREAM_BEARER_TOKEN=upstream-dev-token
```

이후 `docker compose up --build`로 실행하면, upstream은 bearer가 없으면 401을 반환합니다.

## 5) DLP Policy Mock (ops)

Gateway의 DLP 룰 파일(`DLP_RULES_PATH`)을 조회/갱신하는 **Mock 운영 API**를 제공합니다.

- 조회: `GET /ops/dlp/rules`
- 갱신: `PUT /ops/dlp/rules` (body: YAML 또는 JSON `{ \"raw\": \"...\" }`)

보호:
- `Authorization: Bearer <admin role token>` 필요
- `X-Ops-Key: <OPS_POLICY_KEY 또는 OPS_RETENTION_PURGE_KEY>` 필요

## 6) Workspace Lifecycle Mock (Portal)

Portal은 관리자 키(`X-Admin-Key`) 기반으로 아래 mock API를 제공합니다.

- tenants: `GET/POST /api/tenants`
- projects: `GET/POST /api/projects`
- users: `GET/POST /api/users`
- workspaces: `GET/POST /api/workspaces`, `POST /api/workspaces/{id}/start|stop`, `DELETE /api/workspaces/{id}`

운영에서는 DB/RBAC/감사/승인 프로세스로 확장하는 것을 전제로 합니다.

