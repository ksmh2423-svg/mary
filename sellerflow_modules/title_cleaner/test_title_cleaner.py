"""실행: python -m unittest test_title_cleaner  (또는 pytest)"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from title_cleaner import TitleRules, clean, keywords  # noqa: E402


def rules(**kw):
    base = dict(remove_regex=[r"\[[^\]]*\]", r"[★☆]+"], remove_word=["무료배송", "특가", "초특가"],
                replace=[("스텐 ", "스테인리스 ")], stopword=["세트"], max_len=50)
    base.update(kw)
    return TitleRules.from_dicts(**base)


class TestTitleCleaner(unittest.TestCase):
    def test_removes_tags_and_symbols(self):
        r = clean("[무료배송] ★스텐 텀블러★", rules())
        self.assertEqual(r.title, "스테인리스 텀블러")
        self.assertIn("[무료배송]", r.removed)
        self.assertFalse(r.truncated)
        self.assertEqual(r.original, "[무료배송] ★스텐 텀블러★")

    def test_longer_word_removed_first(self):
        self.assertEqual(clean("초특가 캠핑의자", rules()).title, "캠핑의자")

    def test_dedupe_case_insensitive(self):
        self.assertEqual(clean("텀블러 LED 텀블러 led", rules()).title, "텀블러 LED")
        self.assertEqual(clean("텀블러 텀블러", rules(dedupe="false")).title, "텀블러 텀블러")

    def test_truncate_on_word_boundary(self):
        r = clean("가나다 라마바 사아자", rules(max_len=9))
        self.assertEqual(r.title, "가나다 라마바")
        self.assertTrue(r.truncated)
        self.assertLessEqual(len(r.title), 9)

    def test_truncate_exact_boundary_keeps_word(self):
        self.assertEqual(clean("가나다 라마바 사아자", rules(max_len=7)).title, "가나다 라마바")

    def test_truncate_single_long_word(self):
        self.assertEqual(clean("가나다라마바사", rules(max_len=3)).title, "가나다")

    def test_market_specific_limit(self):
        r = rules(max_len=5, max_len_coupang="100")
        self.assertEqual(clean("가나다 라마바", r, market="coupang").title, "가나다 라마바")
        self.assertEqual(clean("가나다 라마바", r, market="11st").title, "가나다")
        self.assertEqual(clean("가나다 라마바", r).title, "가나다")

    def test_blank_market_limit_ignored(self):
        self.assertEqual(rules(max_len_gmarket="").max_len_by_market, {})

    def test_prefix_counts_toward_limit(self):
        r = clean("텀블러", rules(prefix="해피몰"))
        self.assertEqual(r.title, "해피몰 텀블러")

    def test_translate_only_without_hangul(self):
        calls = []

        def fake(t):
            calls.append(t)
            return "번역됨 " + t

        self.assertEqual(clean("Steel tumbler", rules(), translate=fake).title, "번역됨 Steel tumbler")
        clean("스텐 텀블러", rules(), translate=fake)
        self.assertEqual(calls, ["Steel tumbler"])

    def test_translate_failure_keeps_original(self):
        def boom(t):
            raise RuntimeError("API down")
        self.assertEqual(clean("Steel tumbler", rules(), translate=boom).title, "Steel tumbler")

    def test_keywords(self):
        r = rules()
        self.assertEqual(keywords("텀블러 세트 500 500ml 텀블러", r), ["텀블러", "500ml"])
        self.assertEqual(keywords("텀블러", r, extra="주방>컵"), ["텀블러", "주방"])

    def test_empty_title(self):
        r = clean(None, rules())
        self.assertEqual((r.title, r.keywords), ("", []))

    def test_csv_loading(self):
        with tempfile.TemporaryDirectory() as d:
            rp, sp = Path(d) / "r.csv", Path(d) / "s.csv"
            rp.write_text("kind,pattern,replacement,note\n# 메모,,,\nremove_word,특가,,\n"
                          "replace,스텐레스,스테인리스,\n", encoding="utf-8")
            sp.write_text("key,value,note\nmax_len,20,\nmax_len_coupang,,\nprefix,,\n", encoding="utf-8")
            r = TitleRules.from_csv(rp, sp)
        self.assertEqual(r.max_len, 20)
        self.assertEqual(clean("스텐레스 특가 컵", r).title, "스테인리스 컵")

    def test_unknown_kind_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            rp = Path(d) / "r.csv"
            rp.write_text("kind,pattern,replacement,note\nremove,특가,,\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                TitleRules.from_csv(rp)

    def test_bundled_files_load(self):
        r = TitleRules.from_csv(HERE / "rules.csv", HERE / "settings.csv")
        out = clean("[무료배송] ★스텐 진공 텀블러 500ml★ (당일발송 특가)", r)
        self.assertEqual(out.title, "스테인리스 진공 텀블러 500ml")


if __name__ == "__main__":
    unittest.main()
