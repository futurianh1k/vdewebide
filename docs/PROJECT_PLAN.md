# 프로젝트 개발 계획 — 금융권 온프레미스 Cursor-like Web IDE (VDE)

작성일: 2026-01-07  
버전: 초안 v0.1

## 0. 목표(왜/무엇을)

금융권 폐쇄망(VDE) 환경에서 **웹 기반 IDE(code-server)** 로 개발 경험을 제공하면서,
AI 기능(Tab/Agent/Chat/RAG)은 **AI Gateway 단일 통제 지점**으로 수렴시켜
보안·감사·운영·비용 통제를 만족하는 “온프레미스 Cursor-like” 솔루션을 구축한다.

## 1. 비협상 원칙(Non-negotiables)

`architecture/AGENTS.md` 기준:

- 외부 인터넷 의존성 추가 금지(폐쇄망 전제)
- Workspace → AI Gateway 단일 경유 유지
- Workspace 사용자 토큰을 Upstream에 전달 금지(Upstream auth 분리)
- JWKS 캐시/리프레시 + fail-open은 승인된 경우만
- Streaming DLP 기본값은 pre_only
- 감사 DB 월별 파티셔닝 + retention purge 절차
- OpenAPI pinned + verify로 drift 차단

## 2. 범위 정의(현재 확정/미확정)

### 2.1 지금 바로 할 수 있는 것(고객 결정 없이 가능한 MVP)

- Web IDE(code-server) 기반 “작동하는 데모”
- AI Gateway(FastAPI) 기반 “단일 통제 지점” 작동
- Mock upstream(탭비/LLM/RAG 대체)으로 end-to-end 통신 검증
- 기본 보안 가드레일:
  - Authorization 토큰 업스트림 미전달
  - DLP pre-check로 비밀키/토큰 패턴 차단
  - 최소 감사 이벤트 생성(확장 가능)

### 2.2 고객 정보가 필요해 MVP 이후에 확정할 것

- SSO/JWT 발급 주체(issuer/audience/JWKS 제공 방식)
- Upstream auth 표준(mTLS vs static token)
- DLP 정책(차단/마스킹 기준, PII 룰셋, 오탐 처리)
- 감사 원문 저장 여부(프롬프트/응답 저장, 보관 기간, SIEM 연계)
- RAG Index 권한/운영 방식(인덱서 전용 계정 여부)

## 3. 아키텍처(수직 슬라이스 기준)

### 3.1 런타임 구성요소(최소)

- **IDE(Workspace)**: code-server (웹 IDE)
- **AI Gateway**: 인증/인가, 정책 라우팅, DLP, 감사/메트릭
- **Upstream Services**: Tab/Agent/Chat/RAG (MVP에서는 mock으로 대체)

### 3.2 흐름

1) 사용자가 IDE에서 AI 기능 호출  
2) IDE는 AI Gateway로만 요청(egress 단일화)  
3) Gateway는 AuthN/Z → DLP → 라우팅 → Upstream 호출  
4) 응답/사용량/정책 결과를 감사/메트릭으로 기록  

## 4. 로드맵(마일스톤)

### M0 — MVP 데모(1~2주)

- 산출물
  - `docker-compose.yml`로 IDE+Gateway+Mock Upstream 구동
  - Gateway 기본 테스트(인가/DLP/헬스/메트릭)
  - 개발 환경 가이드(Windows/Ubuntu)
- 성공 기준
  - IDE에서 Gateway 호출이 가능한 형태로 확인
  - Gateway가 업스트림에 Workspace 토큰을 전달하지 않음을 증명
  - DLP 차단 이벤트가 감사/메트릭에 반영됨

### M1 — 파일럿(폐쇄망 VDE 설치/운영) (2~6주)

- 네트워크 정책(Workspace → Gateway 단일 egress) 및 서비스 간 통신 표준화
- Upstream auth(mTLS/내부 토큰) 적용
- JWKS 캐시/리프레시 운영 설정 확정
- 감사 DB 적재(Postgres) + 월별 파티션 + Retention job 운영화

### M2 — 제출/운영 레디(6~12주)

- DLP 룰 확장(PII/내부 분류 태그) + 마스킹 정책
- SIEM 연계용 감사 로그 필드 표준화
- OpenAPI pinned + verify를 CI에 고정
- DR/백업/비용통제(토큰 모니터링/쿼터) 체계 구축

### M3 — 제품화(지속)

- Portal/SSO/워크스페이스 프로비저닝(tenant/project/workspace lifecycle)
- 관리자 기능(정책 배포/승인/감사 조회) 및 Audit UI
- Workspace 표준 이미지(확장 사전 설치/런타임 설치 금지) 빌드 파이프라인

## 5. 품질/보안 기본 정책(초기부터 강제)

- 시크릿: `.env`/코드 하드코딩 금지, Secret 마운트 방식 기본
- 로그: 토큰/비밀번호/PII 원문 기록 금지(최소 메타데이터만)
- 접근제어: role 기반으로 엔드포인트 권한 강제(`/v1/agent` 등)
- 테스트: 최소 보안 동작(인가/DLP/헬스/메트릭) 자동화

## 6. 참고(외부 구성요소)

- Web IDE: code-server — `https://github.com/coder/code-server`
- AI Gateway 프레임워크: FastAPI — `https://fastapi.tiangolo.com/`
- 메트릭: Prometheus Python client — `https://github.com/prometheus/client_python`

