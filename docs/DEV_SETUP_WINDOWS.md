# 개발환경 구축 가이드 (Windows)

## 1) 준비물

- Docker Desktop (WSL2 기반 권장)

## 2) 실행(로컬 데모)

PowerShell에서 레포 루트로 이동 후:

```powershell
docker compose up --build
```

## 3) 접속

- Web IDE(code-server): `http://localhost:8080`
  - 비밀번호: `dev-only` (데모 전용)
- AI Gateway: `http://localhost:8081`
- Mock Upstream: `http://localhost:8082`
- Admin Portal: `http://localhost:8090/admin`
  - Admin Key(기본): `dev-admin-key`

## 4) 보안 주의사항(데모 한정)

- `JWT_DEV_MODE=true`와 `PASSWORD=dev-only`는 로컬 데모 용도이며 운영에서 사용 금지

