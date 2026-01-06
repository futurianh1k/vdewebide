# 아키텍처 문서 리뷰 & 프로젝트 개발 계획 (v0.3)

작성일: 2026-01-07  
대상 범위: `architecture/` 폴더 내 문서 및 참조 구현(`architecture/gateway/`)

## 1. 한 줄 요약

현재 문서는 금융권 VDE 환경에서 **Workspace(IDE)와 AI Runtime을 분리**하고 **AI Gateway 단일 통제 지점**으로 보안/감사/정책을 집행하는 방향이 일관되게 정리되어 있습니다.  
다만, **OpenAPI pin 산출물(`openapi.json`)이 비어 있음**, **운영 보호가 필요한 ops 엔드포인트의 데모 수준 보호**, **JWT 검증 구현의 잠재 오류** 등 “제출/운영 수준” 관점에서 바로 보완해야 할 항목이 확인됩니다.

## 2. 문서 세트 구성(읽은 자료)

- **PRD**: `architecture/PRD.md`
- **운영/제출 강화 노트**: `architecture/docs/FINANCIAL_SUBMISSION_NOTES.md`
- **Non-negotiables(개발 가드레일)**: `architecture/AGENTS.md`
- **Infra 메모**: `architecture/infra/NOTES.md`
- **Gateway 운영 가이드**: `architecture/gateway/README.md`
- **표준 이미지 설계서(PDF)**: `architecture/newarchitecture_금융권 Vde 워크스페이스 표준 이미지 설계서.pdf`  
  - 로컬에서 `pdftotext`로 변환하여 검토(텍스트 변환본은 `/tmp/vde_arch_pdf.txt`)

## 3. 목표/범위 정합성(문서 간 일치 여부)

### 3.1 핵심 원칙(문서 공통)

- **분리 원칙**: Workspace(IDE) ≠ Model/AI Runtime
- **단일 진입점**: Workspace의 AI 호출은 **AI Gateway 단일 경유**
- **불변 이미지**: 개발 중 Workspace를 인플레이스 업데이트하지 않음
- **강통제 기본값**: 확장/패키지/네트워크 기본 차단 후 허용
- **Upstream Auth 분리**: Workspace 사용자 토큰을 업스트림(모델/탭비 등)에 전달 금지

위 원칙은 PRD/제출노트/PDF/AGENTS에 모두 나타나며, `architecture/gateway/app/main.py`의 프록시 구현도 “Workspace 토큰을 업스트림에 전달하지 않음”을 명시적으로 구현합니다.

### 3.2 AI Gateway 기능 요구사항 ↔ 참조 구현 매핑

- **JWT/JWKS 인증 + 캐시/리프레시 + Fail-open/close 정책**: 문서 O / 코드 O
- **Streaming DLP (pre + incremental 옵션)**: 문서 O / 코드 O
- **감사 로그 + 월별 파티셔닝 + Retention/ILM**: 문서 O / 코드 O(스키마/파티션 생성/드롭)
- **OpenAPI 고정(pinned) + drift 검증**: 문서 O / 스크립트 O / **산출물(핀 파일) 미완성**

## 4. 발견 사항(리스크/갭) — 제출/운영 관점

### 4.1 OpenAPI pin 산출물 미완성(High)

- `architecture/gateway/openapi/openapi.json`이 현재 `{}` 입니다.
- 스크립트(`generate_openapi.py`, `verify_openapi.py`)는 준비되어 있으나,
  - 제출/운영에서 “스펙 고정 + drift 차단”을 주장하려면 **실제 pinned 스펙이 반드시 커밋되어야** 합니다.

### 4.2 ops 엔드포인트 보호(High)

- `/ops/retention/purge`는 데모 수준으로 `x-ops-key: change-me` 헤더 키를 요구합니다.
- 문서에서는 운영 시 mTLS/관리자 스코프 보호를 요구하므로, 제출/운영 환경에서는:
  - 네트워크 레벨(mTLS/mesh/ACL) + 애플리케이션 레벨(RBAC)로 보호하거나
  - 별도 운영 잡/배치로 분리하는 방식이 필요합니다.

### 4.3 JWT 검증 구현의 잠재 오류/미완(High)

참조 구현에서 PyJWT로 JWK를 변환하는 로직이 `key["kty"]` 기반으로 알고리즘을 선택합니다.  
일반적으로 `kty`는 `"RSA"` 같은 키 타입이며, 알고리즘 선택/파싱 로직이 의도대로 동작하지 않을 수 있습니다. (또한 sync 경로에 `asyncio` import 누락 정황이 있습니다.)

→ **제출/운영 기준에서는 “정상 토큰/만료/키 롤오버/알고리즘” 테스트 케이스로 보증**하는 것이 안전합니다.

### 4.4 DLP 정책(범위/행동) 확장 필요(Medium~High)

