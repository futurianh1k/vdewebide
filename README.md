# VDE Web IDE (Cursor-like) On-Prem MVP

이 레포는 금융권 폐쇄망(VDE) 환경을 전제로 한 **Web 기반 IDE(code-server)** + **AI Gateway(단일 통제 지점)** MVP 착수 구현입니다.

## 핵심 원칙(요약)

- Workspace(IDE)와 Model/AI Runtime 분리
- Workspace의 AI 호출은 AI Gateway 단일 경유
- Workspace 사용자 토큰을 업스트림으로 전달 금지(Upstream Auth 분리)
- 강통제 기본값(확장/패키지/네트워크 차단 후 허용)
- 모든 AI 행위는 감사 가능(최소 로그 + 필요시 SIEM 연계)

자세한 설계/리뷰 문서: `architecture/` 참고.

## 빠른 시작(로컬 데모)

로컬에서 **AI Gateway + mock upstream + code-server**를 한 번에 띄우는 데모를 제공합니다.

- 실행: `docker compose up --build`
- 접속: code-server는 `http://localhost:8080`
- Gateway는 `http://localhost:8081`
- Admin Portal은 `http://localhost:8090/admin`

자세한 설정/운영 가이드는 `docs/`를 참고하세요.

