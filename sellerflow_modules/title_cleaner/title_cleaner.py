"""상품명 정리 (표준 라이브러리만 사용).

도매처 상품명에 붙은 홍보 꼬리표·특수문자를 지우고, 중복 단어를 정리하고,
글자 수 제한에 맞춰 단어 단위로 자르고, 검색 키워드를 뽑습니다.

정책 내용(지울 단어·패턴, 바꿀 단어, 키워드 제외어, 길이 제한)은
rules.csv / settings.csv 에 있습니다. config.yaml 에서 관리한다면
TitleRules.from_dicts(...) 를 쓰면 됩니다.
"""
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

RULE_KINDS = ("remove_regex", "remove_word", "replace", "stopword")


@dataclass
class TitleRules:
    remove_regex: list = field(default_factory=list)   # 정규식 → 지움
    remove_word: list = field(default_factory=list)    # 단어 → 지움 (포함되면 그 부분만)
    replace: list = field(default_factory=list)        # [(바꿀 것, 바뀔 것)]
    stopword: list = field(default_factory=list)       # 키워드에서 뺄 단어
    max_len: int = 50                                  # 기본 글자 수 제한
    max_len_by_market: dict = field(default_factory=dict)  # {"coupang": 100, ...} 확인된 값만 넣기
    prefix: str = ""                                   # 상품명 앞에 붙일 말 (예: 스토어 이름)
    dedupe: bool = True                                # 같은 단어 반복 제거
    keyword_count: int = 10

    def __post_init__(self):
        self._compiled = [re.compile(p) for p in self.remove_regex]

    @classmethod
    def from_csv(cls, rules_path, settings_path=None, encoding="utf-8-sig"):
        """rules.csv (열: kind, pattern, replacement, note) + settings.csv (열: key, value, note)."""
        d = {k: [] for k in RULE_KINDS}
        with open(Path(rules_path), newline="", encoding=encoding) as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip()
                if not kind or kind.startswith("#"):
                    continue
                if kind not in RULE_KINDS:
                    raise ValueError(f"알 수 없는 kind: {kind} (가능: {RULE_KINDS})")
                pat = row.get("pattern") or ""
                if kind != "replace":
                    pat = pat.strip()
                if not pat:
                    continue
                if kind == "replace":
                    d[kind].append((pat, row.get("replacement") or ""))
                else:
                    d[kind].append(pat)
        settings = _read_settings(settings_path, encoding) if settings_path else {}
        return cls.from_dicts(**d, **settings)

    @classmethod
    def from_dicts(cls, remove_regex=(), remove_word=(), replace=(), stopword=(), **settings):
        by_market = {k[len("max_len_"):]: int(v) for k, v in settings.items()
                     if k.startswith("max_len_") and str(v).strip()}
        return cls(
            remove_regex=list(remove_regex), remove_word=list(remove_word),
            replace=[tuple(x) for x in replace], stopword=list(stopword),
            max_len=int(settings.get("max_len", 50)), max_len_by_market=by_market,
            prefix=str(settings.get("prefix", "") or ""),
            dedupe=str(settings.get("dedupe", "true")).lower() in ("1", "true", "yes", "y"),
            keyword_count=int(settings.get("keyword_count", 10)),
        )


def _read_settings(path, encoding):
    out = {}
    with open(Path(path), newline="", encoding=encoding) as f:
        for row in csv.DictReader(f):
            key = (row.get("key") or "").strip()
            if key and not key.startswith("#"):
                out[key] = (row.get("value") or "").strip()
    return out


@dataclass
class TitleResult:
    title: str                 # 정리된 상품명
    original: str
    removed: list = field(default_factory=list)   # 지워진 조각 (확인용)
    truncated: bool = False    # 글자 수 제한 때문에 잘렸는지
    keywords: list = field(default_factory=list)


def clean(title, rules, market=None, translate=None):
    """상품명을 정리한다.

    title     : 원본 상품명
    rules     : TitleRules
    market    : "coupang" 등. rules.max_len_by_market 에 있으면 그 길이를 쓴다.
    translate : 선택. 한글이 하나도 없는 상품명(해외 소싱)에만 호출하는 함수 str→str.
                실패하면 원문을 그대로 쓴다.
    반환      : TitleResult
    """
    original = title or ""
    t = original
    if translate and t and not re.search(r"[가-힣]", t):
        try:
            t = translate(t) or t
        except Exception:
            pass

    removed = []
    for src, dst in rules.replace:
        t = t.replace(src, dst)
    for rx in rules._compiled:
        removed += [m.group(0) for m in rx.finditer(t)]
        t = rx.sub(" ", t)
    for w in sorted(rules.remove_word, key=len, reverse=True):
        if w in t:
            removed.append(w)
            t = t.replace(w, " ")

    words = t.split()
    if rules.dedupe:
        seen, uniq = set(), []
        for w in words:
            k = w.lower()
            if k in seen:
                removed.append(w)
                continue
            seen.add(k)
            uniq.append(w)
        words = uniq
    t = " ".join(words)

    if rules.prefix and not t.startswith(rules.prefix):
        t = f"{rules.prefix} {t}".strip()

    limit = rules.max_len_by_market.get(market, rules.max_len) if market else rules.max_len
    truncated = False
    if limit and len(t) > limit:
        truncated = True
        cut = t[:limit]
        # 단어 중간에서 잘리면 그 단어는 뺀다 (단어가 하나뿐이면 그냥 자른다)
        if t[limit:limit + 1] not in ("", " ") and " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        t = cut.strip()

    return TitleResult(title=t, original=original, removed=removed, truncated=truncated,
                       keywords=keywords(t, rules))


def keywords(text, rules, extra=""):
    """정리된 상품명(+ extra, 예: 카테고리 이름)에서 검색 키워드를 뽑는다. 두 글자 이상, 숫자만인 것 제외."""
    stop = {s.lower() for s in rules.stopword}
    out = []
    for tok in re.findall(r"[가-힣A-Za-z0-9]{2,}", f"{text} {extra}"):
        if tok.isdigit() or tok.lower() in stop or tok in out:
            continue
        out.append(tok)
    return out[: rules.keyword_count]
