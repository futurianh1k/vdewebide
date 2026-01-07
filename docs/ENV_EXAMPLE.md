# 환경변수 예시(Plan A: opencode 바이너리 포함)

`docker compose`는 기본적으로 현재 디렉토리의 `.env`를 읽습니다.  
보안상 `.env`는 커밋하지 말고(레포에는 포함하지 않음), 아래 예시를 참고해 로컬/운영에서 별도로 관리하세요.

## 1) 내부 아티팩트 다운로드(권장)

- `OPENCODE_URL`: 내부 아티팩트에서 opencode 바이너리를 내려받는 URL
- `OPENCODE_SHA256`: 해당 바이너리의 sha256(hex)

예시:

```bash
export OPENCODE_URL='https://artifact.intra.example/opencode/opencode-linux-amd64'
export OPENCODE_SHA256='(hex sha256)'
./scripts/preflight_opencode_env.sh
docker compose build ide
```

## 2) 오프라인 COPY(데모 기본)

`OPENCODE_URL`이 비어있으면, `services/workspace-image/opencode/`의 파일을 사용합니다.

- `services/workspace-image/opencode/opencode`
- `services/workspace-image/opencode/opencode.sha256`

## 3) 운영 체크리스트(실수 방지)

- `OPENCODE_URL`을 설정했다면:
  - `OPENCODE_SHA256`도 반드시 설정되어야 함(빈 값이면 실패)
  - `OPENCODE_SHA256` 형식은 **64자리 hex**여야 함
  - 빌드 전 `./scripts/preflight_opencode_env.sh`로 사전 검증(권장)
- `OPENCODE_URL`이 비어있다면:
  - 오프라인 COPY 경로를 사용
  - `services/workspace-image/opencode/opencode.sha256`가 실제 바이너리 sha256과 일치해야 함

## CI(GitHub Actions)에서 artifact 경로 스모크 테스트를 켜는 방법

- GitHub 레포 Settings → Secrets and variables → Actions → Secrets에 아래 2개를 등록하면,
  `.github/workflows/ci.yml`의 `image_smoke_artifact` job이 자동으로 활성화됩니다.
  - `OPENCODE_URL`: 사내 아티팩트의 opencode 바이너리 URL
  - `OPENCODE_SHA256`: 위 바이너리의 sha256(64-hex)

- 미등록 시에는 `image_smoke_artifact` job이 **스킵**되며, offline(COPY) 스모크 테스트만 수행됩니다.
