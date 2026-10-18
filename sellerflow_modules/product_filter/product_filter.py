"""금지어 · 상표권 의심어 · 인증 필요 품목 걸러내기 (표준 라이브러리만 사용).

정책 내용(단어 목록)은 코드에 없고 rules.csv 에 있습니다.
SellerFlow 의 config.yaml 처럼 다른 곳에서 목록을 관리한다면
FilterRules.from_dicts(...) 로 같은 규칙을 만들 수 있습니다.

판정 결과
  "block"  : 금지어가 있음 → 등록 제외 권장
  "review" : 상표 의심어 또는 인증 확인 품목 → 사람이 확인 후 등록
  "pass"   : 걸린 단어 없음

예외 문구(allow)는 '위험 단어를 포함한 전체 문구'로 적습니다.
  예) allow "무알콜 맥주" → '무알콜 맥주' 안의 '맥주'는 무시, '수제 맥주'는 그대로 걸림

이 모듈은 '보조 장치'입니다. pass 가 '판매해도 법적으로 안전하다'는 뜻은 아닙니다.
"""
import csv
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("block", "trademark", "cert", "allow")


@dataclass(frozen=True)
class Rule:
    kind: str        # block | trademark | cert | allow
    word: str
    note: str = ""


@dataclass(frozen=True)
class Hit:
    kind: str        # block | trademark | cert
    word: str
    field: str       # 어느 입력 칸에서 찾았는지 (title, brand 등)
    note: str = ""


@dataclass
class FilterResult:
    decision: str                       # block | review | pass
    hits: list = field(default_factory=list)

    @property
    def blocked(self):
        return self.decision == "block"

    def summary(self):
        """사람이 읽는 한 줄 요약. 예: '금지어:전자담배, 상표의심:나이키'"""
        label = {"block": "금지어", "trademark": "상표의심", "cert": "인증확인"}
        return ", ".join(f"{label[h.kind]}:{h.word}" for h in self.hits)


def normalize(text):
    """대소문자·띄어쓰기 차이를 없앤다. '전자 담배' 와 '전자담배' 를 같게 본다."""
    return "".join(str(text or "").lower().split())


class FilterRules:
    def __init__(self, rules):
        bad = [r for r in rules if r.kind not in KINDS]
        if bad:
            raise ValueError(f"알 수 없는 kind: {[r.kind for r in bad]} (가능: {KINDS})")
        self.rules = [r for r in rules if r.word.strip()]
        # 긴 예외 문구부터 지워야 짧은 문구에 먼저 먹히지 않는다
        self.allow = sorted({normalize(r.word) for r in self.rules if r.kind == "allow"}, key=len, reverse=True)
        # 금지어 → 상표 → 인증 순, 같은 종류 안에서는 긴 단어부터 검사한다.
        # 찾은 부분은 지워서 '전자담배' 안의 '담배', '충전기' 안의 '전기' 가 또 걸리지 않게 한다.
        order = {"block": 0, "trademark": 1, "cert": 2}
        self.check_rules = sorted((r for r in self.rules if r.kind != "allow"),
                                  key=lambda r: (order[r.kind], -len(normalize(r.word))))

    @classmethod
    def from_csv(cls, path, encoding="utf-8-sig"):
        """rules.csv (열: kind, word, note). '#' 으로 시작하는 kind 는 메모로 건너뜀."""
        rules = []
        with open(Path(path), newline="", encoding=encoding) as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip()
                if not kind or kind.startswith("#"):
                    continue
                rules.append(Rule(kind, (row.get("word") or "").strip(), (row.get("note") or "").strip()))
        return cls(rules)

    @classmethod
    def from_dicts(cls, block=(), trademark=(), cert=(), allow=()):
        """config.yaml 등에서 읽은 단어 목록으로 만들기."""
        rules = [Rule("block", w) for w in block] + [Rule("trademark", w) for w in trademark]
        rules += [Rule("cert", w) for w in cert] + [Rule("allow", w) for w in allow]
        return cls(rules)


def check(fields, rules):
    """상품 정보를 검사한다.

    fields : {"title": "...", "brand": "...", "category": "..."} 처럼 칸 이름 → 글자.
             글자 하나만 넘기면 {"text": 그 글자} 로 본다.
    rules  : FilterRules
    반환   : FilterResult (같은 단어는 한 번만 기록, 금지어가 하나라도 있으면 block)
    """
    if isinstance(fields, str):
        fields = {"text": fields}
    hits, seen = [], set()
    for name, value in fields.items():
        text = normalize(value)
        for phrase in rules.allow:
            text = text.replace(phrase, " ")
        for r in rules.check_rules:
            key = (r.kind, r.word)
            w = normalize(r.word)
            if w in text:
                text = text.replace(w, " ")
                if key not in seen:
                    hits.append(Hit(r.kind, r.word, name, r.note))
                    seen.add(key)
    order = {"block": 0, "trademark": 1, "cert": 2}
    hits.sort(key=lambda h: order[h.kind])
    if any(h.kind == "block" for h in hits):
        decision = "block"
    elif hits:
        decision = "review"
    else:
        decision = "pass"
    return FilterResult(decision, hits)
