# 변경 이력 — feature/workspace-opencode-autoconfig

작성일: 2026-01-07  
브랜치: `feature/workspace-opencode-autoconfig`  
변경 성격: **신기능(워크스페이스 생성 시 opencode 설정 자동 주입)**

## 1) 내가 요구한 내용

- “code-server + opencode.ai” 컨셉에 맞게,
  Portal에서 워크스페이스를 만들면 **opencode 설정(JSON)** 이 자동으로 준비되도록 진행한다.

## 2) 내가(에이전트) 답한 내용(요약)

- Docker 기반 워크스페이스 생성 시,
  - `~/.config/opencode/opencode.json`을 **자동 생성/주입**하고
  - 워크스페이스 컨테이너를 **Gateway와 같은 네트워크에 붙여** `http://gateway:8081`로 접근 가능하게 만든다.
- 토큰/시크릿은 설정 파일에 저장하지 않고(보안), Secret 마운트 방식으로 확장 가능하게 둔다.

## 3) 수정/추가 내용 요약(예정)

- `services/portal`: DockerProvisioner에 opencode config volume 생성/초기화 로직 추가
- `docs`: 데모/운영 주의사항 업데이트
- 테스트: 설정 생성 로직의 단위 테스트 추가(도커 없이 검증 가능)

