@echo off
echo ========================================
echo Naver News Crawler - Anti 403 Mode
echo ========================================
echo.

REM UTF-8 setting
chcp 65001 > nul

REM Environment variables
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo [Settings]
echo - Request delay: 4 seconds
echo - Max URLs: 30
echo - Retry wait: increased
echo.

REM Run with safe parameters
python main.py --keyword "test" --days 1 --delay 4.0 --content-delay 4.5 --max-urls 30

echo.
echo Task completed.
pause