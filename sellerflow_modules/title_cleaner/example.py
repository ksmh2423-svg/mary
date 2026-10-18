"""사용 예시: python example.py"""
from pathlib import Path

from title_cleaner import TitleRules, clean

here = Path(__file__).parent
rules = TitleRules.from_csv(here / "rules.csv", here / "settings.csv")

for t in [
    "[무료배송] ★스텐 진공 텀블러 500ml 보온보냉 텀블러★",
    "【당일발송】 접이식 캠핑 의자 초경량 캠핑의자 특가",
    "실리콘 주방 집게 3종 세트 도매 (이벤트 특가)",
]:
    r = clean(t, rules, market="coupang")
    print(f"{r.title}\n  지운 것: {r.removed}\n  키워드: {r.keywords}\n")
