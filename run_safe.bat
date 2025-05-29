@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo Starting crawler with anti-403 settings...
echo.

python main.py --keyword "조선" --days 1 --delay 4.0 --content-delay 4.5 --max-urls 30

echo.
pause