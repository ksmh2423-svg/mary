"""전체 흐름: 불러오기 → 상품명 정리 → 필터 → 가격 → 이미지 → 마켓별 엑셀 + 결과표."""
import json
import sys
from datetime import datetime
from pathlib import Path

from . import exporters, images, pricing, titles
from .filters import ProductFilter

if getattr(sys, "frozen", False):  # exe로 묶었을 때: exe 옆 폴더 기준
    ROOT = Path(sys.executable).resolve().parent
    _BUNDLE = Path(getattr(sys, "_MEIPASS", ROOT))
    CONFIG_DIR = ROOT / "config" if (ROOT / "config").exists() else _BUNDLE / "config"
else:
    ROOT = Path(__file__).resolve().parent.parent
    CONFIG_DIR = ROOT / "config"


def load_settings(config_dir=CONFIG_DIR):
    cfg = json.loads((Path(config_dir) / "settings.json").read_text(encoding="utf-8"))
    cfg["markets"] = {}
    for f in sorted((Path(config_dir) / "markets").glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        cfg["markets"][f.stem] = m
    return cfg


def process(products, cfg, config_dir=CONFIG_DIR, translate=None, log=print):
    flt = ProductFilter(config_dir)
    for p in products:
        p.clean_title = titles.clean_title(p.title, cfg, translate)
        p.keywords = titles.keywords(p.clean_title, p.category)
        p.flags, p.blocked = flt.check(p)
        if p.cost <= 0:
            p.flags.append("가격없음")
            p.blocked = True
        if cfg.get("skip_out_of_stock", True) and p.stock == 0 and not p.options:
            pass  # 재고 0 은 도매처가 재고를 안 알려주는 경우가 많아 경고만
    log(f"가공 완료: {len(products)}개 (제외 {sum(p.blocked for p in products)}개)")
    return products


def run(products, cfg, markets, out_dir, templates=None, do_images=True,
        config_dir=CONFIG_DIR, translate=None, log=print):
    templates = templates or {}
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = Path(out_dir) / stamp
    process(products, cfg, config_dir, translate, log)
    ok = [p for p in products if not p.blocked]
    if not cfg.get("include_warned", True):
        ok = [p for p in ok if not p.flags]

    if do_images:
        log("이미지 내려받기·정리 중…")
        for i, p in enumerate(ok, 1):
            p.local_images = images.process_product_images(p, out / "images", cfg, log=log)
            if i % 10 == 0:
                log(f"  이미지 {i}/{len(ok)}")

    files = []
    for mk in markets:
        mcfg = cfg["markets"][mk]
        for p in ok:
            p.sale_price = pricing.sale_price(p, cfg, mk)
        path = out / f"{mcfg.get('label', mk)}_대량등록_{stamp}.xlsx"
        missing = exporters.export_market(ok, mcfg, cfg, path, templates.get(mk))
        if missing:
            log(f"  [{mcfg.get('label', mk)}] 양식에서 못 찾은 열: {', '.join(missing)}")
        files.append(path)
        log(f"엑셀 저장: {path.name} ({len(ok)}개)")

    if markets:  # 결과표는 첫 마켓 가격 기준
        for p in ok:
            p.sale_price = pricing.sale_price(p, cfg, markets[0])
    report = out / f"결과표_{stamp}.xlsx"
    exporters.export_report(products, cfg, markets, report)
    files.append(report)
    log(f"결과표 저장: {report.name}")
    return out, files
