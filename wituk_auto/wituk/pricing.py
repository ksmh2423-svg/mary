"""판매가 계산: 원가(환율·관부가세 반영) + 배송비 → 마진·마켓수수료를 남기는 가격."""
import math


def landed_cost(p, cfg):
    """상품 1개를 내 손에 넣기까지 드는 돈(원)."""
    rate = cfg.get("exchange_rates", {}).get(p.currency, 1.0)
    goods = p.cost * rate
    if p.currency != "KRW":
        # 해외 직구형: 관세·부가세 (면세 기준 이하면 0)
        if goods > cfg.get("duty_free_limit_krw", 150000):
            duty = goods * cfg.get("duty_rate", 0.08)
            goods = goods + duty + (goods + duty) * cfg.get("vat_rate", 0.10)
        goods += cfg.get("intl_shipping_krw", 0)
    return goods + p.source_shipping


def sale_price(p, cfg, market=None):
    """마켓 수수료를 떼고도 마진율이 남는 가격. 끝자리 반올림."""
    m = cfg.get("markets", {}).get(market, {}) if market else {}
    fee = m.get("fee_rate", cfg.get("default_fee_rate", 0.11))
    margin = cfg.get("margin_rate", 0.25)
    add_ship = cfg.get("my_shipping_fee", 0) if cfg.get("free_shipping", True) else 0
    base = landed_cost(p, cfg) + add_ship + cfg.get("extra_cost_per_item", 0)
    denom = 1 - fee - margin
    if denom <= 0:
        raise ValueError("수수료율+마진율이 100%를 넘습니다. 설정을 확인하세요.")
    price = base / denom
    unit = cfg.get("round_unit", 100)
    price = math.ceil(price / unit) * unit
    return max(int(price), cfg.get("min_price", 0))


def profit(price, p, cfg, market=None):
    m = cfg.get("markets", {}).get(market, {}) if market else {}
    fee = m.get("fee_rate", cfg.get("default_fee_rate", 0.11))
    add_ship = cfg.get("my_shipping_fee", 0) if cfg.get("free_shipping", True) else 0
    return int(price * (1 - fee) - landed_cost(p, cfg) - add_ship - cfg.get("extra_cost_per_item", 0))
