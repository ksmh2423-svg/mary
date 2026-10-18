"""실행: python -m unittest test_product_filter  (또는 pytest)"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from product_filter import FilterRules, Rule, check, normalize  # noqa: E402


class TestProductFilter(unittest.TestCase):
    def setUp(self):
        self.rules = FilterRules.from_dicts(
            block=["전자담배", "맥주"], trademark=["나이키"], cert=["충전기", "USB"], allow=["무알콜 맥주"])

    def test_pass(self):
        r = check({"title": "스텐 텀블러 500ml"}, self.rules)
        self.assertEqual(r.decision, "pass")
        self.assertEqual(r.hits, [])

    def test_block_wins_over_review(self):
        r = check({"title": "나이키 전자담배 케이스"}, self.rules)
        self.assertEqual(r.decision, "block")
        self.assertTrue(r.blocked)
        self.assertEqual([h.kind for h in r.hits], ["block", "trademark"])

    def test_review_for_trademark_and_cert(self):
        self.assertEqual(check("나이키 운동화", self.rules).decision, "review")
        self.assertEqual(check("고속 충전기", self.rules).decision, "review")

    def test_spacing_and_case_ignored(self):
        self.assertEqual(check("전자 담배 파우치", self.rules).decision, "block")
        self.assertEqual(check("usb 케이블", self.rules).decision, "review")

    def test_allow_phrase(self):
        self.assertEqual(check("무알콜 맥주", self.rules).decision, "pass")
        self.assertEqual(check("수제 맥주", self.rules).decision, "block")

    def test_field_reported_and_no_duplicates(self):
        r = check({"title": "충전기", "category": "디지털>충전기"}, self.rules)
        self.assertEqual(len(r.hits), 1)
        self.assertEqual(r.hits[0].field, "title")

    def test_brand_field_checked(self):
        r = check({"title": "운동화", "brand": "NIKE 나이키"}, self.rules)
        self.assertEqual(r.hits[0].field, "brand")

    def test_longer_word_hides_inner_word(self):
        rules = FilterRules.from_dicts(block=["담배", "전자담배"], cert=["전기", "충전기"])
        self.assertEqual(check("전자담배 충전기", rules).summary(), "금지어:전자담배, 인증확인:충전기")
        self.assertEqual(check("전기 히터", rules).summary(), "인증확인:전기")

    def test_summary(self):
        self.assertEqual(check("나이키 충전기", self.rules).summary(), "상표의심:나이키, 인증확인:충전기")

    def test_empty_and_none(self):
        self.assertEqual(check({"title": None, "brand": ""}, self.rules).decision, "pass")
        self.assertEqual(normalize(None), "")

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            FilterRules([Rule("banned", "x")])

    def test_csv_loading_skips_comments(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.csv"
            p.write_text("kind,word,note\n# 메모,,\nblock,짝퉁,\ncert,LED,\n,,\n", encoding="utf-8")
            rules = FilterRules.from_csv(p)
        self.assertEqual(len(rules.check_rules), 2)
        self.assertEqual(check("짝퉁 LED", rules).decision, "block")

    def test_bundled_rules_csv_loads(self):
        rules = FilterRules.from_csv(HERE / "rules.csv")
        self.assertEqual(check("무알콜 맥주", rules).decision, "pass")
        self.assertEqual(check("와인잔 2개", rules).decision, "pass")
        self.assertEqual(check("레드 와인", rules).decision, "block")


if __name__ == "__main__":
    unittest.main()
