"""
URL 수집 제한 로직 수정 테스트 스크립트
"""

import sys
import os
sys.path.append('src')

from datetime import datetime
from src.core.daily_collector import NaverNewsDailyCollector

def test_daily_limit_fix():
    """일별 수집 제한 수정 테스트"""
    print("=== URL 수집 제한 로직 수정 테스트 ===")
    
    collector = NaverNewsDailyCollector()
    
    # 테스트 설정
    query = "원전"
    test_date = datetime(2025, 5, 29)
    daily_limit = 15  # 15개로 설정
    
    print(f"검색어: {query}")  
    print(f"날짜: {test_date.strftime('%Y-%m-%d')}")
    print(f"일별 제한: {daily_limit}개")
    print(f"기대 결과: {daily_limit}개 수집 (또는 해당 날짜의 최대 가능 개수)")
    print()
    
    # 단일 날짜 수집 테스트
    result = collector.collect_single_day(
        query=query,
        date=test_date,
        sort='recent',
        news_type='all',
        extract_content=True,
        daily_limit=daily_limit,
        save_intermediate=False
    )
    
    print(f"\n=== 테스트 결과 ===")
    print(f"수집된 URL: {result.get('urls_collected', 0)}개")
    print(f"추출된 본문: {result.get('contents_extracted', 0)}개")
    print(f"상태: {result.get('status', 'unknown')}")
    
    # 결과 분석
    urls_collected = result.get('urls_collected', 0)
    if urls_collected == daily_limit:
        print(f"🎉 성공: 정확히 {daily_limit}개 수집됨")
    elif urls_collected > 8:  # 기존 8개 제한을 넘어섰다면 개선됨
        print(f"✅ 개선됨: {urls_collected}개 수집 (기존 8개 → {urls_collected}개)")
    elif urls_collected == 8:
        print(f"❌ 여전히 8개 제한: 추가 확인 필요")
    else:
        print(f"⚠️  예상과 다른 결과: {urls_collected}개")
    
    return result

if __name__ == "__main__":
    result = test_daily_limit_fix()
