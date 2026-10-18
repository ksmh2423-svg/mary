"""명령줄 실행(화면 없이). 예:
  python -m wituk.cli --excel sample/샘플_도매상품.xlsx --markets smartstore coupang
  python -m wituk.cli --domeggook 텀블러 --max 30 --markets smartstore
"""
import argparse
import sys

from .pipeline import CONFIG_DIR, ROOT, load_settings, run
from .sources import excel_import


def main(argv=None):
    ap = argparse.ArgumentParser(description="위탁판매 자동화")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--excel", help="도매처 엑셀/CSV 파일")
    src.add_argument("--domeggook", metavar="키워드", help="도매꾹 API로 키워드 수집")
    ap.add_argument("--category", default="", help="도매꾹 카테고리 코드")
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--markets", nargs="+", default=["smartstore", "coupang"])
    ap.add_argument("--template", action="append", default=[], metavar="마켓=파일",
                    help="마켓 양식 파일, 예: smartstore=양식.xlsx")
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "output"))
    a = ap.parse_args(argv)

    cfg = load_settings()
    unknown = [m for m in a.markets if m not in cfg["markets"]]
    if unknown:
        print(f"없는 마켓: {unknown}. 사용 가능: {list(cfg['markets'])}")
        return 2
    if a.excel:
        products = excel_import.load_products(a.excel, cfg.get("excel_import_columns"))
    else:
        from .sources.domeggook import DomeggookClient
        client = DomeggookClient(a.api_key, dump_dir=ROOT / "output" / "_api_raw")
        products = client.collect(a.domeggook, a.category, a.max, progress=print)
    print(f"불러온 상품: {len(products)}개")
    templates = dict(t.split("=", 1) for t in a.template)
    out, files = run(products, cfg, a.markets, a.out, templates, not a.no_images, CONFIG_DIR)
    print(f"\n완료! 폴더: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
