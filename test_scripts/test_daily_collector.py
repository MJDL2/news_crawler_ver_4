#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
날짜별 수집기 테스트 스크립트
"""

import sys
import os

# src 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.daily_collector import NaverNewsDailyCollector
from datetime import datetime, timedelta

def test_daily_collector():
    """날짜별 수집기 테스트"""
    collector = NaverNewsDailyCollector()
    
    # 최근 2일간 데이터 수집 테스트
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    results = collector.collect_date_range(
        query='테스트',
        start_date=start_date,
        end_date=end_date,
        daily_limit=5,
        extract_content=True
    )
    
    print(f"수집 결과: {results}")

if __name__ == '__main__':
    test_daily_collector()
