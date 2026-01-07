# 변경 이력 — aicontainers

작성일: 2026-01-07  
브랜치: `aicontainers`  
변경 성격: **중대한 변화(AI Assistant용 온프레미스 컨테이너 스택(qdrant/tabby/vLLM) 준비)**

## 1) 내가 요구한 내용

- `aicontainers` 브랜치를 만들고, code-server에서 AI assistant를 사용하기 위한 준비를 한다.
- 온프레미스 환경에서 아래 컴포넌트를 사용할 수 있는지 검토하고, 필요 시 포함한다:
  - Qdrant(벡터 DB)
  - Tabby(코드 자동완성)
  - vLLM(OpenAI compatible 서버)

## 2) 내가(에이전트) 답한 내용(요약)

- 결론: **온프레미스 환경에서 사용 가능**하다.
  - Tabby/Qdrant/vLLM은 모두 컨테이너로 구동 가능하며 외부 인터넷 없이도 운영 가능(모델/이미지/아티팩트 사내 미러 필요).
  - 단, vLLM은 보통 GPU/드라이버/NVIDIA Container Toolkit이 필요하고, 모델 라이선스/배포 정책을 선행 확정해야 한다.
- 구현 전략: “기존 Gateway 단일 통제 지점” 원칙을 유지한 채,
  - Tabby: `/v1/autocomplete` upstream으로 연결(혹은 별도 라우트)
  - Chat/Agent: vLLM(OpenAI compatible) 또는 내부 LLM API로 라우팅
  - RAG: Qdrant + 인덱서(추후) + Gateway 권한/감사 통제

## 3) 수정/추가 내용(예정)

- `docker-compose.yml`에 **옵션(프로필) 기반** AI 컨테이너 스택 추가
  - `qdrant` (profile: `ai`)
  - `tabby` (profile: `ai`)
  - `vllm` (profile: `ai-gpu`)
- 문서: 온프레미스 제약/전제(GPU, 모델 배포, 리소스, 보안 통제) + PoC 단계별 계획

