# 개발환경 구축 가이드 (Ubuntu)

## 1) 준비물

- Docker + Docker Compose(v2)

## 2) 실행(로컬 데모)

레포 루트에서:

```bash
docker compose up --build
```

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

