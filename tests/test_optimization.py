#!/usr/bin/env python
"""
최적화 후 테스트 스크립트
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_interactive_mode():
    """대화형 모드 테스트"""
    print("=== 대화형 모드 시뮬레이션 테스트 ===")
    
    from src.ui.interactive import InteractiveInterface
    
    # InteractiveInterface의 get_input 메서드를 모킹
    test_inputs = {
        "검색어": "테스트",
        "검색 기간": "custom",
        "시작일 (YYYYMMDD)": "20250601",
        "종료일 (YYYYMMDD)": "20250603",
        "정렬 방식": "recent",
        "뉴스 유형": "all",
        "최대 페이지 수 (0=무제한)": "2",
        "최대 URL 수 (0=무제한)": "50",
        "URL 유형": "all",
        "병합시 최종 추출 개수 (0=전체)": "0",  # 전체 병합 테스트
        "일별 최대 수집 개수": "20",
        "추출 방식": "balanced",
        "본문 저장 디렉토리": "data/test_news",
        "URL 저장 디렉토리": "data/test_urls"
    }
    
    # 원래 메서드 백업
    original_get_input = InteractiveInterface.get_input
    original_get_yes_no = InteractiveInterface.get_yes_no
    
    # 모킹 함수
    def mock_get_input(self, prompt, default=None, choices=None):
        for key, value in test_inputs.items():
            if key in prompt:
                print(f"{prompt} [{default}]: {value}")
                return value
        return default
    
    def mock_get_yes_no(self, prompt, default=True):
        print(f"{prompt} (y/n) [{'Y' if default else 'N'}]: y")
        return True
    
    # 메서드 교체
    InteractiveInterface.get_input = mock_get_input
    InteractiveInterface.get_yes_no = mock_get_yes_no
    
    try:
        # 대화형 인터페이스 실행
        interface = InteractiveInterface()
        options = interface.run()
        
        if options:
            print("\n=== 수집된 옵션 ===")
            for key, value in options.items():
                print(f"{key}: {value}")
            
            # 주요 설정 확인
            assert options['content_limit'] == 0, "content_limit이 0(전체)이어야 합니다"
            assert options.get('daily_limit', 0) == 20, "daily_limit이 20이어야 합니다"
            assert options['extraction_mode'] == 'balanced', "extraction_mode가 balanced여야 합니다"
            
            print("\n[PASS] 모든 테스트 통과!")
        else:
            print("\n[FAIL] 옵션 수집 실패")
    
    finally:
        # 원래 메서드 복원
        InteractiveInterface.get_input = original_get_input
        InteractiveInterface.get_yes_no = original_get_yes_no

def test_balanced_extraction():
    """balanced 추출 방식 테스트"""
    print("\n=== Balanced 추출 방식 테스트 ===")
    
    from src.core.daily_collector import NaverNewsDailyCollector
    
    collector = NaverNewsDailyCollector()
    
    # 테스트 데이터
    test_contents = []
    for date in ['2025-06-01', '2025-06-02', '2025-06-03']:
        for i in range(10):
            test_contents.append({
                'title': f'{date} 기사 {i+1}',
                'collection_date': date
            })
    
    # 전체 병합 테스트 (content_limit = 0)
    result = collector._select_contents_by_mode(test_contents, 0, 'balanced')
    print(f"전체 병합: {len(result)}개 (예상: 30개)")
    assert len(result) == 30, "전체 데이터가 포함되어야 합니다"
    
    # 제한된 병합 테스트 (content_limit = 15)
    result = collector._select_contents_by_mode(test_contents, 15, 'balanced')
    print(f"제한 병합: {len(result)}개 (예상: 15개)")
    
    # 날짜별 분포 확인
    date_count = {}
    for content in result:
        date = content['collection_date']
        date_count[date] = date_count.get(date, 0) + 1
    
    print("날짜별 분포:")
    for date, count in sorted(date_count.items()):
        print(f"  {date}: {count}개")
    
    # 균등 분배 확인
    counts = list(date_count.values())
    assert max(counts) - min(counts) <= 1, "날짜별 균등 분배가 되어야 합니다"
    
    print("\n[PASS] Balanced 추출 테스트 통과!")

def test_cli_daily_limit():
    """CLI daily_limit 처리 테스트"""
    print("\n=== CLI daily_limit 처리 테스트 ===")
    
    from src.ui.cli import CLI
    import argparse
    
    cli = CLI()
    
    # 테스트용 args 생성
    args = argparse.Namespace(
        interactive=False,
        query='테스트',
        period='custom',
        start_date='20250601',
        end_date='20250603',
        sort='recent',
        type='all',
        pages=2,
        max_urls=50,
        url_type='all',
        extract_content=True,
        content_limit=0,
        extraction_mode='balanced',
        output='data/test_news',
        url_output='data/test_urls',
        daily_limit=25,
        delay=0.5,
        content_delay=0.5,
        verbose=False
    )
    
    # _should_use_daily_collector 테스트
    should_use = cli._should_use_daily_collector(args)
    print(f"날짜별 수집 모드 사용: {should_use}")
    assert should_use == True, "날짜별 수집 모드가 활성화되어야 합니다"
    
    print("\n[PASS] CLI 테스트 통과!")

if __name__ == "__main__":
    print("네이버 뉴스 크롤러 최적화 테스트")
    print("=" * 50)
    
    try:
        test_interactive_mode()
        test_balanced_extraction()
        test_cli_daily_limit()
        
        print("\n" + "=" * 50)
        print("[PASS] 모든 테스트 완료!")
        print("\n주요 변경사항:")
        print("1. content_limit 기본값: 20 -> 0 (전체)")
        print("2. balanced 추출 방식 지원 완료")
        print("3. 일별 수집 제한 별도 입력 추가")
        print("4. UI 안내 문구 개선")
        
    except Exception as e:
        print(f"\n[FAIL] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
