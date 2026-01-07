# AI Assistant (On-Prem) 준비 — qdrant / tabby / vLLM

## 0) 결론: 온프레미스에서 가능한가?

가능합니다. 다만 **모델/이미지/아티팩트를 사내에서 공급**할 수 있어야 하며(폐쇄망), vLLM은 보통 **GPU 환경**이 필요합니다.

## 1) 컴포넌트 역할(현 아키텍처 기준)

- **code-server(Workspace)**: 사용자가 코드를 편집하는 IDE. (현재 PoC의 workspace)
- **AI Gateway**: 인증/인가, DLP, 감사, 라우팅을 수행하는 **단일 통제 지점**.
- **Tabby**: 코드 자동완성(autocomplete) 제공.
- **vLLM**: OpenAI compatible API로 LLM 서빙(채팅/에이전트/요약 등).
- **Qdrant**: RAG 벡터 검색(문서/코드 임베딩 인덱스).

## 2) 온프레미스 제약/전제 체크리스트(필수)

- **이미지 공급**: docker registry mirror/프라이빗 레지스트리
- **모델 공급**: 모델 파일 사내 저장소(라이선스/내부 배포 승인 포함)
- **GPU**(vLLM): NVIDIA Driver + NVIDIA Container Toolkit, 리소스 할당 정책
- **보안**:
  - Workspace 토큰을 upstream(Tabby/vLLM/Qdrant)으로 직접 전달 금지(현재 원칙 유지)
  - Gateway에서만 upstream 인증/정책/DLP/감사 집행
- **관측/운영**:
  - 모델/벡터DB 상태 점검(health), 비용/쿼터(추후)

## 3) 구현 단계(권장)

### M0 (PoC, 1~3일)

- docker-compose에 qdrant/tabby/vLLM 서비스를 **옵션(profile)** 로 추가
- Gateway 환경변수로 upstream 타겟을 전환 가능하게 구성(기본은 mock 유지)

### M1 (PoC+, 1~2주)

- code-server에서 “AI assistant” 기능이 Gateway를 통해 동작하도록 연결 정리
  - autocomplete: Tabby
  - chat/agent: vLLM(OpenAI compatible)
- ops 레벨에서 최소한의 토글/설정(예: upstream auth)과 감사 이벤트 강화

### M2 (파일럿, 2~6주)

- RAG: 인덱서(문서/레포) + Qdrant + 권한 모델(tenant/project scope) + 감사
- 정책 배포(승인/버전/롤백) 설계

## 4) 참고 자료(출처)

- code-server: `https://github.com/coder/code-server`
- Tabby: `https://github.com/TabbyML/tabby`
- vLLM: `https://github.com/vllm-project/vllm`
- Qdrant: `https://github.com/qdrant/qdrant`

