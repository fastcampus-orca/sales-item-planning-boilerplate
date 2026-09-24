#!/usr/bin/env python3
"""Check research inputs and economics. Source authenticity needs source review."""
import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path


class InvalidInput(ValueError):
    pass


CORE_CONDITIONS = {"fulfillment", "order_unit", "returns", "eligibility", "tax_shipping"}


def number(value, label, positive=False, ratio=False, integer=False):
    if isinstance(value, bool) or value is None:
        raise InvalidInput(f"{label}: 숫자가 필요합니다")
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise InvalidInput(f"{label}: 숫자가 필요합니다") from None
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise InvalidInput(f"{label}: 유효한 양수 또는 0이 필요합니다")
    if ratio and result > 1:
        raise InvalidInput(f"{label}: 비율은 0~1입니다")
    if integer and result != result.to_integral_value():
        raise InvalidInput(f"{label}: 정수가 필요합니다")
    return result


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise InvalidInput(f"{label}: 내용이 필요합니다")
    return value


def evidence(ref, records, root):
    record = records.get(ref)
    if not isinstance(record, dict):
        raise InvalidInput(f"{ref}: 근거 기록이 없습니다")
    raw = (root / text(record.get("file"), f"{ref}.file")).resolve()
    if not raw.is_relative_to(root.resolve()) or not raw.is_file():
        raise InvalidInput(f"{ref}: 프로젝트 안의 근거 파일이 필요합니다")
    text(record.get("detail"), f"{ref}.detail")
    if record.get("kind") == "observed":
        url = text(record.get("url"), f"{ref}.url")
        if not url.startswith(("https://", "http://")):
            raise InvalidInput(f"{ref}: 원문 URL이 필요합니다")
    elif record.get("kind") != "approved":
        raise InvalidInput(f"{ref}: observed 또는 approved로 구분합니다")
    return record


