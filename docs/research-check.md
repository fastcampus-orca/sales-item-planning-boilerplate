# 마진 계산 도구

판매가와 비용으로 건당 이익·마진율만 계산한다. 확인값과 추정값을 모두 사용할 수 있으며 후보를 통과·탈락시키지 않는다. 출처와 추정 이유는 시장 조사 노트에 적는다.

## 사용

필요할 때만 실행하며 문서에서 직접 계산해도 된다.

```sh
python3 scripts/check-research.py artifacts/sources/research-screening.json > artifacts/sources/research-check.json
```

## 입력

JSON의 `rules`에는 적용 비용률, `items`에는 상품별 `id`와 `values`를 둔다. 값은 숫자 또는 `{ "value": 숫자 }`로 적는다. 금액은 원, 비율은 소수, ROAS는 배수다.

- `rules`: `product_fee_rate`(상품 수수료율), `shipping_fee_rate`(배송비 수수료율), `ad_share`(광고 기여 비중), `roas`, `loss_rate`(손실충당률).
- `values`: `price`(판매가), `customer_shipping`(고객 배송비), `supply`(공급가), `supplier_shipping`(발송비), `other_cost`(기타 비용).

적용되지 않는 비용은 이유를 문서에 적고 0으로 넣는다. 근거 ID·공급 조건·예산·목표 마진 등은 코드의 필수 입력이 아니다.

## 결과

건당 이익 = 판매가 + 고객 배송비 − 공급가 − 발송비 − 수수료 − 광고비 − 손실충당 − 기타 비용.

마진율 = 건당 이익 ÷ 판매가.

`calculation`에 결과를, 잘못된 입력은 `warnings`에 표시한다. `action`은 항상 `WRITE_DOCUMENT`이며 출처 검증·후보 판정·문서 작성 중단을 지시하지 않는다.

## 참고자료

- 문서 작성 지침: [AGENTS.md](../AGENTS.md)
- 시장 조사 노트 양식: [market-research-template.md](../templates/market-research-template.md)
