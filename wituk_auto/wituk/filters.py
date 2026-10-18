"""금지어 / 상표권 의심어 / 인증 필요 품목 걸러내기.
목록은 config 폴더의 txt 파일(한 줄에 하나, #은 메모)로 직접 고칠 수 있습니다.
프로그램은 보조 장치일 뿐, 최종 판매 책임은 판매자에게 있습니다."""
from pathlib import Path


def load_list(path):
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


class ProductFilter:
    def __init__(self, config_dir):
        d = Path(config_dir)
        self.banned = load_list(d / "forbidden_words.txt")
        self.trademarks = load_list(d / "trademark_words.txt")
        self.cert = load_list(d / "cert_keywords.txt")

    def check(self, p):
        """(경고목록, 차단여부)를 돌려준다. 금지어는 차단, 상표·인증은 경고."""
        text = f"{p.title} {p.clean_title} {p.brand} {p.category}".lower()
        flags, blocked = [], False
        for w in self.banned:
            if w.lower() in text:
                flags.append(f"금지어:{w}")
                blocked = True
        for w in self.trademarks:
            if w.lower() in text:
                flags.append(f"상표의심:{w}")
        for w in self.cert:
            if w.lower() in text:
                flags.append(f"인증확인:{w}")
        return flags, blocked
