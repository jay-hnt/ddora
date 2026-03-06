@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
)
python main.py
if errorlevel 1 (
    echo.
    echo 실행 오류. Python과 pygame 설치 여부를 확인하세요.
    echo 설치: pip install -r requirements.txt
    pause
)
