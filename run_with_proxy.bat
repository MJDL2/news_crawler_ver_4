@echo off
echo 프록시를 통한 네이버 뉴스 크롤러 실행
echo.

REM 프록시 설정 (여기에 실제 프록시 주소를 입력하세요)
set HTTP_PROXY=http://your-proxy-server:port
set HTTPS_PROXY=http://your-proxy-server:port

echo 현재 프록시 설정:
echo HTTP_PROXY=%HTTP_PROXY%
echo HTTPS_PROXY=%HTTPS_PROXY%
echo.

REM UTF-8 설정
chcp 65001 > nul

REM 크롤러 실행 (지연 시간 증가)
python main.py %* --delay 3.0 --content-delay 3.5

echo.
echo 완료! 프록시 설정이 해제됩니다.

REM 프록시 설정 해제
set HTTP_PROXY=
set HTTPS_PROXY=

pause