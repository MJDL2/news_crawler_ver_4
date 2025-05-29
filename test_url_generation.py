"""
네이버 뉴스 검색 URL 생성 테스트
"""

import sys
sys.path.append('src')

from src.models.search_options import NaverNewsSearchOption
from datetime import datetime

def test_url_generation():
    """날짜별 URL 생성 테스트"""
    print("=== 네이버 뉴스 검색 URL 생성 테스트 ===")
    
    # 테스트용 검색 옵션 생성
    search_option = NaverNewsSearchOption("원전")
    
    # 날짜별 URL 생성 테스트
    test_dates = ['20250520', '20250521', '20250529']
    
    for date_str in test_dates:
        search_option.set_period(
            NaverNewsSearchOption.PERIOD_CUSTOM, 
            start_date=date_str, 
            end_date=date_str
        )
        search_option.set_sort(NaverNewsSearchOption.SORT_BY_RECENT)
        
        url = search_option.build_url()
        print(f"\n날짜: {date_str}")
        print(f"URL: {url}")
        print(f"URL 길이: {len(url)}")
        
        # URL 파라미터 분석
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        print(f"ds (시작일): {params.get('ds', ['없음'])}")
        print(f"de (종료일): {params.get('de', ['없음'])}")
        print(f"pd (기간): {params.get('pd', ['없음'])}")
        print(f"nso: {params.get('nso', ['없음'])}")

if __name__ == "__main__":
    test_url_generation()
