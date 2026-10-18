"""실행: python -m unittest test_image_square  (또는 pytest). Pillow 필요."""
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from image_square import SquareSettings, make_square, square_bytes, square_file  # noqa: E402


def product(w=1200, h=600, box=(500, 150, 700, 450), color=(200, 0, 0), mode="RGB"):
    bg = (255, 255, 255, 0) if mode == "RGBA" else "white"
    im = Image.new(mode, (w, h), bg)
    ImageDraw.Draw(im).rectangle(box, fill=color)
    return im


class TestImageSquare(unittest.TestCase):
    def test_output_is_square_with_padding(self):
        s = SquareSettings(size=1000, padding_ratio=0.05, max_upscale=5)
        res = make_square(product(), s)
        self.assertEqual(res.image.size, (1000, 1000))
        self.assertEqual(res.image.mode, "RGB")
        # 내용(세로가 더 긴 빨간 상자)이 위아래 5% 여백을 남기고 꽉 참
        bbox = Image.eval(res.image.convert("L"), lambda v: 255 if v < 200 else 0).getbbox()
        self.assertAlmostEqual(bbox[1], 50, delta=2)
        self.assertAlmostEqual(bbox[3], 950, delta=2)

    def test_trims_existing_white_margin(self):
        res = make_square(product(), SquareSettings())
        self.assertEqual(res.content_box, (500, 150, 701, 451))
        self.assertEqual(res.source_size, (1200, 600))

    def test_no_trim_keeps_whole_frame(self):
        res = make_square(product(), SquareSettings(trim=False))
        self.assertEqual(res.content_box, (0, 0, 1200, 600))

    def test_centered(self):
        res = make_square(product(), SquareSettings(size=500))
        bbox = Image.eval(res.image.convert("L"), lambda v: 255 if v < 200 else 0).getbbox()
        self.assertAlmostEqual((bbox[0] + bbox[2]) / 2, 250, delta=2)
        self.assertAlmostEqual((bbox[1] + bbox[3]) / 2, 250, delta=2)

    def test_transparent_png_gets_background(self):
        res = make_square(product(mode="RGBA", color=(0, 0, 255, 255)), SquareSettings(size=200))
        self.assertEqual(res.image.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(res.image.getpixel((100, 100)), (0, 0, 255))

    def test_small_image_upscale_capped(self):
        # 내용 41x51 → 900 이 되려면 17배 필요하지만 기본 2배까지만
        res = make_square(product(100, 80, (10, 10, 50, 60)), SquareSettings(size=1000))
        bbox = Image.eval(res.image.convert("L"), lambda v: 255 if v < 200 else 0).getbbox()
        self.assertAlmostEqual(bbox[3] - bbox[1], 102, delta=2)
        self.assertTrue(any("작음" in w for w in res.warnings))
        self.assertTrue(any("2배까지만" in w for w in res.warnings))

    def test_no_upscale_when_max_is_one(self):
        res = make_square(product(100, 80, (10, 10, 50, 60)), SquareSettings(size=1000, max_upscale=1.0))
        bbox = Image.eval(res.image.convert("L"), lambda v: 255 if v < 200 else 0).getbbox()
        self.assertAlmostEqual(bbox[3] - bbox[1], 51, delta=1)

    def test_blank_image_warns(self):
        res = make_square(Image.new("RGB", (300, 300), "white"), SquareSettings(size=100))
        self.assertEqual(res.image.size, (100, 100))
        self.assertTrue(any("내용이 없는" in w for w in res.warnings))

    def test_exif_orientation_applied(self):
        im = product(600, 300, (100, 100, 200, 150))
        exif = Image.Exif()
        exif[0x0112] = 6  # 90도 회전 표시
        buf = BytesIO()
        im.save(buf, "JPEG", exif=exif)
        _, res = square_bytes(buf.getvalue(), SquareSettings(trim=False))
        self.assertEqual(res.source_size, (300, 600))

    def test_bytes_roundtrip_jpeg(self):
        buf = BytesIO()
        product().save(buf, "PNG")
        out, res = square_bytes(buf.getvalue(), SquareSettings(size=300))
        with Image.open(BytesIO(out)) as im:
            self.assertEqual((im.format, im.size), ("JPEG", (300, 300)))

    def test_file_to_file_creates_folder(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.png"
            product().save(src)
            dest = Path(d) / "new" / "b.png"
            square_file(src, dest, SquareSettings(size=200, format="png"))
            with Image.open(dest) as im:
                self.assertEqual((im.format, im.size), ("PNG", (200, 200)))
            # 원본은 그대로
            with Image.open(src) as im:
                self.assertEqual(im.size, (1200, 600))

    def test_invalid_settings(self):
        with self.assertRaises(ValueError):
            SquareSettings(padding_ratio=0.5)
        with self.assertRaises(ValueError):
            SquareSettings(size=0)
        with self.assertRaises(ValueError):
            SquareSettings(format="GIF")
        with self.assertRaises(ValueError):
            SquareSettings(max_upscale=0.5)

    def test_csv_and_blank_values(self):
        s = SquareSettings.from_csv(HERE / "settings.csv")
        self.assertEqual((s.size, s.format, s.trim, s.max_upscale), (1000, "JPEG", True, 2.0))
        self.assertEqual(SquareSettings.from_dict({"size": "", "jpg": 1}).size, 1000)


if __name__ == "__main__":
    unittest.main()
