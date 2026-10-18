"""상품 이미지 정사각형 정리 (Pillow 하나만 필요).

하는 일: 사진 방향(EXIF) 바로잡기 → 둘레의 흰 여백 잘라내기 → 지정 크기 정사각형
캔버스 가운데에 여백 비율만큼 띄워 놓기 → JPG/PNG 로 저장.

인터넷에서 내려받는 기능은 없습니다. 파일 경로, bytes, PIL 이미지 중 하나를 넣으세요.
설정(크기·여백·배경색 등)은 settings.csv 에 있고, dict 로 직접 넘겨도 됩니다.
"""
import csv
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

DEFAULTS = {
    "size": 1000,             # 결과 한 변 길이(px)
    "padding_ratio": 0.05,    # 한쪽 여백 비율 (0.05 = 5%)
    "background": "#FFFFFF",
    "trim": True,             # 원래 있던 흰 여백 잘라내기
    "trim_tolerance": 10,     # 배경색과 이만큼 차이 나면 '내용'으로 봄 (0~255)
    "max_upscale": 2.0,       # 최대 몇 배까지 키울지 (1.0 = 키우지 않음, 많이 키우면 흐려짐)
    "min_source_px": 500,     # 원본 긴 변이 이보다 작으면 경고
    "format": "JPEG",
    "jpeg_quality": 90,
}


@dataclass
class SquareSettings:
    size: int = DEFAULTS["size"]
    padding_ratio: float = DEFAULTS["padding_ratio"]
    background: str = DEFAULTS["background"]
    trim: bool = DEFAULTS["trim"]
    trim_tolerance: int = DEFAULTS["trim_tolerance"]
    max_upscale: float = DEFAULTS["max_upscale"]
    min_source_px: int = DEFAULTS["min_source_px"]
    format: str = DEFAULTS["format"]
    jpeg_quality: int = DEFAULTS["jpeg_quality"]

    def __post_init__(self):
        if self.size <= 0:
            raise ValueError("size 는 1 이상이어야 합니다.")
        if not 0 <= self.padding_ratio < 0.5:
            raise ValueError("padding_ratio 는 0 이상 0.5 미만이어야 합니다.")
        if self.max_upscale < 1:
            raise ValueError("max_upscale 은 1.0 이상이어야 합니다.")
        self.format = self.format.upper().replace("JPG", "JPEG")
        if self.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("format 은 JPEG, PNG, WEBP 중 하나입니다.")

    @classmethod
    def from_dict(cls, d):
        def b(v):
            return v if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes", "y")
        d = {k: v for k, v in (d or {}).items() if str(v).strip() != ""}
        return cls(
            size=int(d.get("size", DEFAULTS["size"])),
            padding_ratio=float(d.get("padding_ratio", DEFAULTS["padding_ratio"])),
            background=str(d.get("background", DEFAULTS["background"])),
            trim=b(d.get("trim", DEFAULTS["trim"])),
            trim_tolerance=int(d.get("trim_tolerance", DEFAULTS["trim_tolerance"])),
            max_upscale=float(d.get("max_upscale", DEFAULTS["max_upscale"])),
            min_source_px=int(d.get("min_source_px", DEFAULTS["min_source_px"])),
            format=str(d.get("format", DEFAULTS["format"])),
            jpeg_quality=int(d.get("jpeg_quality", DEFAULTS["jpeg_quality"])),
        )

    @classmethod
    def from_csv(cls, path, encoding="utf-8-sig"):
        """settings.csv (열: key, value, note)"""
        d = {}
        with open(Path(path), newline="", encoding=encoding) as f:
            for row in csv.DictReader(f):
                key = (row.get("key") or "").strip()
                if key and not key.startswith("#"):
                    d[key] = (row.get("value") or "").strip()
        return cls.from_dict(d)


@dataclass
class SquareResult:
    image: Image.Image          # 결과 이미지 (RGB 정사각형)
    source_size: tuple          # 원본 (가로, 세로)
    content_box: tuple          # 잘라낸 뒤 남은 영역 (왼, 위, 오른, 아래) — 원본 기준
    warnings: list = field(default_factory=list)


def _rgb(color):
    from PIL import ImageColor
    return ImageColor.getrgb(color)[:3]


def _flatten(img, bg):
    """투명 배경은 배경색으로 채워 RGB 로 만든다."""
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, bg)
        canvas.paste(rgba, mask=rgba.getchannel("A"))
        return canvas
    return img.convert("RGB")


def _content_box(img, bg, tolerance):
    diff = ImageChops.difference(img, Image.new("RGB", img.size, bg)).convert("L")
    mask = diff.point(lambda v: 255 if v > tolerance else 0)
    return mask.getbbox()


def make_square(image, settings=None):
    """PIL 이미지 → SquareResult. 원본은 바꾸지 않는다."""
    s = settings or SquareSettings()
    bg = _rgb(s.background)
    img = _flatten(image, bg)
    src_size = img.size
    warnings = []

    box = (0, 0) + img.size
    if s.trim:
        found = _content_box(img, bg, s.trim_tolerance)
        if found is None:
            warnings.append("내용이 없는(배경색뿐인) 이미지")
        else:
            box = found
            img = img.crop(box)

    if max(src_size) < s.min_source_px:
        warnings.append(f"원본이 작음({src_size[0]}x{src_size[1]})")

    inner = max(1, round(s.size * (1 - 2 * s.padding_ratio)))
    scale = inner / max(img.size)
    if scale > s.max_upscale:
        warnings.append(f"{scale:.1f}배 확대가 필요하지만 {s.max_upscale:g}배까지만 키움(상품이 작게 보임)")
        scale = s.max_upscale
    if scale != 1:
        new = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        img = img.resize(new, Image.LANCZOS)

    canvas = Image.new("RGB", (s.size, s.size), bg)
    canvas.paste(img, ((s.size - img.width) // 2, (s.size - img.height) // 2))
    return SquareResult(canvas, src_size, box, warnings)


def to_bytes(result, settings=None):
    s = settings or SquareSettings()
    buf = BytesIO()
    kw = {"quality": s.jpeg_quality} if s.format in ("JPEG", "WEBP") else {}
    result.image.save(buf, s.format, **kw)
    return buf.getvalue()


def square_bytes(data, settings=None):
    """이미지 bytes → (결과 bytes, SquareResult). 예: 이미 내려받은 응답 내용."""
    with Image.open(BytesIO(data)) as im:
        res = make_square(im, settings)
    return to_bytes(res, settings), res


def square_file(src, dest, settings=None):
    """파일 → 파일. 반환: SquareResult. 저장 폴더가 없으면 만든다."""
    s = settings or SquareSettings()
    with Image.open(src) as im:
        res = make_square(im, s)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(to_bytes(res, s))
    return res
