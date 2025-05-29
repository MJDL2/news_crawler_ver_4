# PowerShell 스크립트로 대화형 모드 실행
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

Write-Host "`n=== 네이버 뉴스 크롤러 대화형 모드 ===`n" -ForegroundColor Cyan

& python -u main.py -i

Write-Host "`n프로그램이 종료되었습니다." -ForegroundColor Green
Read-Host "Enter 키를 눌러 종료하세요"