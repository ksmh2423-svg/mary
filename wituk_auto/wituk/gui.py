"""버튼 클릭 화면 (윈도우용, 파이썬 기본 tkinter 사용)."""
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .pipeline import CONFIG_DIR, ROOT, load_settings, run
from .sources import excel_import


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("위탁판매 자동화")
        self.geometry("760x640")
        self.cfg = load_settings()
        self.q = queue.Queue()
        self.last_out = None
        self._build()
        self.after(200, self._drain)

    def _build(self):
        pad = {"padx": 8, "pady": 4}
        f1 = ttk.LabelFrame(self, text="① 상품 가져오기")
        f1.pack(fill="x", **pad)
        self.src = tk.StringVar(value="excel")
        ttk.Radiobutton(f1, text="도매처 엑셀/CSV 파일", variable=self.src, value="excel").grid(row=0, column=0, sticky="w")
        self.excel_path = tk.StringVar(value=str(ROOT / "sample" / "샘플_도매상품.xlsx"))
        ttk.Entry(f1, textvariable=self.excel_path, width=60).grid(row=0, column=1)
        ttk.Button(f1, text="찾기", command=self._pick_excel).grid(row=0, column=2)
        ttk.Radiobutton(f1, text="도매꾹 API 검색", variable=self.src, value="domeggook").grid(row=1, column=0, sticky="w")
        g = ttk.Frame(f1)
        g.grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Label(g, text="키워드").pack(side="left")
        self.kw = tk.StringVar()
        ttk.Entry(g, textvariable=self.kw, width=16).pack(side="left")
        ttk.Label(g, text=" 개수").pack(side="left")
        self.maxn = tk.IntVar(value=30)
        ttk.Spinbox(g, from_=1, to=500, textvariable=self.maxn, width=5).pack(side="left")
        ttk.Label(g, text=" API키").pack(side="left")
        self.key = tk.StringVar(value=os.environ.get("DOMEGGOOK_API_KEY", ""))
        ttk.Entry(g, textvariable=self.key, width=18, show="*").pack(side="left")

        f2 = ttk.LabelFrame(self, text="② 올릴 마켓 · 양식 파일(선택)")
        f2.pack(fill="x", **pad)
        self.mk_vars, self.tpl_vars = {}, {}
        for i, (mk, m) in enumerate(self.cfg["markets"].items()):
            v = tk.BooleanVar(value=True)
            self.mk_vars[mk] = v
            ttk.Checkbutton(f2, text=m.get("label", mk), variable=v).grid(row=i, column=0, sticky="w")
            t = tk.StringVar()
            self.tpl_vars[mk] = t
            ttk.Entry(f2, textvariable=t, width=55).grid(row=i, column=1)
            ttk.Button(f2, text="양식", command=lambda t=t: self._pick_tpl(t)).grid(row=i, column=2)
        ttk.Label(f2, text="※ 양식을 비워 두면 기본 열 이름으로 만들어요. 마켓에서 받은 양식을 넣으면 거기에 바로 채워요.",
                  foreground="#666").grid(row=99, column=0, columnspan=3, sticky="w")

        f3 = ttk.LabelFrame(self, text="③ 가격 · 옵션")
        f3.pack(fill="x", **pad)
        self.margin = tk.DoubleVar(value=round(self.cfg["margin_rate"] * 100, 1))
        self.ship = tk.IntVar(value=self.cfg["my_shipping_fee"])
        self.do_img = tk.BooleanVar(value=True)
        ttk.Label(f3, text="마진율(%)").pack(side="left")
        ttk.Entry(f3, textvariable=self.margin, width=6).pack(side="left")
        ttk.Label(f3, text="  내 배송비(원)").pack(side="left")
        ttk.Entry(f3, textvariable=self.ship, width=7).pack(side="left")
        ttk.Checkbutton(f3, text="이미지 내려받아 정리", variable=self.do_img).pack(side="left", padx=10)
        ttk.Button(f3, text="설정 폴더 열기", command=lambda: self._open(CONFIG_DIR)).pack(side="right")

        f4 = ttk.Frame(self)
        f4.pack(fill="x", **pad)
        self.go = ttk.Button(f4, text="▶ 시작", command=self._start)
        self.go.pack(side="left")
        self.open_btn = ttk.Button(f4, text="결과 폴더 열기", command=lambda: self._open(self.last_out), state="disabled")
        self.open_btn.pack(side="left", padx=6)
        self.bar = ttk.Progressbar(f4, mode="indeterminate", length=250)
        self.bar.pack(side="right")

        self.log = tk.Text(self, height=18, wrap="word")
        self.log.pack(fill="both", expand=True, **pad)
        self._log("준비 완료. 샘플 파일로 바로 [▶ 시작]을 눌러 보셔도 돼요.")

    def _pick_excel(self):
        p = filedialog.askopenfilename(filetypes=[("엑셀/CSV", "*.xlsx *.xlsm *.csv")])
        if p:
            self.excel_path.set(p)
            self.src.set("excel")

    def _pick_tpl(self, var):
        p = filedialog.askopenfilename(filetypes=[("엑셀", "*.xlsx *.xlsm")])
        if p:
            var.set(p)

    def _open(self, path):
        if not path:
            return
        if sys.platform.startswith("win"):
            os.startfile(path)
        else:
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])

    def _log(self, msg):
        self.q.put(str(msg))

    def _drain(self):
        while not self.q.empty():
            self.log.insert("end", self.q.get() + "\n")
            self.log.see("end")
        self.after(200, self._drain)

    def _start(self):
        markets = [m for m, v in self.mk_vars.items() if v.get()]
        if not markets:
            messagebox.showwarning("마켓 선택", "올릴 마켓을 하나 이상 골라 주세요.")
            return
        try:
            self.cfg["margin_rate"] = float(self.margin.get()) / 100
            self.cfg["my_shipping_fee"] = int(self.ship.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("숫자 확인", "마진율과 배송비는 숫자로 넣어 주세요.")
            return
        self.go.config(state="disabled")
        self.bar.start(10)
        threading.Thread(target=self._work, args=(markets,), daemon=True).start()

    def _work(self, markets):
        try:
            if self.src.get() == "excel":
                products = excel_import.load_products(self.excel_path.get(), self.cfg.get("excel_import_columns"))
            else:
                from .sources.domeggook import DomeggookClient
                client = DomeggookClient(self.key.get().strip(), dump_dir=ROOT / "output" / "_api_raw")
                products = client.collect(self.kw.get().strip(), "", int(self.maxn.get()), progress=self._log)
            self._log(f"불러온 상품: {len(products)}개")
            tpls = {m: v.get().strip() for m, v in self.tpl_vars.items() if v.get().strip()}
            out, files = run(products, self.cfg, markets, ROOT / "output", tpls, self.do_img.get(),
                             CONFIG_DIR, log=self._log)
            self.last_out = out
            self._log(f"\n✅ 완료! 결과 폴더: {out}")
            self.after(0, lambda: self.open_btn.config(state="normal"))
        except Exception as e:
            self._log(f"\n❌ 오류: {e}")
        finally:
            self.after(0, lambda: (self.bar.stop(), self.go.config(state="normal")))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
