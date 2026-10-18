"""상품명 다듬기: 도매처 꼬리표 제거, 중복 단어 정리, 길이 제한, 검색 키워드 뽑기.
해외 소싱 상품명은 번역 함수를 연결할 수 있습니다(translate 인자)."""
import re

NOISE_PATTERNS = [
    r"\[[^\]]*\]", r"【[^】]*】", r"\([^)]*(무료배송|당일발송|특가|이벤트|도매|최저가)[^)]*\)",
    r"(무료배송|당일발송|당일출고|초특가|특가|최저가|도매|땡처리|1\+1행사|사은품증정)",
    r"[★☆♥♡◆◇■□●○▶▷※#~!@^*]+",
]


def clean_title(title, cfg, translate=None):
    t = title or ""
    if translate and re.search(r"[一-鿿]|[A-Za-z]{4,}", t) and not re.search(r"[가-힣]", t):
        try:
            t = translate(t)
        except Exception:
            pass
    for pat in NOISE_PATTERNS + cfg.get("title_remove_patterns", []):
        t = re.sub(pat, " ", t)
    for w in cfg.get("title_remove_words", []):
        t = t.replace(w, " ")
    words, seen = [], set()
    for w in t.split():
        key = w.lower()
        if key in seen:
            continue
        seen.add(key)
        words.append(w)
    t = " ".join(words)
    prefix = cfg.get("title_prefix", "").strip()
    if prefix and not t.startswith(prefix):
        t = f"{prefix} {t}"
    limit = cfg.get("title_max_len", 50)
    if len(t) > limit:
        cut = t[:limit]
        t = cut.rsplit(" ", 1)[0] if " " in cut else cut
    return t.strip()


STOP = {"및", "용", "개", "세트", "상품", "제품", "추천", "인기", "신상"}


def keywords(title, category="", n=10):
    toks = re.findall(r"[가-힣A-Za-z0-9]{2,}", f"{title} {category}")
    out = []
    for t in toks:
        if t in STOP or t.isdigit() or t in out:
            continue
        out.append(t)
    return out[:n]
