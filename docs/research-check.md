# 시장조사 실행 검사

공급 조건과 수익성을 먼저 확인하고, 유효 후보를 확보한 경우에만 시장조사를 완료한다. 에이전트는 아래 입력을 조사 기록으로 관리하고 검사 결과에 따라 다음 작업을 정한다.

## 실행 순서

1. 확정한 사업 조건·시장조사 기준을 읽고 조사 한도를 입력한다. 고객·구매 목적이나 계산 전제가 빠졌으면 필요한 결정만 확인한다.
2. 공개 단가와 요청한 판매 방식의 거래 조건을 함께 확인할 수 있는 공급 경로부터 찾는다. 국내 위탁판매라면 고객 직배송, 최소 주문 수량, 반품 책임, 회원 자격·선충전 조건을 먼저 확인한다. 조회 가능 여부와 실제 발주 자격을 구분한다.
3. 상품별 소매 상세와 공급 상세를 짝지어 가격·비용을 기록하고 검사를 실행한다. 부가세·옵션·수량·배송비를 통일하며, 높은 판매가만 골라 통과시키지 않는다.
4. `READY_FOR_DETAIL` 상품만 수요·경쟁을 조사한다. 결과가 확정 기준을 충족하면 해당 근거를 추가하고 다시 검사한다.
5. `COMPLETE`에서만 유효 후보를 양식에 옮긴다. 부족한 경우에는 결과 문서를 완성하지 않고 아래 후속 행동을 따른다.

```sh
python3 scripts/check-research.py artifacts/sources/research-screening.json > artifacts/sources/research-check.json
```

종료 코드 `0`은 완료, `2`는 조사 진행 또는 미완료, `1`은 입력 오류다. 근거 파일의 존재와 계산을 검사하며, 원문 진위·동일 상품 여부·확정 기준과 입력값의 일치는 에이전트가 원문과 대조해야 한다.

## 후속 행동

| 검사 결과 | 다음 작업 |
| --- | --- |
| `CONTINUE_SCREENING` | 남은 한도 안에서 아직 확인하지 않은 상품 선별 |
| `CHANGE_SUPPLIER` | 탈락 원인을 해결할 다른 실제 공급사로 전환. 같은 공급사의 다른 쇼핑몰은 제외 |
| `RESEARCH_READY_ITEMS` | 선별을 통과한 상품의 수요·경쟁 조사부터 마무리 |
| `STOP_INCOMPLETE` | 조사 종료. 유효 후보 수·핵심 탈락 원인·재개에 필요한 조건만 보고 |
| `INVALID_INPUT` | 입력을 원문과 대조해 수정. 누락값을 0으로 메우지 않음 |
| `COMPLETE` | 유효 후보로 시장 조사 노트 작성 후 문서 품질 검사 |

조사 기록은 누적한다. 파일명·에이전트·공급처를 바꿔도 수집 건수·소요 시간·탈락 이력을 초기화하지 않는다. 검사는 `artifacts/sources/research-history.json`을 자동 생성해 이전 상품의 삭제·교체와 누적 시간 감소를 거부한다. 이 파일을 지워 한도를 우회하지 않는다. 한도 소진 후 자동 재시작하지 않는다. 새 근거 또는 사용자가 확정한 조건 변경 없이 동일한 실패 경로로 돌아가지 않는다.

## 입력 규격

입력 JSON은 `rules`, `elapsed_minutes`, `evidence`, `items`로 구성한다. 금액은 원, 비율은 소수, ROAS는 배수다. `elapsed_minutes`는 실제 도구 실행과 조사에 쓴 누적 분수이며 재개해도 합산한다. 숫자는 확정한 기준에서 옮기며 검사 편의를 위해 바꾸지 않는다.

### 확정 기준 — `rules`

| 필드 | 내용 |
| --- | --- |
| `customer`, `purchase_purpose`, `approval` | 고객·구매 목적·확정 기준의 근거 ID |
| `target_profit`, `fixed_cost`, `order_limit`, `min_margin` | 월 목표 이익·월 고정비·처리 가능한 월 주문 수·명시적으로 정한 최소 마진율. 최소 마진율을 쓰지 않기로 했다면 0 |
| `product_fee_rate`, `shipping_fee_rate` | 상품대금·배송비 수입 각각의 적용 수수료율 |
| `ad_share`, `roas`, `loss_rate`, `settlement_share` | 광고 기여 비중·ROAS·매출 대비 손실충당 비율·정산 시차 동안 먼저 지급할 원가 비중 |
| `working_budget`, `ad_budget`, `loss_budget`, `operating_budget` | 월 운전자금·광고비·손실충당 한도, 고정비까지 포함한 전체 운영자금 한도 |
| `min_candidates` | 완료에 필요한 유효 후보 수 |
| `max_screened`, `max_routes`, `route_fail_limit`, `max_minutes` | 전체 선별 상품·실제 공급사·공급사별 탈락·전체 조사 시간의 상한 |
| `required_conditions` | `fulfillment`(배송·제공 방식), `order_unit`(주문 단위), `returns`(반품 책임), `eligibility`(이용 자격), `tax_shipping`(세금·배송 조건)을 반드시 포함하고 사업별 필수 조건 추가 |

