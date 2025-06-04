"""
개선사항 테스트 스크립트

통합 설정, 세션 풀, daily_collector 등 개선된 기능을 테스트합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# 프로젝트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import get_config
from src.utils.session_pool import get_session_pool
from src.core.daily_collector import NaverNewsDailyCollector
from src.core.content_extractor import NaverNewsContentExtractor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_unified_config():
    """통합 설정 파일 테스트"""
    print("\n=== 통합 설정 파일 테스트 ===")
    
    config = get_config()
    
    # 설정 로드 확인
    print(f"설정 파일: {config._config_file}")
    
    # extraction 설정 확인
    if hasattr(config, 'extraction'):
        print(f"CSS 선택자 로드됨:")
        print(f"  - 제목 선택자: {len(config.extraction.content_selectors.get('title', []))}개")
        print(f"  - 본문 선택자: {len(config.extraction.content_selectors.get('content', []))}개")
        print(f"  - 날짜 선택자: {len(config.extraction.content_selectors.get('date', []))}개")
        print(f"  - 최소 본문 길이: {config.extraction.min_content_length}")
        print(f"  - 최대 본문 길이: {config.extraction.max_content_length}")
    else:
        print("extraction 설정이 없습니다.")
    
    # advanced 설정 확인
    if hasattr(config, 'advanced'):
        print(f"\n고급 설정:")
        print(f"  - 세션 풀 크기: {config.advanced.session_management.get('max_sessions_pool', 3)}")
        print(f"  - 점진적 백오프: {config.advanced.anti_403.get('enable_progressive_backoff', False)}")
        print(f"  - 프록시 로테이션: {config.advanced.anti_403.get('enable_proxy_rotation', False)}")
    
    return True


def test_session_pool():
    """세션 풀 테스트"""
    print("\n=== 세션 풀 테스트 ===")
    
    try:
        pool = get_session_pool()
        
        # 세션 풀 상태 확인
        status = pool.get_status()
        print(f"세션 풀 크기: {status['pool_size']}")
        print(f"사용 가능한 세션: {status['available_sessions']}")
        print(f"차단된 세션: {status['blocked_sessions']}")
        
        # 세션 가져오기 테스트
        print("\n세션 가져오기 테스트:")
        for i in range(5):
            session = pool.get_session()
            print(f"  - 세션 {i+1} 획득: {session is not None}")
        
        # 세션 상태 다시 확인
        status = pool.get_status()
        print(f"\n세션 사용 후 상태:")
        for session_info in status['sessions']:
            print(f"  - 세션 {session_info['id']}: 요청 {session_info['request_count']}회, 에러 {session_info['error_count']}회")
        
        return True
        
    except Exception as e:
        logger.error(f"세션 풀 테스트 실패: {e}")
        return False


def test_content_extraction_with_config():
    """설정 파일 기반 콘텐츠 추출 테스트"""
    print("\n=== 설정 기반 콘텐츠 추출 테스트 ===")
    
    extractor = NaverNewsContentExtractor()
    
    # 테스트 URL (실제 뉴스 URL로 변경 필요)
    test_url = "https://n.news.naver.com/article/001/0014874563"
    
    print(f"테스트 URL: {test_url}")
    print("CSS 선택자 설정에서 로드 중...")
    
    try:
        article = extractor.extract_news_content(test_url)
        
        if article.title:
            print(f"\n추출 성공:")
            print(f"  - 제목: {article.title[:50]}...")
            print(f"  - 언론사: {article.press}")
            print(f"  - 날짜: {article.date}")
            print(f"  - 본문 길이: {len(article.content) if article.content else 0}자")
            print(f"  - 기자: {article.reporter}")
            
            # 본문 길이 검증
            if article.content:
                config = get_config()
                if len(article.content) < config.extraction.min_content_length:
                    print(f"  ⚠️ 본문이 최소 길이({config.extraction.min_content_length})보다 짧습니다.")
                elif len(article.content) == config.extraction.max_content_length:
                    print(f"  ⚠️ 본문이 최대 길이({config.extraction.max_content_length})로 잘렸을 수 있습니다.")
            
            return True
        else:
            print("추출 실패: 제목을 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        logger.error(f"콘텐츠 추출 테스트 실패: {e}")
        return False


def test_daily_collector_merge():
    """daily_collector의 _merge_daily_contents 테스트"""
    print("\n=== Daily Collector 병합 기능 테스트 ===")
    
    collector = NaverNewsDailyCollector()
    
    # 테스트용 통계 데이터 생성
    test_stats = {
        'query': 'AI',
        'start_date': '2024-03-01',
        'end_date': '2024-03-03',
        'daily_results': []
    }
    
    # 임시 테스트 데이터 생성
    temp_dir = collector.temp_dir
    os.makedirs(temp_dir, exist_ok=True)
    
    # 3일간의 가짜 데이터 생성
    for i in range(3):
        date = datetime(2024, 3, i+1)
        content_file = os.path.join(temp_dir, f"test_contents_{date.strftime('%Y%m%d')}.json")
        
        # 가짜 기사 데이터
        articles = []
        for j in range(5):
            articles.append({
                'title': f'테스트 기사 {date.strftime("%m/%d")} - {j+1}',
                'url': f'https://test.com/article/{i}_{j}',
                'content': f'본문 내용 {i}_{j}',
                'date': date.isoformat()
            })
        
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False)
        
        test_stats['daily_results'].append({
            'date': date.strftime('%Y-%m-%d'),
            'status': 'success',
            'content_file': content_file
        })
    
    print("테스트 데이터 생성 완료")
    
    # 병합 테스트
    print("\n1. 순차적 모드 (sequential) 테스트:")
    collector._merge_daily_contents(test_stats, content_limit=10, extraction_mode='sequential')
    
    print("\n2. 균등 분배 모드 (even_distribution) 테스트:")
    collector._merge_daily_contents(test_stats, content_limit=10, extraction_mode='even_distribution')
    
    print("\n3. 최신순 모드 (recent_first) 테스트:")
    collector._merge_daily_contents(test_stats, content_limit=10, extraction_mode='recent_first')
    
    # 임시 파일 정리
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    return True


def main():
    """메인 테스트 함수"""
    print("네이버 뉴스 크롤러 개선사항 테스트")
    print("=" * 50)
    
    # 설정 파일 확인
    if not os.path.exists('unified_config.json'):
        print("⚠️ unified_config.json 파일이 없습니다. 기본 설정을 사용합니다.")
    
    tests = [
        ("통합 설정", test_unified_config),
        ("세션 풀", test_session_pool),
        ("설정 기반 콘텐츠 추출", test_content_extraction_with_config),
        ("Daily Collector 병합", test_daily_collector_merge)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            result = test_func()
            results.append((test_name, result))
            print(f"\n✅ {test_name} 테스트: {'성공' if result else '실패'}")
        except Exception as e:
            logger.error(f"{test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
            print(f"\n❌ {test_name} 테스트: 실패 (예외 발생)")
    
    # 최종 결과
    print(f"\n{'='*50}")
    print("테스트 결과 요약:")
    for test_name, result in results:
        print(f"  - {test_name}: {'✅ 성공' if result else '❌ 실패'}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\n총 {len(results)}개 중 {success_count}개 성공")


if __name__ == "__main__":
    main()
