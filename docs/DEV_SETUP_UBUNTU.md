# 개발환경 구축 가이드 (Ubuntu)

## 1) 준비물

- Docker + Docker Compose(v2)

## 2) 실행(로컬 데모)

레포 루트에서:

```bash
docker compose up --build
```

### Workspace 이미지(opencode 포함) 빌드(Plan A)

이 데모는 `services/workspace-image/`를 통해 `vde-workspace:0.1` 이미지를 빌드합니다.

- **오프라인 COPY(데모 기본)**: `services/workspace-image/opencode/opencode` 파일을 사용
- **내부 아티팩트 다운로드(권장)**: `OPENCODE_URL`, `OPENCODE_SHA256`를 build-arg로 제공

자세한 내용은 `services/workspace-image/README.md` 참고.

### (중요) Docker가 Snap 설치인 경우

Ubuntu에서 Docker가 Snap(`/snap/bin/docker`)로 설치된 환경에서는,
Snap 격리 정책 때문에 `/data*` 같은 외부 마운트 경로의 파일을 `docker compose`가 읽지 못할 수 있습니다.

이 레포가 `/data8tb01/...` 아래에 있는 현재 환경에서는 아래 중 하나를 선택하세요:

- **권장(간단)**: 레포를 `/home/ubuntu/` 아래로 복제해서 거기서 `docker compose up --build` 실행
- **대안**: Snap이 아닌 Docker(apt 설치)로 전환(조직 표준에 따름)

## 3) 접속

- Web IDE(code-server): `http://localhost:8080`
  - 비밀번호: `dev-only` (데모 전용)
- AI Gateway: `http://localhost:8081`
- Mock Upstream: `http://localhost:8082`
- Admin Portal: `http://localhost:8090/admin`
  - Admin Key(기본): `dev-admin-key`

## 4) 빠른 호출 예시

Gateway는 dev 모드에서 `Authorization: Bearer dev`를 허용합니다.

```bash
curl -sS -X POST http://localhost:8081/v1/chat \
  -H 'Authorization: Bearer dev' \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hello"}]}' | jq .
```

## 5) 보안 주의사항(데모 한정)

- `JWT_DEV_MODE=true`와 `PASSWORD=dev-only`는 로컬 데모 용도이며 운영에서 사용 금지
- 운영에서는 SSO/JWKS, 네트워크 egress 통제, mTLS/mesh, Secret 관리 체계를 반드시 적용

## 6) 원클릭 실행(추천)

Snap docker 환경에서 `/data*` 경로 문제를 피하기 위해, 아래 스크립트를 사용할 수 있습니다:

```bash
./scripts/run_demo.sh
```

중지:

```bash
./scripts/stop_demo.sh
```

## 7) 워크스페이스를 “실제로” 생성하는 데모(Portal docker provisioner)

현재 `docker-compose.yml`은 기본적으로 Portal이 `WORKSPACE_PROVISIONER=docker`로 동작하도록 구성되어 있습니다.
즉, 관리자 화면에서 워크스페이스를 생성하면 **실제 code-server 컨테이너**가 Docker Engine에 생성됩니다.

주의:
- Portal 컨테이너에 `/var/run/docker.sock`를 마운트합니다(운영에서는 지양).
- Docker 소켓 권한 이슈가 있으면 `sudo docker compose up ...` 형태로 실행해야 할 수 있습니다.