이 계산은 단일 품목이 목표 이익을 달성할 수 있는지 비교한다. 여러 품목의 예산·수익을 합치는 모델로 해석하지 않는다. 월별 한도가 다르면 각 월의 입력으로 따로 검사한다. 다른 비용 구조가 필요하면 산식을 먼저 합의하고 검사도 맞춰 변경한다.

### 근거 — `evidence`

근거 ID를 키로 하고 다음 항목을 기록한다.

- `kind`: 원문에서 확인한 사실은 `observed`, 사용자가 확정한 조건·계획 가정은 `approved`.
- `file`: 프로젝트 안에 저장한 원본의 상대 경로.
- `detail`: 확인한 값·적용 조건 또는 사용자가 확정한 내용과 문서 내 위치.
- `url`: `observed`일 때 실제로 연 원문 URL.

### 상품 — `items`

상품별 객체를 배열에 누적한다. 같은 상품의 소매 판매처를 여러 개 찾았다고 상품 수를 늘리지 않는다.

- `id`, `product_key`, `supplier_id`: 조사 번호, 제조사·모델·옵션·구성 수량을 합친 상품 식별값, 실제 공급사 식별값.
- 가격 수집 전에 제외한 상품: `excluded_reason`, `excluded_evidence`에 탈락 사유와 근거 ID를 기록하고 비용을 억지로 채우지 않는다.
- `checks`: `identity`와 필수 소싱 조건별로 `{ "pass": true, "evidence": "근거 ID" }`를 기록한다. 수요·경쟁 조사 후 `demand`, `competition`도 같은 형식으로 추가한다. 미확인을 통과로 표시하지 않는다.
- `values`: 아래 금액마다 `{ "value": 금액, "evidence": "근거 ID" }`를 기록한다.
- `product_fee_evidence`, `shipping_fee_evidence`: 적용 수수료 원문 근거 ID.

| 금액 필드 | 내용 |
| --- | --- |
| `price`, `customer_shipping` | 실제 소매가·고객에게 받는 배송비 |
| `supply`, `supplier_shipping` | 동일 판매 단위의 부가세 포함 공급가·공급사 배송비 |
| `other_cost`, `other_upfront` | 그 밖의 건당 비용 전체·그중 정산 전에 지급할 금액. 이익 계산에는 전체 비용만 한 번 반영 |
| `prepay_minimum`, `prepay_increment` | 공급사 최소 선충전액·충전 단위. 미발생이 확인된 경우에만 0 |

## 계산과 완료 판정

- 수수료 = 소매가 × 상품 수수료율 + 배송비 수입 × 배송비 수수료율.
- 광고비 = 소매가 × 광고 기여 비중 ÷ ROAS. 광고를 쓰지 않기로 확정한 경우 0.
- 건당 이익 = 소매가 + 배송비 수입 − 공급가 − 공급사 배송비 − 수수료 − 광고비 − 손실충당 − 기타 비용.
- 필요 이익은 월 목표·고정비를 주문 한도로 나눈 값과 최소 마진율에 필요한 이익 중 큰 값이다. 이를 빼고 남는 금액이 허용 매입원가다.
- 실제 이익으로 필요한 주문 수를 올림 계산하고 운전자금·광고비·손실충당·총 운영자금 한도를 각각 검사한다. 선충전 최소액·충전 단위도 운전자금에 반영한다.
- 소싱·수익성·수요·경쟁을 모두 통과한 상품만 유효 후보로 센다. 검사 통과와 문서 양식·출처 품질 검사는 별개이며 둘 다 충족해야 최종본을 만든다.

## 참고자료

- 공통 지침: [AGENTS.md](../AGENTS.md)
- 검사 프로그램: [check-research.py](../scripts/check-research.py)
- 시장 조사 노트 양식: [market-research-template.md](../templates/market-research-template.md)
