# 판매 아이템 기획

스마트스토어 판매 아이템을 조사해 후보를 비교하고, 선정한 아이템의 판매 기획서를 작성하는 프로젝트입니다. 사업 조건과 조사 근거를 바탕으로 수익성·예산·실행 계획을 검토합니다.

작업 지침은 [AGENTS.md](AGENTS.md)를 따릅니다. `CLAUDE.md`는 같은 지침을 가리키는 링크입니다.

## 폴더 구조

```text
sales-item-planning-boilerplate/
├── README.md
├── AGENTS.md            # 공통 작업 지침
├── CLAUDE.md            # AGENTS.md를 가리키는 링크
├── docs/                # 시장조사 실행·검사 규격
├── scripts/             # 수익성·완료 조건 검사
├── templates/           # 문서 양식 3종
├── samples/             # 양식에 맞춰 작성된 샘플 3종
└── artifacts/
    ├── sources/         # 조사 중 내려받은 원본 자료
    ├── assets/          # 웹페이지에 사용할 이미지·폰트 원본
    ├── rules/           # 작업 전 사업 조건과 작업 기준
    ├── drafts/          # 작성·수정 중인 문서 3종
    ├── quality-gate/    # 품질 기준과 검사 기록
    └── final/           # 최종 문서 3종·공유 웹페이지
```

## 공통 작업 규칙

저장 위치는 아래 표를 따릅니다. 같은 파일명이라도 작성 중 문서와 검사를 통과한 최종 문서를 구분합니다.

### 문서 저장

모든 경로는 프로젝트 루트 기준입니다. 문서의 역할에 맞는 아래 파일을 생성하거나 갱신하고, 작업 후 실제 저장한 파일을 알려 줍니다.

| 문서 | 저장 위치 |
| --- | --- |
| 인터뷰로 정한 사업 조건 | `artifacts/rules/business-brief.md` |
| 시장조사 기준 | `artifacts/rules/research-criteria.md` |
| 판매 아이템 선정 기준 | `artifacts/rules/selection-criteria.md` |
| 누적 선별·계산 입력 | `artifacts/sources/research-screening.json` |
| 선별·완료 조건 검사 결과 | `artifacts/sources/research-check.json` |
| 검사 프로그램의 누적 탐색 이력 | `artifacts/sources/research-history.json` |
| 단계별 품질 기준 | `artifacts/quality-gate/criteria.md` |
| 검사·수정 요청·재검사 기록 | `artifacts/quality-gate/quality-review.md` |

| 작업 | 사용할 양식 | 작성·수정할 문서 | 최종 문서 |
| --- | --- | --- | --- |
| 시장조사 | `templates/market-research-template.md` | `artifacts/drafts/market-research.md` | `artifacts/final/market-research.md` |
| 후보 선정 | `templates/item-candidates-template.md` | `artifacts/drafts/item-candidates.md` | `artifacts/final/item-candidates.md` |
| 기획서 작성 | `templates/proposal-template.md` | `artifacts/drafts/sales-item-proposal.md` | `artifacts/final/sales-item-proposal.md` |

- 템플릿에는 항목만 두고, 실제 내용은 담당 문서에 작성합니다.
- `samples/`는 양식별 작성 예시입니다.
- 초안을 갱신하고, 검사를 통과한 문서만 `artifacts/final/`에 복사합니다.
- 같은 작업 파일을 수정하고 이전 내용은 Git으로 관리합니다. 조사 중 내려받은 원본은 `artifacts/sources/`에 보관합니다.
- 시장조사 담당 에이전트는 [실행 검사 규격](docs/research-check.md)에 따라 상품별 소싱·수익성을 먼저 검사하고, 통과한 상품만 상세 조사합니다. 검사 프로그램은 Python 3.9 이상에서 실행합니다.

### 검사 기록

실제 문서를 품질 기준과 대조하고 `quality-review.md`에 아래 내용을 기록합니다.

- 검사한 문서
- 항목별 통과·실패와 이유
- 결과: 통과 또는 반려
- 반려 사유·수정 내용·재검사 결과

### 웹페이지와 공유

웹페이지는 `artifacts/final/share/index.html`에 저장합니다. 이미지·폰트 원본은 `artifacts/assets/`에 두고, 실제 사용하는 파일만 `artifacts/final/share/assets/`에 복사해 페이지와 상대 경로로 연결합니다. 공유할 때는 `artifacts/final/share/`만 배포합니다. 원자료·초안·사업 조건 파일은 배포하지 않습니다.

페이지 점검 결과와 공유 URL은 현재 실행의 검사 기록에 추가합니다. 기획서가 수정되면 재검사 후 페이지에도 반영합니다.

### 스킬 파일

프로젝트에 설치하는 스킬 원본과 참조 파일은 `.agents/skills/<스킬명>/`에 두고, `.claude/skills/<스킬명>`은 원본을 가리키는 상대 경로 심볼릭 링크로 연결합니다. 기존 설치·수정은 보존합니다.
