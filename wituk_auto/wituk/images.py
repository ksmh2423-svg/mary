"""이미지 내려받기 → 정사각형 흰 여백 → 지정 크기로 리사이즈 → JPG 저장."""
import hashlib
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image


def _open(src, http):
    if str(src).startswith("http"):
        r = http.get(src, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    return Image.open(src)


def to_square(img, size=1000, pad_ratio=0.05, bg=(255, 255, 255)):
    img = img.convert("RGBA")
    # 원래 있던 흰 여백 잘라내기
    gray = Image.new("RGBA", img.size, bg + (255,))
    diff = Image.alpha_composite(gray, img).convert("L").point(lambda v: 255 if v < 245 else 0)
    box = diff.getbbox()
    if box:
        img = img.crop(box)
    inner = int(size * (1 - 2 * pad_ratio))
    img.thumbnail((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), bg)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    return canvas


def process_product_images(p, out_dir, cfg, http=None, log=print):
    http = http or requests.Session()
    out = Path(out_dir) / f"{p.source}_{p.source_id}"
    out.mkdir(parents=True, exist_ok=True)
    size = cfg.get("image_size", 1000)
    pad = cfg.get("image_padding", 0.05)
    saved = []
    for i, src in enumerate(p.images[: cfg.get("max_images", 10)], 1):
        name = f"{i:02d}_{hashlib.md5(str(src).encode()).hexdigest()[:6]}.jpg"
        dest = out / name
        if not dest.exists():
            try:
                to_square(_open(src, http), size, pad).save(dest, "JPEG", quality=90)
            except Exception as e:
                log(f"  이미지 실패({p.source_id} #{i}): {e}")
                continue
        saved.append(str(dest))
    return saved
