#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 import 테스트
"""

def test_import():
    """Import 테스트만 진행"""
    try:
        from src.core.daily_collector import NaverNewsDailyCollector
        print("Import successful")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def test_instantiation():
    """객체 생성 테스트"""
    try:
        from src.core.daily_collector import NaverNewsDailyCollector
        collector = NaverNewsDailyCollector()
        print("Instantiation successful")
        return True
    except Exception as e:
        print(f"Instantiation failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing imports...")
    import_result = test_import()
    print("Testing instantiation...")
    inst_result = test_instantiation()
    
    if import_result and inst_result:
        print("All basic tests passed!")
    else:
        print("Some tests failed!")