- 현재 DLP 룰은 “block 위주”이며 룰 셋이 최소(예: AWS Key, Private Key, Bearer token)입니다.
- PDF/PRD에서는 PII(주민번호/계좌/카드 등), 사내 분류 태그 기반 차단/마스킹까지 언급합니다.

→ 금융권 제출용이라면 **룰 확장 + 마스킹 정책(allow/mask/block) + 운영 튜닝(오탐/지연)** 계획이 필요합니다.

### 4.5 감사 적재(스키마/타입)와 운영 승인 프로세스(Medium)

- 감사 이벤트는 stdout + DB 적재 구조로 되어 있으나, 운영에서는:
  - DB 연결 실패 시 동작(버퍼링/유실 허용 범위)
  - `extra`(JSONB) 적재 타입/인코딩 호환성
  - Retention purge의 운영 승인/변경관리 절차
  - SIEM 연계(필드 표준화)
  을 명확히 해야 합니다.

### 4.6 문서에 있으나 아직 구현/산출물이 부족한 항목(Medium)

- **레이트리밋/쿼터**(프로젝트·사용자·워크스페이스 단위)
- **K8s 매니페스트/네트워크 정책/DR 시나리오**(PRD 산출물에 있으나 폴더 내 부재)
- **Workspace 표준 이미지(Dockerfile/빌드 파이프라인/확장 패키지)** 구현물(현재는 PDF 설계만 존재)

## 5. 개발 계획(권장 로드맵)

### 5.1 마일스톤 0 — “문서 ↔ 구현” 정합성 확보 (1~3일)

- Gateway의 핵심 동작을 “제출 가능한 형태”로 증명
  - OpenAPI pinned 생성 및 고정
  - JWKS 캐시/리프레시/Fail 정책 테스트
  - DLP pre/stream 모드 테스트
  - Audit 파티션 생성/적재 테스트

산출물
- `gateway/openapi/openapi.json` 실 스키마
- 최소 테스트 스위트(인증/정책/감사)

### 5.2 마일스톤 1 — 운영 보안 하드닝 (1~2주)

- ops 엔드포인트 운영 보호 방식 확정(예: mesh+mTLS+RBAC 또는 배치 잡 분리)
- JWT 검증 로직 정리(키 타입/알고리즘/키 롤오버) + 보안 요구사항(issuer/audience) 확정
- DLP 룰 확장(PII/내부 분류 태그) 및 마스킹/차단 정책 확정
- 감사 로그 표준화(PII 최소화, SIEM 필드 매핑, 보관 정책)

### 5.3 마일스톤 2 — Infra/K8s “제출 패키지” 구성 (2~4주)

- Gateway 및 백엔드(autocomplete/agent/chat/rag)의 배포 매니페스트
- 네트워크 정책(Workspace → Gateway 단일 egress) 및 서비스 간 mTLS 표준
- 모니터링/비용 추적(Prometheus 지표, 알람)
- DR/백업(Workspace PVC snapshot, Gateway DNS 절체 시나리오)

### 5.4 마일스톤 3 — Workspace 표준 이미지 구현 (2~6주, 병렬 가능)

PDF 설계서를 코드로 “재현 가능”하게 만들기:
- base 이미지/패키지/로케일/사용자 권한(UID 고정) 반영
- code-server 설치/설정(telemetry/auto-update off, 프록시 SSO 전제)
- VSIX 사전 설치 및 런타임 설치 금지(읽기 전용 정책)
- opencode 설정(JSON 고정, AI Gateway만 지정, 시크릿은 `/run/secrets/*`로 마운트)

### 5.5 마일스톤 4 — 포털/SSO 연동 및 운영 프로세스 (선택, 범위 확정 필요)

- Web Portal에서 Workspace 생성/접속, 사용자/프로젝트/워크스페이스 claims 발급
- RBAC(Developer/Admin/Auditor) 및 감사 조회 UI/Export
- 변경관리(정책 버전, 이미지 버전, 릴리즈 승인) 프로세스 문서화

## 6. 당장 확정이 필요한 질문(결정 없으면 설계가 흔들리는 지점)

- SSO/토큰 발급 주체는 무엇인가요? (Issuer, Audience, JWKS 제공 방식)
- `tenant/project/workspace`의 생성·수명주기(삭제/보관) 정책은?
- DLP 정책은 “차단”이 기본인가요, “마스킹”이 기본인가요?
- 감사 원문 저장 정책(프롬프트/응답 저장 여부)은 규정상 어떻게 결정되나요?
- Upstream Auth는 `static_bearer`가 기본인가요, `mtls`가 기본인가요?
- Retention 기간(예: 180/365일) 및 purge 승인 프로세스는?

## 7. 참고(외부 도구/자료)

- PDF 텍스트 변환: `pdftotext` (Poppler utilities) — `https://poppler.freedesktop.org/`
- 보안/감사 일반 참고: OWASP Secure Coding Practices — `https://owasp.org/`

