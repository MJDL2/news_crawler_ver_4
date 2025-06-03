@echo off
echo ========================================
echo    네이버 뉴스 크롤러 v4.2.1 사용법
echo ========================================
echo.
echo 사용법: python main.py [옵션] 검색어
echo.
echo 옵션:
echo   -h, --help            도움말 표시
echo   -i, --interactive     대화형 모드로 실행
echo.
echo 필수 인자:
echo   검색어                검색할 키워드 (대화형 모드에서는 선택적)
echo.
echo 검색 옵션:
echo   --period {all,1h,1d,1w,1m,3m,6m,1y,custom}
echo                         검색 기간 (기본값: 1m)
echo   --start-date DATE     시작일 (YYYYMMDD 형식, --period=custom 필요)
echo   --end-date DATE       종료일 (YYYYMMDD 형식, --period=custom 필요)
echo   --sort {relevance,recent,oldest}
echo                         정렬 방식 (기본값: relevance)
echo   --type {all,photo,video,print,press_release,auto}
echo                         뉴스 유형 (기본값: all)
echo.
echo 수집 옵션:
echo   --pages N             수집할 페이지 수 (0=무제한, 기본값: 0)
echo   --max-urls N          수집할 최대 URL 개수 (0=제한 없음, 기본값: 0)
echo   --url-type {all,naver,original}
echo                         수집할 URL 유형 (기본값: all)
echo.
echo 날짜별 수집 옵션:
echo   --daily               날짜별 수집 모드 사용
echo   --daily-limit N       일별 수집 개수 제한 (기본값: 10)
echo   --extraction-mode {sequential,even_distribution,recent_first}
echo                         본문 추출 방식 (기본값: sequential)
echo.
echo 본문 추출 옵션:
echo   --extract-content     뉴스 본문 추출 여부
echo   --content-limit N     추출할 뉴스 본문 수 제한 (0=전체, 기본값: 0)
echo.
echo 지연 시간 옵션:
echo   --delay SECONDS       URL 요청 간 지연 시간(초) (기본값: 1.0)
echo   --content-delay SECONDS
echo                         본문 추출 시 요청 간 지연 시간(초) (기본값: 1.5)
echo.
echo 출력 옵션:
echo   --output DIR          뉴스 데이터 저장 디렉토리 (기본값: data/news_data)
echo   --url-output DIR      URL 데이터 저장 디렉토리 (기본값: data/url_data)
echo.
echo 기타 옵션:
echo   -v, --verbose         상세 로그 출력
echo.
echo 사용 예시:
echo   python main.py "원전" --period 1w --extract-content
echo   python main.py "경제" --period custom --start-date 20250101 --end-date 20250131
echo   python main.py -i  (대화형 모드)
echo.
pause
