@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv (
  python -m venv .venv
  .venv\Scripts\pip install -r requirements.txt
)
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --noconfirm --windowed --name 위탁판매자동화 run.py
xcopy /e /i /y config dist\위탁판매자동화\config >nul
xcopy /e /i /y sample dist\위탁판매자동화\sample >nul
echo.
echo dist\위탁판매자동화 폴더에 실행 파일이 만들어졌습니다. 폴더째 옮겨서 쓰세요.
pause
