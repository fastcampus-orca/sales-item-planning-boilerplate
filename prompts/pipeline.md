판매 아이템 기획서를 처음부터 끝까지 만들어 줘.

## 실행과 저장

- 새 전체 실행을 시작할 때 Orca Run을 생성하고, 반환된 실제 `runId`를 모든 워커에게 전달해 줘.
- 폴더와 `.md` 확장자는 유지하고, 초안·최종 문서·검사 기록은 `문서이름_ID.md` 형식으로 저장해 줘. 파일명에는 실제 `runId`에서 맨 앞의 `run_`만 뺀 값을 사용하고, 이번 실행에서는 이 규칙을 기본 파일명보다 우선해 줘.
  예: 반환된 ID가 `run_a1b2c3d4e5f6`이면 `market-research.md` → `market-research_a1b2c3d4e5f6.md`.
- 개별 실행의 기존 파일과 다른 Run의 결과는 덮어쓰지 마. 사업 조건·기준·양식·샘플은 아래 참고자료를 그대로 사용해 줘.
- 다음 단계 입력·문서 간 참조 링크·품질 검사 대상은 같은 ID가 붙은 이번 실행의 문서로 연결해 줘.
- 중단 후 재개·반려 후 수정·재검사는 같은 Run과 파일명을 유지하고, 검사 기록은 누적해 줘.

## 작업 흐름

1. 시장 조사 노트 → 아이템 후보 비교표 → 판매 아이템 기획서 순서로 워커에게 하나씩 배정해 줘.
2. 각 워커에게 공통 지침과 해당 단계의 확정 기준·양식·샘플, 앞 단계에서 통과한 문서를 전달해 줘.
3. 세부 조건은 기준 문서를 따르고, 양식의 필수 섹션·표 구성을 지켜 줘. 샘플은 구성·표현만 참고해 줘.

## 품질 게이트

- 코디네이터가 실제 문서를 품질 기준과 대조하고 검사 결과와 이유를 기록해 줘.
- 통과한 문서를 최종 폴더에 반영하고 다음 워커에게 넘겨 줘.
- 실패하면 문제 위치·이유·수정 요청을 담당 워커에게 전달하고 재검사해 줘. 코디네이터가 직접 고치지는 마.
- 같은 오류가 반복되면 전달한 기준과 입력을 대조해 원인을 해결한 뒤 이어서 진행해 줘.

## 완료 보고

최종 문서 3종과 검사 기록의 경로, 반려가 있었다면 반려 이유와 수정 결과를 알려 줘.
내가 결과를 확인하고 정리를 승인하기 전까지는 작업이 끝난 워커도 종료하거나 터미널을 닫지 마.

#### 참고자료

경로는 프로젝트 루트 기준.

- 공통 지침: `AGENTS.md`
- 저장 규칙: `README.md`
- 사업 조건: `artifacts/rules/business-brief.md`
- 시장조사 기준: `artifacts/rules/research-criteria.md`
- 판매 아이템 선정 기준: `artifacts/rules/selection-criteria.md`
- 품질 기준: `artifacts/quality-gate/criteria.md`
- 시장 조사 노트 양식: `references/templates/market-research-template.md`
- 시장 조사 노트 샘플: `references/samples/market-research-sample.md`
- 아이템 후보 비교표 양식: `references/templates/item-candidates-template.md`
- 아이템 후보 비교표 샘플: `references/samples/item-candidates-sample.md`
- 판매 아이템 기획서 양식: `references/templates/proposal-template.md`
- 판매 아이템 기획서 샘플: `references/samples/proposal-sample.md`
