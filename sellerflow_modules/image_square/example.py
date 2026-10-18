"""사용 예시: python example.py  → 같은 폴더 example_out/ 에 결과 저장"""
from pathlib import Path

from PIL import Image, ImageDraw

from image_square import SquareSettings, square_file

here = Path(__file__).parent
settings = SquareSettings.from_csv(here / "settings.csv")

# 시험용 가로 사진 만들기 (흰 여백이 넓은 상품 사진 흉내)
src = here / "example_out" / "src_wide.png"
src.parent.mkdir(exist_ok=True)
im = Image.new("RGB", (1200, 600), "white")
ImageDraw.Draw(im).rounded_rectangle((500, 150, 700, 450), radius=30, fill=(40, 90, 160))
im.save(src)

res = square_file(src, here / "example_out" / "square.jpg", settings)
print("원본", res.source_size, "→ 내용 영역", res.content_box, "→", res.image.size, res.warnings)
