# 판매 아이템 기획

Orca의 순차 파이프라인으로 시장 조사 노트·아이템 후보 비교표·판매 아이템 기획서를 만들고, 기획서를 웹페이지로 공유하는 프로젝트입니다.

## 제공 저장소

| 저장소 | 용도 |
| --- | --- |
| `sales-item-planning-boilerplate` | Fork해서 시작할 기본 뼈대 |
| `sales-item-planning` | 전체 실행 결과가 포함된 완성 예시 |

## 시작하기

1. 기본 뼈대를 Fork → Clone하고 Orca에서 열기.
2. 에이전트에게 프로젝트의 지침과 폴더 구조를 읽고 프로젝트를 파악하도록 요청.
3. 스킬 설치 → 사업 조건·템플릿·작업 기준 설정 → 개별 작업 → 품질 기준 설정 → 전체 실행 → 웹페이지 공유.

README·AGENTS.md·CLAUDE.md와 템플릿 3종을 제공합니다. 빈 폴더의 `.gitkeep`은 Git에 폴더를 남기기 위한 파일입니다. `AGENTS.md`가 에이전트 지침 원본이고 `CLAUDE.md`는 그 원본을 가리키는 심볼릭 링크입니다. 스킬도 같은 구조로 원본은 `.agents/skills/`, `.claude/skills/`는 링크입니다.

## 폴더 구조

```text
sales-item-planning-boilerplate/
├── README.md
├── AGENTS.md            # 공통 작업 지침
├── CLAUDE.md            # AGENTS.md를 가리키는 링크
├── templates/           # 제공 템플릿 3종
├── samples/             # 양식에 맞춰 작성된 샘플 3종
├── prompts/             # 사용한 파이프라인 실행 프롬프트
└── artifacts/
    ├── sources/         # 조사 중 내려받은 원본 자료
    ├── assets/          # 웹페이지에 사용할 이미지·폰트 원본
    ├── rules/           # 작업 전 사업 조건과 작업 기준
    ├── drafts/          # 작성·수정 중인 문서 3종
    ├── quality-gate/    # 품질 기준과 검사 기록
    └── final/           # 최종 문서 3종·공유 웹페이지
```

## 공통 작업 규칙

개별 작업 에이전트와 코디네이터·워커는 작업 전에 이 규칙을 읽습니다. 요청에는 할 일과 입력 자료를 주고, 저장 위치·파일명은 아래 규칙을 적용합니다. 사용자가 연결한 실제 입력 파일을 읽으며 파일명이 같은 문서의 초안과 최종 문서를 구분합니다.

### 문서 저장

모든 경로는 프로젝트 루트 기준입니다. 문서의 역할에 맞는 아래 파일을 생성하거나 갱신하고, 작업 후 실제 저장한 파일을 알려 줍니다.

| 문서 | 저장 위치 |
| --- | --- |
| 인터뷰로 정한 사업 조건 | `artifacts/rules/business-brief.md` |
| 시장조사 기준 | `artifacts/rules/research-criteria.md` |
| 판매 아이템 선정 기준 | `artifacts/rules/selection-criteria.md` |
| 단계별 품질 기준 | `artifacts/quality-gate/criteria.md` |
| 검사·수정 요청·재검사 기록 | `artifacts/quality-gate/quality-review.md` |
| 전체 실행에 사용한 제공 프롬프트 | `prompts/pipeline.md` |

| 작업 | 사용할 양식 | 작성·수정할 문서 | 최종 문서 |
| --- | --- | --- | --- |
| 시장조사 | `templates/market-research-template.md` | `artifacts/drafts/market-research.md` | `artifacts/final/market-research.md` |
| 후보 선정 | `templates/item-candidates-template.md` | `artifacts/drafts/item-candidates.md` | `artifacts/final/item-candidates.md` |
| 기획서 작성 | `templates/proposal-template.md` | `artifacts/drafts/sales-item-proposal.md` | `artifacts/final/sales-item-proposal.md` |

- 템플릿에는 항목만 두고, 실제 내용은 담당 문서에 작성합니다.
- `samples/`는 양식에 맞춰 작성된 샘플입니다. 소재와 수치가 가상 값이므로 내용·수치·출처를 문서에 옮기거나 근거로 쓰지 않습니다.
- 코디네이터는 각 워커에게 이 지침과 담당 작업에 필요한 기준·양식, 앞 단계에서 통과한 문서를 전달합니다. 새 워커는 이전 대화를 모른다고 가정합니다.
- 전체 실행에서는 기존 초안을 새 내용으로 갱신하고, 검사를 통과한 문서만 `artifacts/final/`에 복사합니다.
- 같은 작업 파일을 수정하고 이전 내용은 Git으로 관리합니다. 조사 중 내려받은 원본은 `artifacts/sources/`에 보관합니다.

### 검사 기록

코디네이터는 워커의 완료 보고만으로 통과시키지 않고, 실제 문서를 품질 기준과 대조합니다. 검사할 때마다 `quality-review.md`에 아래 내용을 추가합니다.

- 검사한 문서
- 항목별 통과·실패와 이유
- 결과: 통과 또는 반려
- 반려했다면 워커에게 보낸 수정 요청과 재검사 결과
- 통과했다면 다음에 배정한 워커

### 웹페이지와 공유

웹페이지는 `artifacts/final/share/index.html`에 저장합니다. 이미지·폰트 원본은 `artifacts/assets/`에 두고, 실제 사용하는 파일만 `artifacts/final/share/assets/`에 복사해 페이지와 상대 경로로 연결합니다. 공유할 때는 `artifacts/final/share/`만 배포합니다. 원자료·초안·사업 조건 파일은 배포하지 않습니다.

페이지 점검 결과와 공유 URL은 현재 실행의 검사 기록에 추가합니다. 기획서가 수정되면 재검사 후 페이지에도 반영합니다.

### 스킬 설치

`grill-me`·`grilling`은 실습에서 함께 설치합니다. 스킬 원본과 참조 파일은 프로젝트의 `.agents/skills/<스킬명>/`에 두고, `.claude/skills/<스킬명>`은 해당 원본을 가리키는 상대 경로 심볼릭 링크로 연결합니다. 기존 설치·수정은 보존하고 두 위치에서 파일을 읽을 수 있는지 확인합니다.

`orchestration`·`orca-cli`는 Part 4의 기존 설치를 사용합니다. 스킬 폴더나 설치 완료 상태를 기본 뼈대에 미리 만들어 두지 않습니다.
