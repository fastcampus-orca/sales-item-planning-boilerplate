#!/usr/bin/env python3
"""Calculate per-item profit and margin; never decide research completion."""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def amount(value, label, rate=False):
    if isinstance(value, dict):
        value = value.get('value')
    try:
        if value is None or isinstance(value, bool):
            raise ValueError
        value = Decimal(str(value))
        if not value.is_finite() or value < 0 or (rate and value > 1):
            raise ValueError
        return value
    except (ValueError, InvalidOperation):
        raise ValueError(f'{label}: 유효한 확인값 또는 추정값을 입력하세요') from None


def check(data, root=None):
    result = {'action': 'WRITE_DOCUMENT', 'items': [], 'warnings': []}
    rules = data.get('rules', {})
    for index, item in enumerate(data.get('items', []), 1):
        row = {'id': item.get('id', str(index)), 'calculation': {}, 'warnings': []}
        result['items'].append(row)
        try:
            values = item.get('values', {})
            v = {key: amount(values.get(key), key) for key in
                 ('price', 'customer_shipping', 'supply', 'supplier_shipping', 'other_cost')}
            r = {key: amount(rules.get(key), key, rate=True) for key in
                 ('product_fee_rate', 'shipping_fee_rate', 'ad_share', 'loss_rate')}
            price = v['price']
            if price == 0:
                raise ValueError('price: 마진율 계산에는 0보다 큰 판매가가 필요합니다')
            ad = Decimal(0)
            if r['ad_share']:
                roas = amount(rules.get('roas'), 'roas')
                if roas == 0:
                    raise ValueError('roas: 광고 기여가 있으면 0보다 커야 합니다')
                ad = price * r['ad_share'] / roas
            fee = price * r['product_fee_rate'] + v['customer_shipping'] * r['shipping_fee_rate']
            loss = price * r['loss_rate']
            profit = price + v['customer_shipping'] - v['supply'] - v['supplier_shipping'] - fee - ad - loss - v['other_cost']
            row['calculation'] = {'fee': fee, 'ad': ad, 'loss': loss,
                                  'profit': profit, 'margin': profit / price}
        except (ValueError, TypeError, AttributeError, ArithmeticError) as error:
            row['warnings'].append(str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = check(json.loads(args.input.read_text()))
    except (OSError, ValueError, TypeError, AttributeError) as error:
        result = {'action': 'WRITE_DOCUMENT', 'items': [],
                  'warnings': [f'입력을 보완하거나 문서에서 직접 계산하세요: {error}']}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
