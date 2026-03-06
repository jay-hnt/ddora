@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/2] PyInstaller 설치 중...
pip install pyinstaller -q
echo [2/2] exe 빌드 중... (잠시 걸립니다)
python -m PyInstaller --onefile --windowed --name "StairJump" ^
  --add-data "image;image" ^
  --hidden-import=config --hidden-import=game ^
  --exclude-module numpy ^
  --exclude-module matplotlib ^
  --exclude-module PIL ^
  --exclude-module scipy ^
  main.py
echo.
echo ========================================
echo   빌드 완료!
echo   아래 파일 하나만 상대방에게 전달하세요.
echo   dist\StairJump.exe
echo ========================================
echo   받는 사람: exe 더블클릭만 하면 실행됩니다 (Python 불필요).
echo ========================================
pause
