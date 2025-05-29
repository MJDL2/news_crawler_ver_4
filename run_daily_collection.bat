@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 네이버 뉴스 날짜별 수집 스크립트
echo ========================================
echo.

REM 검색어 입력
set /p QUERY="검색어를 입력하세요: "
if "%QUERY%"=="" (
    echo 검색어가 필요합니다!
    pause
    exit /b
)

REM 기간 선택
echo.
echo 수집 기간을 선택하세요:
echo   1. 일주일 (1w)
echo   2. 한달 (1m)
echo   3. 3개월 (3m)
echo   4. 커스텀 날짜 입력
echo.
set /p PERIOD_CHOICE="선택 [1]: "
if "%PERIOD_CHOICE%"=="" set PERIOD_CHOICE=1

if "%PERIOD_CHOICE%"=="1" (
    set PERIOD=1w
) else if "%PERIOD_CHOICE%"=="2" (
    set PERIOD=1m
) else if "%PERIOD_CHOICE%"=="3" (
    set PERIOD=3m
) else if "%PERIOD_CHOICE%"=="4" (
    set PERIOD=custom
    set /p START_DATE="시작 날짜 (YYYYMMDD): "
    set /p END_DATE="종료 날짜 (YYYYMMDD): "
) else (
    set PERIOD=1w
)

REM 일별 수집 개수
echo.
set /p DAILY_LIMIT="일별 수집 개수 [10]: "
if "%DAILY_LIMIT%"=="" set DAILY_LIMIT=10

REM 본문 추출 여부
echo.
set /p EXTRACT="본문도 추출하시겠습니까? (Y/n): "
if /i "%EXTRACT%"=="n" (
    set EXTRACT_FLAG=
) else (
    set EXTRACT_FLAG=--extract-content
)

REM 명령 실행
echo.
echo 수집을 시작합니다...
echo ========================================

if "%PERIOD%"=="custom" (
    python main.py "%QUERY%" --period custom --start-date %START_DATE% --end-date %END_DATE% --daily --daily-limit %DAILY_LIMIT% %EXTRACT_FLAG% --extraction-mode even_distribution
) else (
    python main.py "%QUERY%" --period %PERIOD% --daily --daily-limit %DAILY_LIMIT% %EXTRACT_FLAG% --extraction-mode even_distribution
)

echo.
echo ========================================
echo 수집이 완료되었습니다!
echo 결과는 data/news_data 폴더를 확인하세요.
echo ========================================
echo.
pause