def check(data, root):
    records = data["evidence"]
    rules = data["rules"]
    for name in ("customer", "purchase_purpose"):
        text(rules.get(name), name)
    if evidence(rules.get("approval"), records, root)["kind"] != "approved":
        raise InvalidInput("rules.approval: 확정한 사업 조건·기준 근거가 필요합니다")
    money = ("target_profit", "fixed_cost", "min_margin", "product_fee_rate",
             "shipping_fee_rate", "ad_share", "roas", "loss_rate", "settlement_share",
             "working_budget", "ad_budget", "loss_budget", "operating_budget")
    rates = {"min_margin", "product_fee_rate", "shipping_fee_rate", "ad_share", "loss_rate", "settlement_share"}
    r = {k: number(rules.get(k), k, ratio=k in rates) for k in money}
    if r["ad_share"] and not r["roas"]:
        raise InvalidInput("광고 기여가 있으면 ROAS는 0보다 커야 합니다")
    for k in ("order_limit", "min_candidates", "max_screened", "max_routes", "route_fail_limit"):
        r[k] = number(rules.get(k), k, positive=True, integer=True)
    r["max_minutes"] = number(rules.get("max_minutes"), "max_minutes", positive=True)
    elapsed = number(data.get("elapsed_minutes"), "elapsed_minutes")
    conditions = rules.get("required_conditions")
    if not isinstance(conditions, list) or not conditions or len(set(conditions)) != len(conditions):
        raise InvalidInput("required_conditions: 중복 없는 필수 소싱 조건 목록이 필요합니다")
    for condition in conditions:
        text(condition, "required_conditions")
    if not CORE_CONDITIONS.issubset(conditions):
        raise InvalidInput("소싱 조건에는 fulfillment·order_unit·returns·eligibility·tax_shipping이 모두 필요합니다")
    rows, seen, products, routes, failures = [], set(), set(), set(), {}
    required_values = ("price", "customer_shipping", "supply", "supplier_shipping",
                       "other_cost", "other_upfront", "prepay_minimum", "prepay_increment")
    if len(data["items"]) > r["max_screened"]:
        raise InvalidInput("확정한 전체 선별 상품 한도를 초과했습니다")
    for item in data["items"]:
        item_id = text(item.get("id"), "상품 ID")
        if item_id in seen:
            raise InvalidInput(f"{item_id}: 중복 상품 ID")
        seen.add(item_id)
        product = text(item.get("product_key"), f"{item_id}.product_key")
        if product in products:
            raise InvalidInput(f"{item_id}: 같은 상품·옵션을 중복 집계할 수 없습니다")
        products.add(product)
        route = text(item.get("supplier_id"), f"{item_id}.supplier_id")
        routes.add(route)
        if len(routes) > r["max_routes"]:
            raise InvalidInput("확정한 공급사 탐색 한도를 초과했습니다")
        if failures.get(route, 0) >= r["route_fail_limit"]:
            raise InvalidInput(f"{route}: 탈락 한도에 도달한 공급사에서 추가 탐색했습니다")
        row = {"id": item_id, "supplier_id": route, "status": "EXCLUDED", "reasons": []}
        try:
            if item.get("excluded_reason"):
                evidence(item.get("excluded_evidence"), records, root)
                raise InvalidInput(text(item["excluded_reason"], "탈락 사유"))
            for name in ("identity", *conditions):
                fact = item.get("checks", {}).get(name, {})
                if fact.get("pass") is not True:
                    raise InvalidInput(f"{name}: 미확인 또는 조건 미달")
                evidence(fact.get("evidence"), records, root)
            v = {}
            for name in required_values:
                fact = item.get("values", {}).get(name, {})
                v[name] = number(fact.get("value"), name, positive=name == "price")
                ref = evidence(fact.get("evidence"), records, root)
                if name in ("price", "customer_shipping", "supply", "supplier_shipping") and ref["kind"] != "observed":
                    raise InvalidInput(f"{name}: 실제 가격 근거가 필요합니다")
            for name in ("product_fee_evidence", "shipping_fee_evidence"):
                if evidence(item.get(name), records, root)["kind"] != "observed":
                    raise InvalidInput(f"{name}: 적용 수수료 원문이 필요합니다")
            if v["other_upfront"] > v["other_cost"]:
                raise InvalidInput("기타 선지급 비용은 기타 비용 전체보다 클 수 없습니다")
            p, b = v["price"], v["customer_shipping"]
            cost = v["supply"] + v["supplier_shipping"]
            fee = p * r["product_fee_rate"] + b * r["shipping_fee_rate"]
            ad = p * r["ad_share"] / r["roas"] if r["ad_share"] else Decimal(0)
            loss = p * r["loss_rate"]
            goal = r["target_profit"] + r["fixed_cost"]
            profit = p + b - cost - fee - ad - loss - v["other_cost"]
            needed = max(goal / r["order_limit"], p * r["min_margin"])
            allowance = p + b - fee - ad - loss - v["other_cost"] - needed
            row["calculation"] = {"fee": fee, "ad": ad, "loss": loss, "landed_cost": cost,
                                  "allowable_landed_cost": allowance, "profit": profit, "margin": profit / p}
            if profit <= 0 or profit < needed:
                raise InvalidInput("원가 한도 초과 또는 건당 이익 미달")
            orders = max(1, int((goal / profit).to_integral_value(rounding=ROUND_CEILING)))
            working = Decimal(orders) * (cost + v["other_upfront"]) * r["settlement_share"]
            working = max(working, cost + v["other_upfront"], v["prepay_minimum"])
            if v["prepay_increment"]:
                working = (working / v["prepay_increment"]).to_integral_value(rounding=ROUND_CEILING) * v["prepay_increment"]
            ads, losses = ad * orders, loss * orders
            row["calculation"].update(orders=orders, working=working, monthly_ad=ads, monthly_loss=losses)
            limits = ((orders, r["order_limit"], "주문 처리 한도"),
                      (working, r["working_budget"], "운전자금 한도"),
                      (ads, r["ad_budget"], "광고비 한도"),
                      (losses, r["loss_budget"], "손실충당 한도"),
                      (working + ads + losses + r["fixed_cost"], r["operating_budget"], "전체 운영자금 한도"))
            for actual, limit, label in limits:
                if actual > limit:
                    row["reasons"].append(label + " 초과")
            if row["reasons"]:
                raise InvalidInput("수익성 외 월 운영 한도 미달")
            row["status"] = "READY_FOR_DETAIL"
            for name in ("demand", "competition"):
                fact = item.get("checks", {}).get(name, {})
                if fact.get("pass") is False:
                    raise InvalidInput(f"{name}: 확정 기준 미달")
                if fact.get("pass") is not True:
                    row["reasons"].append(f"{name}: 기준 충족 근거 필요")
                else:
                    evidence(fact.get("evidence"), records, root)
            if not row["reasons"]:
                row["status"] = "VALID"
        except InvalidInput as error:
            row["status"] = "EXCLUDED"
            row["reasons"].append(str(error))
        failures[route] = failures.get(route, 0) + (row["status"] == "EXCLUDED")
        rows.append(row)
    valid = [row["id"] for row in rows if row["status"] == "VALID"]
    ready = [row["id"] for row in rows if row["status"] == "READY_FOR_DETAIL"]
    closed = sorted(route for route, count in failures.items() if count >= r["route_fail_limit"])
    exhausted = elapsed >= r["max_minutes"] or len(seen) >= r["max_screened"]
    routes_exhausted = len(routes) >= r["max_routes"] and all(route in closed for route in routes)
    if len(valid) >= r["min_candidates"]:
        action = "COMPLETE"
    elif exhausted or (routes_exhausted and not ready):
        action = "STOP_INCOMPLETE"
    elif ready:
        action = "RESEARCH_READY_ITEMS"
    elif rows and rows[-1]["supplier_id"] in closed:
        action = "CHANGE_SUPPLIER"
    else:
        action = "CONTINUE_SCREENING"
    return {"action": action, "valid_ids": valid, "ready_ids": ready,
            "closed_suppliers": closed, "screened": len(seen), "routes": len(routes), "items": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        if not args.input.resolve().is_relative_to(root):
            raise InvalidInput("입력은 프로젝트 안에 저장해야 합니다")
        raw = args.input.read_bytes()
        data = json.loads(raw)
        history_path = root / "artifacts/sources/research-history.json"
        history = json.loads(history_path.read_text()) if history_path.exists() else {}
        current = {item["id"]: [item["product_key"], item["supplier_id"]] for item in data["items"]}
        for item_id, identity in history.get("items", {}).items():
            if current.get(item_id) != identity:
                raise InvalidInput("누적 상품을 삭제·교체해 탐색 한도를 초기화할 수 없습니다")
        if number(data.get("elapsed_minutes"), "elapsed_minutes") < number(history.get("elapsed_minutes", 0), "history.elapsed_minutes"):
            raise InvalidInput("누적 조사 시간을 줄일 수 없습니다")
        result = check(data, root)
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        history_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = history_path.with_suffix(".tmp")
        temporary.write_text(json.dumps({"items": current, "elapsed_minutes": data["elapsed_minutes"]}, ensure_ascii=False, indent=2))
        temporary.replace(history_path)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0 if result["action"] == "COMPLETE" else 2
    except (InvalidInput, KeyError, TypeError, AttributeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"action": "INVALID_INPUT", "reason": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
