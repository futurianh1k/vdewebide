# Workspace Image (Plan A: opencode 바이너리 포함)

## 목적

금융권 폐쇄망(VDE) 환경에서 워크스페이스를 **재현 가능(불변 이미지)** 하게 제공하기 위해,
code-server 기반 이미지에 `opencode` 바이너리를 포함합니다.

## 빌드 방식(2가지)

### 1) 내부 아티팩트에서 다운로드(권장)

빌드 시점에 사내 아티팩트(예: Nexus/Artifactory/Harbor HTTP)에서 `opencode` 바이너리를 내려받아 포함합니다.
반드시 sha256로 무결성 검증을 수행합니다.

필수 build-arg:
- `OPENCODE_URL`: 내부 다운로드 URL
- `OPENCODE_SHA256`: 바이너리 sha256 (hex)

예시:

```bash
docker build -t vde-workspace:0.1 \\
  --build-arg OPENCODE_URL='https://artifact.intra.example/opencode/opencode-linux-amd64' \\
  --build-arg OPENCODE_SHA256='...hex...' \\
  services/workspace-image
```

### 2) 오프라인 COPY(완전 폐쇄망/다운로드 금지 환경)

빌드 컨텍스트에 바이너리를 넣고 COPY합니다.

- `services/workspace-image/opencode/opencode` 경로에 바이너리 배치
- `services/workspace-image/opencode/opencode.sha256`에 sha256 기록

```bash
docker build -t vde-workspace:0.1 services/workspace-image
```

## 실행 확인

컨테이너에서:

```bash
opencode --help
```

## 보안/운영 주의사항

- 바이너리는 반드시 **승인된 사내 아티팩트**에서만 공급
- sha256 검증은 필수(변조 방지)
- 운영에서는 버전/체크섬/승인 이력을 릴리즈 노트/Change Management로 남길 것

