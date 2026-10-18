"""도매꾹 오픈API 수집기.

- 도매꾹에서 발급받은 API 키(aid)가 필요합니다. 키는 settings.json 이 아니라
  환경변수 DOMEGGOOK_API_KEY 또는 프로그램 화면의 입력칸으로 넣습니다.
- 공식 API만 사용합니다(로그인 우회·화면 긁기 없음). 요청 사이에 쉬는 시간을 둡니다.
- 응답 구조는 버전에 따라 조금씩 다를 수 있어, 필드를 여러 이름으로 찾아봅니다.
  실제 키로 처음 돌릴 때 '원본 응답 저장'을 켜 두면 구조를 확인할 수 있습니다.
"""
import json
import os
import time
from pathlib import Path

import requests

from ..models import Option, Product

API_URL = "https://domeggook.com/ssl/api/"


def _first(d, *keys, default=None):
    for k in keys:
        cur = d
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur not in (None, ""):
            return cur
    return default


def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _to_int(v):
    try:
        return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return 0


class DomeggookClient:
    def __init__(self, api_key=None, version="4.1", delay=1.0, dump_dir=None, session=None):
        self.api_key = api_key or os.environ.get("DOMEGGOOK_API_KEY", "")
        if not self.api_key:
            raise ValueError("도매꾹 API 키가 없습니다. 화면에 입력하거나 DOMEGGOOK_API_KEY 환경변수를 설정하세요.")
        self.version = version
        self.delay = delay
        self.dump_dir = Path(dump_dir) if dump_dir else None
        self.http = session or requests.Session()
        self._last = 0.0

    def _call(self, mode, **params):
        wait = self.delay - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        q = {"ver": self.version, "mode": mode, "aid": self.api_key, "om": "json", **params}
        r = self.http.get(API_URL, params=q, timeout=20)
        self._last = time.time()
        r.raise_for_status()
        data = r.json()
        if self.dump_dir:
            self.dump_dir.mkdir(parents=True, exist_ok=True)
            name = f"{mode}_{params.get('no') or params.get('kw') or params.get('ca') or ''}_{int(time.time())}.json"
            (self.dump_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        err = _first(data, "errors", "domeggook.errors", "error")
        if err:
            raise RuntimeError(f"도매꾹 API 오류: {err}")
        return data

    def search(self, keyword="", category="", max_items=50, page_size=50):
        """키워드 또는 카테고리로 상품 목록(요약)을 가져온다."""
        items, page = [], 1
        while len(items) < max_items:
            params = {"market": "dome", "sz": min(page_size, max_items), "pg": page}
            if keyword:
                params["kw"] = keyword
            if category:
                params["ca"] = category
            data = self._call("getItemList", **params)
            batch = _as_list(_first(data, "domeggook.list.item", "list.item", "items"))
            if not batch:
                break
            items.extend(batch)
            page += 1
        return items[:max_items]

    def detail(self, item_no):
        return self._call("getItemView", no=item_no)

    def collect(self, keyword="", category="", max_items=50, with_detail=True, progress=None):
        summaries = self.search(keyword, category, max_items)
        products = []
        for i, s in enumerate(summaries, 1):
            no = str(_first(s, "no", "itemNo", "id", default=""))
            d = {}
            if with_detail and no:
                try:
                    d = _first(self.detail(no), "domeggook", default={}) or {}
                except Exception as e:  # 상세 실패해도 요약 정보로 진행
                    if progress:
                        progress(f"  상세 실패 {no}: {e}")
            products.append(to_product(s, d))
            if progress:
                progress(f"[{i}/{len(summaries)}] {products[-1].title[:30]}")
        return products


def to_product(summary, detail=None):
    detail = detail or {}
    merged = {**summary, **detail}
    no = str(_first(merged, "basis.no", "no", "itemNo", default=""))
    title = str(_first(merged, "basis.title", "title", "name", default=""))
    price = _to_int(_first(merged, "price.dome", "price", "unitPrice", default=0))
    stock = _to_int(_first(merged, "qty.inventory", "inventory", "stock", default=0))
    images = []
    for k in ("thumb.original", "thumb.large", "thumb", "image", "img"):
        v = _first(merged, k)
        if isinstance(v, str) and v.startswith("http"):
            images.append(v)
            break
    detail_html = str(_first(merged, "desc.contents.item", "desc.contents", "detail", default=""))
    options = []
    for o in _as_list(_first(merged, "selectOpt.data", "options.item", "options")):
        if isinstance(o, dict):
            options.append(Option(
                name=str(_first(o, "name", "title", default="")),
                extra_price=_to_int(_first(o, "price", "addPrice", default=0)),
                stock=_to_int(_first(o, "qty", "stock", default=0)),
            ))
    ship = _to_int(_first(merged, "deli.dome.fee", "deli.fee", "deliveryFee", default=0))
    return Product(
        source="domeggook", source_id=no, title=title, cost=price, stock=stock,
        category=str(_first(merged, "category.current.name", "category", default="")),
        brand=str(_first(merged, "detail.brand", "brand", default="")),
        images=images, detail_html=detail_html, options=options, source_shipping=ship,
        url=f"https://domeggook.com/{no}" if no else "",
    )
