"""사용 예시: python example.py"""
from pathlib import Path

from product_filter import FilterRules, check

rules = FilterRules.from_csv(Path(__file__).with_name("rules.csv"))

for title, brand in [
    ("스텐 진공 텀블러 500ml", ""),
    ("고속 충전기 USB-C 25W", ""),
    ("나이키 스타일 운동화", ""),
    ("전자담배 가죽 케이스", ""),
    ("무알콜 맥주 6캔", ""),
]:
    r = check({"title": title, "brand": brand}, rules)
    print(f"{r.decision:7s} | {title} | {r.summary()}")

# config.yaml 에서 읽은 목록으로 만들 때
rules2 = FilterRules.from_dicts(block=["짝퉁"], trademark=["샤넬"], cert=["LED"])
print(check("샤넬 st LED 거울", rules2).summary())
