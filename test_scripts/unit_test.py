#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네트워크 요청 없는 단위 테스트
"""

import pytest
from datetime import datetime, timedelta

def test_import():
    """Import 테스트"""
    from src.core.daily_collector import NaverNewsDailyCollector
    assert True

def test_instantiation():
    """객체 생성 테스트"""
    from src.core.daily_collector import NaverNewsDailyCollector
    collector = NaverNewsDailyCollector()
    assert collector is not None

def test_date_range_calculation():
    """날짜 범위 계산 테스트"""
    from src.core.daily_collector import NaverNewsDailyCollector
    collector = NaverNewsDailyCollector()
    
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 3)
    
    # private 메서드가 있다면 테스트 가능
    # 여기서는 기본 객체 생성만 테스트

if __name__ == '__main__':
    test_import()
    test_instantiation() 
    test_date_range_calculation()
    print("All unit tests passed!")
