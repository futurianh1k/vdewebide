# 변경 이력 — feature/vde-onprem-web-ide-mvp

작성일: 2026-01-07  
브랜치: `feature/vde-onprem-web-ide-mvp`  
변경 성격: **신기능(MVP 착수) / 실행 가능한 데모 구성 / 서비스 구조 도입**

## 1) 내가 요구한 내용

- `architecture/` 문서 리뷰를 바탕으로 “금융권 온프레미스 Cursor-like Web IDE” 구현을 시작한다.

## 2) 내가(에이전트) 답한 내용(요약)

- 고객 답변이 없어도, **MVP 수직 슬라이스**로 착수 가능.
- `AI Gateway`를 실제 서비스(`services/gateway`)로 승격하고,
  `docker-compose`로 code-server(Web IDE) + Gateway + mock upstream을 묶어 **로컬 데모**부터 만든다.
- 금융권 제출/운영 관점 리스크(OpenAPI pin, ops 보호, JWT 검증)를 MVP 단계에서 최소 보완한다.

## 3) 수정/추가 내용 요약

- git 저장소 초기화 및 기능 브랜치 생성(브랜치 정책 준수 목적)
- `services/` 서비스 구조 생성:
  - `services/gateway`: Gateway 참조 구현 복제(설계 원본은 `architecture/gateway` 유지)
  - `services/mock_upstream`: 데모용 업스트림 서비스(추가 예정)
- 프로젝트 루트 파일 추가:
  - `.gitignore`
  - `README.md`

## 4) 리스크 및 후속 작업

- OpenAPI pinned 파일이 비어있는 상태(`openapi.json={}`) → generate/verify를 CI에 고정 필요
- ops 엔드포인트 및 헬스/메트릭 경로가 미들웨어에 의해 막힐 수 있는 구조 → 경로 우회 처리 필요
- JWT/JWK 처리 구현의 잠재 오류 가능성 → 테스트로 보증 및 수정 필요

