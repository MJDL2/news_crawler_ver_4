@echo off
echo 안전 모드로 네이버 뉴스 크롤러 실행 (느린 속도)
echo.

REM UTF-8 설정
chcp 65001 > nul

echo 설정:
echo - 페이지 간 지연: 3.5초
echo - 본문 추출 간 지연: 4.0초
echo - 최대 페이지: 5
echo.

REM 크롤러 실행 (안전한 설정)
python main.py %* --delay 3.5 --content-delay 4.0 --pages 5

echo.
echo 완료!
pause