#!/usr/bin/env python
"""
병합 기능 테스트 스크립트
"""

import os
import sys
import json
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.core.daily_collector import NaverNewsDailyCollector
from src.utils.config import Config

def test_merge_function():
    """병합 기능 테스트"""
    
    # NaverNewsDailyCollector 인스턴스 생성
    collector = NaverNewsDailyCollector()
    
    # 테스트용 컨텐츠 생성
    test_contents = []
    dates = ['2025-05-20', '2025-05-21', '2025-05-22']
    
    for date in dates:
        for i in range(10):
            content = {
                'title': f'{date} 테스트 기사 {i+1}',
                'content': f'이것은 {date}의 테스트 컨텐츠입니다.',
                'collection_date': date
            }
            test_contents.append(content)
    
    print(f"테스트 컨텐츠 생성: 총 {len(test_contents)}개")
    
    # 테스트 1: sequential 방식
    print("\n=== Sequential 방식 테스트 ===")
    selected = collector._select_contents_by_mode(test_contents, 15, 'sequential')
    print(f"선택된 컨텐츠: {len(selected)}개")
    for content in selected[:5]:
        print(f"  - {content['title']}")
    
    # 테스트 2: balanced 방식  
    print("\n=== Balanced 방식 테스트 ===")
    selected = collector._select_contents_by_mode(test_contents, 15, 'balanced')
    print(f"선택된 컨텐츠: {len(selected)}개")
    
    # 날짜별 분포 확인
    date_count = {}
    for content in selected:
        date = content['collection_date']
        date_count[date] = date_count.get(date, 0) + 1
    
    print("날짜별 분포:")
    for date, count in sorted(date_count.items()):
        print(f"  - {date}: {count}개")
    
    # 테스트 3: even_distribution 방식 (balanced와 동일해야 함)
    print("\n=== Even Distribution 방식 테스트 ===")
    selected = collector._select_contents_by_mode(test_contents, 15, 'even_distribution')
    print(f"선택된 컨텐츠: {len(selected)}개")
    
    # 날짜별 분포 확인
    date_count = {}
    for content in selected:
        date = content['collection_date']
        date_count[date] = date_count.get(date, 0) + 1
    
    print("날짜별 분포:")
    for date, count in sorted(date_count.items()):
        print(f"  - {date}: {count}개")

if __name__ == "__main__":
    print("네이버 뉴스 크롤러 - 병합 기능 테스트")
    print("=" * 50)
    
    try:
        test_merge_function()
        print("\n테스트 완료!")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
