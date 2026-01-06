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
docker compose build ide
```

## 2) 오프라인 COPY(데모 기본)

`OPENCODE_URL`이 비어있으면, `services/workspace-image/opencode/`의 파일을 사용합니다.

- `services/workspace-image/opencode/opencode`
- `services/workspace-image/opencode/opencode.sha256`

