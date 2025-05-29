# 프록시를 통한 네이버 뉴스 크롤러 실행 스크립트

Write-Host "프록시를 통한 네이버 뉴스 크롤러 실행" -ForegroundColor Green
Write-Host ""

# 프록시 설정 (여기에 실제 프록시 주소를 입력하세요)
$env:HTTP_PROXY = "http://your-proxy-server:port"
$env:HTTPS_PROXY = "http://your-proxy-server:port"

Write-Host "현재 프록시 설정:" -ForegroundColor Yellow
Write-Host "HTTP_PROXY=$env:HTTP_PROXY"
Write-Host "HTTPS_PROXY=$env:HTTPS_PROXY"
Write-Host ""

# UTF-8 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# 크롤러 실행 (지연 시간 증가)
Write-Host "크롤러 실행 중..." -ForegroundColor Cyan
python main.py $args --delay 3.0 --content-delay 3.5

Write-Host ""
Write-Host "완료! 프록시 설정이 해제됩니다." -ForegroundColor Green

# 프록시 설정 해제
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")