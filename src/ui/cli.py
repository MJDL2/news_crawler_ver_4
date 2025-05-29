"""
명령줄 인터페이스 모듈

네이버 뉴스 크롤러의 CLI 인터페이스를 제공합니다.
"""

import argparse
import logging
from typing import Optional

from ..core.crawler import NewsCrawler
from ..utils.config import get_config
from ..utils.file_saver import FileSaver
from .interactive import InteractiveInterface

logger = logging.getLogger(__name__)

class CLI:
    """명령줄 인터페이스"""
    
    def __init__(self):
        self.crawler = NewsCrawler()
        self.file_saver = FileSaver()
        self.config = get_config()
    
    def parse_arguments(self) -> argparse.Namespace:
        """명령행 인자 파싱"""
        parser = argparse.ArgumentParser(
            description='네이버 뉴스 크롤러',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 대화형 모드 옵션
        parser.add_argument('-i', '--interactive', action='store_true',
                          help='대화형 모드로 실행')
        
        # 필수 인자 (대화형 모드에서는 선택적)
        parser.add_argument('query', nargs='?', help='검색할 키워드')
        
        # 검색 옵션
        parser.add_argument('--period', default='1m',
                          choices=['all', '1h', '1d', '1w', '1m', '3m', '6m', '1y', 'custom'],
                          help='검색 기간 (기본값: 1m)')
        parser.add_argument('--start-date', help='시작일 (YYYYMMDD 형식, --period=custom 필요)')
        parser.add_argument('--end-date', help='종료일 (YYYYMMDD 형식, --period=custom 필요)')
        parser.add_argument('--sort', default='relevance',
                          choices=['relevance', 'recent', 'oldest'],
                          help='정렬 방식 (기본값: relevance)')
        parser.add_argument('--type', default='all',
                          choices=['all', 'photo', 'video', 'print', 'press_release', 'auto'],
                          help='뉴스 유형 (기본값: all)')
        
        # 수집 옵션
        parser.add_argument('--pages', type=int, default=0,
                          help='수집할 페이지 수 (0=무제한, 기본값: 0)')
        parser.add_argument('--max-urls', type=int, default=0,
                          help='수집할 최대 URL 개수 (0=제한 없음, 기본값: 0)')
        parser.add_argument('--url-type', choices=['all', 'naver', 'original'], default='all',
                          help='수집할 URL 유형 (기본값: all)')
        
        # 본문 추출 옵션
        parser.add_argument('--extract-content', action='store_true',
                          help='뉴스 본문 추출 여부')
        parser.add_argument('--content-limit', type=int, default=0,
                          help='추출할 뉴스 본문 수 제한 (0=전체, 기본값: 0)')
        parser.add_argument('--extraction-mode', default='balanced',
                          choices=['sequential', 'balanced'],
                          help='본문 추출 방식 (기본값: balanced)')
        
        # 지연 시간 옵션
        parser.add_argument('--delay', type=float, default=1.0,
                          help='URL 요청 간 지연 시간(초) (기본값: 1.0)')
        parser.add_argument('--content-delay', type=float, default=1.5,
                          help='본문 추출 시 요청 간 지연 시간(초) (기본값: 1.5)')
        
        # 출력 옵션
        parser.add_argument('--output', default='data/news_data',
                          help='뉴스 데이터 저장 디렉토리')
        parser.add_argument('--url-output', default='data/url_data',
                          help='URL 데이터 저장 디렉토리')
        
        # 기타 옵션
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='상세 로그 출력')
        
        return parser.parse_args()
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """인자 유효성 검증"""
        # 대화형 모드가 아니고 query가 없으면 에러
        if not args.interactive and not args.query:
            logger.error("검색어를 입력해주세요. 대화형 모드는 -i 또는 --interactive 옵션을 사용하세요.")
            return False
            
        if args.period == 'custom':
            if not args.start_date or not args.end_date:
                logger.error("--period=custom 사용 시 --start-date와 --end-date를 지정해야 합니다.")
                return False
        
        return True
    
    def run(self, args: argparse.Namespace) -> int:
        """CLI 실행"""
        # 인자 검증
        if not self.validate_args(args):
            return 1
        
        # 대화형 모드에서 반환된 옵션 저장
        interactive_options = None
        
        # 대화형 모드 처리
        if args.interactive:
            # 대화형 모드에서는 모든 로깅 완전 비활성화
            logging.disable(logging.CRITICAL)
            for logger_name in logging.root.manager.loggerDict:
                logging.getLogger(logger_name).handlers = []
            
            interactive = InteractiveInterface()
            options = interactive.run()
            
            if options is None:
                print("\n작업이 취소되었습니다.")
                return 0  # 사용자가 취소함
            
            # 대화형 옵션 저장
            interactive_options = options
            
            # 대화형 모드에서 받은 옵션으로 args 업데이트
            args.query = options['query']
            args.period = options['period']
            args.start_date = options.get('start_date')
            args.end_date = options.get('end_date')
            args.sort = options['sort']
            args.type = options['news_type']
            args.pages = options['max_pages']
            args.max_urls = options['max_urls']
            args.url_type = options['url_type']
            args.extract_content = options['extract_content']
            args.content_limit = options['content_limit']
            args.extraction_mode = options['extraction_mode']
            args.output = options['output']
            args.url_output = options['url_output']
            
            # 지연 시간은 기본값 사용 (대화형 모드에서는 설정하지 않음)
            if not hasattr(args, 'delay') or args.delay is None:
                args.delay = 1.0
            if not hasattr(args, 'content_delay') or args.content_delay is None:
                args.content_delay = 1.5
            
            # 로깅 재활성화 (크롤링용)
            logging.disable(logging.NOTSET)
            # 대화형 모드에서는 INFO 레벨로 설정하여 진행 상황 표시
            logging.getLogger().setLevel(logging.INFO)
        
        # 로깅 설정 (대화형 모드가 아닌 경우)
        if args.verbose and not args.interactive:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 환경 초기화
        self.config.storage.news_data_dir = args.output
        self.config.storage.url_data_dir = args.url_output
        self.config.initialize_environment()
        
        print(f"\n크롤링을 시작합니다...")
        logger.info(f"네이버 뉴스 크롤링 시작: '{args.query}'")
        
        try:
            # 날짜별 수집 여부 확인 (대화형 모드에서 설정된 경우)
            if args.interactive and interactive_options and interactive_options.get('_daily_collect'):
                # 날짜별 수집 모드
                from ..core.daily_collector import NaverNewsDailyCollector
                from datetime import datetime, timedelta
                
                print("\n날짜별 분할 수집 모드로 진행합니다.")
                daily_collector = NaverNewsDailyCollector()
                
                # 기간 계산
                if args.period == 'custom' and args.start_date and args.end_date:
                    start_date = datetime.strptime(args.start_date, '%Y%m%d')
                    end_date = datetime.strptime(args.end_date, '%Y%m%d')
                else:
                    # 기본 기간 설정
                    end_date = datetime.now()
                    period_days = {'1w': 7, '1m': 30, '3m': 90, '6m': 180, '1y': 365}
                    days = period_days.get(args.period, 30)
                    start_date = end_date - timedelta(days=days)
                
                # 날짜별 수집 실행
                result = daily_collector.collect_date_range(
                    query=args.query,
                    start_date=start_date,
                    end_date=end_date,
                    sort=args.sort,
                    news_type=args.type,
                    extract_content=args.extract_content,
                    daily_limit=interactive_options.get('_daily_limit', 10),
                    extraction_mode=args.extraction_mode,
                    save_intermediate=True
                )
                
                # 결과 출력
                print("\n===== 날짜별 수집 완료 =====")
                print(f"검색어: {result['query']}")
                print(f"기간: {result['start_date']} ~ {result['end_date']}")
                print(f"총 수집일: {result['total_days']}일")
                print(f"수집된 URL: {result['total_urls']}개")
                print(f"추출된 기사: {result['total_contents']}개")
                
                if result['daily_results']:
                    print("\n일별 수집 현황:")
                    for daily in result['daily_results'][-5:]:  # 최근 5일만 표시
                        print(f"  {daily['date']}: URL {daily['urls_collected']}개, 본문 {daily['contents_extracted']}개")
                
                return 0
                
            else:
                # 기존 크롤링 방식
                result = self.crawler.crawl(
                    query=args.query,
                    period=args.period,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    sort=args.sort,
                    news_type=args.type,
                    max_pages=args.pages,
                    max_urls=args.max_urls,
                    url_type_filter=args.url_type,
                    extract_content=args.extract_content,
                    content_limit=args.content_limit,
                    extraction_mode=args.extraction_mode,
                    request_delay=args.delay,
                    content_delay=args.content_delay
                )
                
                # 결과 저장
                saved_files = self.file_saver.save_crawl_result(result, args.output)
                
                # 결과 출력
                stats = result.get_stats()
                print("\n===== 크롤링 완료 =====")
                print(f"검색어: {stats['query']}")
                print(f"기간: {stats['period']}")
                print(f"수집된 URL: {stats['urls_collected']}개")
                print(f"추출된 기사: {stats['articles_extracted']}개")
                print(f"소요 시간: {stats['duration_seconds']:.2f}초")
                
                if stats['errors_count'] > 0:
                    print(f"오류 발생: {stats['errors_count']}건")
                
                if saved_files['urls']:
                    print(f"\nURL 저장: {saved_files['urls']}")
                if saved_files['articles']:
                    print(f"기사 저장: {len(saved_files['articles'])}개 파일")
                if saved_files['stats']:
                    print(f"통계 저장: {saved_files['stats']}")
                
                return 0
                print(f"\nURL 저장: {saved_files['urls']}")
            if saved_files['articles']:
                print(f"기사 저장: {len(saved_files['articles'])}개 파일")
            if saved_files['stats']:
                print(f"통계 저장: {saved_files['stats']}")
            
            return 0
            
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
            return 1

def main():
    """CLI 메인 함수"""
    cli = CLI()
    args = cli.parse_arguments()
    return cli.run(args)

if __name__ == "__main__":
    exit(main())
