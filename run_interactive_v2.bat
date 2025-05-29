@echo off
chcp 65001 > nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set PYTHONLEGACYWINDOWSSTDIO=1
echo.
echo === 네이버 뉴스 크롤러 대화형 모드 ===
echo.
python -u main.py -i
echo.
echo 프로그램이 종료되었습니다.
pause