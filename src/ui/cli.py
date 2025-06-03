"""
명령줄 인터페이스 모듈

네이버 뉴스 크롤러의 CLI 인터페이스를 제공합니다.
"""

import argparse
import logging
import sys
from typing import Optional
from datetime import datetime

from ..core.crawler import NewsCrawler
from ..core.daily_collector import NaverNewsDailyCollector
from ..utils.config import get_config
from ..utils.file_saver import FileSaver

logger = logging.getLogger(__name__)

class CLI:
    """명령줄 인터페이스"""
    
    def __init__(self):
        # --help 옵션이 있으면 초기화를 최소화
        if '--help' in sys.argv or '-h' in sys.argv:
            self.crawler = None
            self.daily_collector = None
            self.file_saver = None
            self.config = None
        else:
            self.crawler = NewsCrawler()
            self.daily_collector = NaverNewsDailyCollector()
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
        
        # 날짜별 수집 옵션
        parser.add_argument('--daily', action='store_true',
                          help='날짜별 수집 모드 사용')
        parser.add_argument('--daily-limit', type=int, default=10,
                          help='일별 수집 개수 제한 (기본값: 10)')
        parser.add_argument('--extraction-mode', default='sequential',
                          choices=['sequential', 'even_distribution', 'recent_first'],
                          help='본문 추출 방식 (기본값: sequential)')
        
        # 본문 추출 옵션
        parser.add_argument('--extract-content', action='store_true',
                          help='뉴스 본문 추출 여부')
        parser.add_argument('--content-limit', type=int, default=0,
                          help='추출할 뉴스 본문 수 제한 (0=전체, 기본값: 0)')
        
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
        
        # 대화형 모드 처리
        if args.interactive:
            # 대화형 모드에서는 모든 로깅 완전 비활성화
            logging.disable(logging.CRITICAL)
            for logger_name in logging.root.manager.loggerDict:
                logging.getLogger(logger_name).handlers = []
            
            try:
                from .interactive import InteractiveInterface
                interactive = InteractiveInterface()
                options = interactive.run()
                
                if options is None:
                    print("\n작업이 취소되었습니다.")
                    return 0  # 사용자가 취소함
                
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
                
                # 지연 시간은 기본값 사용
                if not hasattr(args, 'delay') or args.delay is None:
                    args.delay = 1.0
                if not hasattr(args, 'content_delay') or args.content_delay is None:
                    args.content_delay = 1.5
                
                # 로깅 재활성화 (크롤링용)
                logging.disable(logging.NOTSET)
                logging.getLogger().setLevel(logging.INFO)
                
            except ImportError:
                print("대화형 인터페이스를 불러올 수 없습니다.")
                return 1
        
        # 로깅 설정
        if args.verbose and not args.interactive:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 환경 초기화
        self.config.storage.news_data_dir = args.output
        self.config.storage.url_data_dir = args.url_output
        self.config.initialize_environment()
        
        print(f"\n크롤링을 시작합니다...")
        logger.info(f"네이버 뉴스 크롤링 시작: '{args.query}'")
        
        try:
            # 날짜별 수집이 필요한지 확인
            use_daily_collector = self._should_use_daily_collector(args)
            
            if use_daily_collector:
                # NaverNewsDailyCollector 사용 (날짜별 수집)
                result = self._run_daily_collection(args)
            else:
                # 기존 NewsCrawler 사용 (전체 기간 한번에)
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
            
            # 결과 저장 및 출력
            if hasattr(result, 'stats'):
                # 날짜별 수집 결과 처리
                self._handle_daily_collection_result(result)
            else:
                # 기존 크롤링 결과 처리
                saved_files = self.file_saver.save_crawl_result(result, args.output)
                self._print_crawl_result(result, saved_files)
            
            return 0
            
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
            return 1

    def _should_use_daily_collector(self, args: argparse.Namespace) -> bool:
        """날짜별 수집이 필요한지 판단"""
        # custom 기간이 아니면 일반 크롤러 사용
        if args.period != 'custom':
            return False
        
        # 시작일과 종료일이 없으면 일반 크롤러 사용
        if not args.start_date or not args.end_date:
            return False
        
        # 본문 추출을 하지 않으면 일반 크롤러 사용
        if not args.extract_content:
            return False
        
        try:
            # 날짜 파싱
            start_dt = datetime.strptime(args.start_date, '%Y%m%d')
            end_dt = datetime.strptime(args.end_date, '%Y%m%d')
            
            # 하루 이상의 기간이면 날짜별 수집 사용
            date_diff = (end_dt - start_dt).days
            return date_diff >= 1
            
        except ValueError:
            logger.warning("날짜 형식 오류, 일반 크롤러를 사용합니다.")
            return False
    
    def _run_daily_collection(self, args: argparse.Namespace):
        """날짜별 수집 실행"""
        from ..models.news import CrawlResult
        
        # 날짜 변환
        start_dt = datetime.strptime(args.start_date, '%Y%m%d')
        end_dt = datetime.strptime(args.end_date, '%Y%m%d')
        
        # 일별 제한 개수 계산
        daily_limit = args.content_limit if args.content_limit > 0 else 10
        
        print(f"날짜별 수집 모드 실행")
        print(f"  기간: {args.start_date} ~ {args.end_date}")
        print(f"  일별 제한: {daily_limit}개")
        
        # NaverNewsDailyCollector로 수집
        stats = self.daily_collector.collect_date_range(
            query=args.query,
            start_date=start_dt,
            end_date=end_dt,
            sort=args.sort,
            news_type=args.type,
            extract_content=args.extract_content,
            content_limit=args.content_limit,  # 전체 제한 개수 전달
            extraction_mode=args.extraction_mode,
            daily_limit=daily_limit,
            save_intermediate=True
        )
        
        # CrawlResult 형태로 변환하여 반환 (기존 코드와 호환성 유지)
        result = CrawlResult(query=args.query, period=args.period)
        result.stats = stats
        
        # 수집된 기사 개수 집계
        total_articles = sum(day.get('contents_extracted', 0) for day in stats.get('daily_results', []))
        
        # 결과 설정
        result.total_articles = total_articles
        result.total_urls = stats.get('total_urls', 0)
        
        return result
    
    def _handle_daily_collection_result(self, result):
        """날짜별 수집 결과 처리"""
        stats = result.stats
        
        print("\n===== 날짜별 수집 완료 =====")
        print(f"검색어: {result.query}")
        print(f"기간: {result.period}")
        print(f"수집 기간: {stats['start_date']} ~ {stats['end_date']} ({stats['total_days']}일)")
        print(f"총 수집 URL: {stats['total_urls']}개")
        print(f"총 추출 기사: {stats['total_contents']}개")
        
        # 일별 상세 결과
        print("\n--- 일별 수집 결과 ---")
        for daily_result in stats['daily_results']:
            if daily_result.get('status') == 'success':
                print(f"  {daily_result['date']}: URL {daily_result.get('urls_collected', 0)}개, "
                      f"기사 {daily_result.get('contents_extracted', 0)}개")
            else:
                print(f"  {daily_result['date']}: 실패 - {daily_result.get('error', 'Unknown error')}")
        
        # 저장 파일 정보
        if stats.get('merged_file'):
            print(f"\n병합 파일 저장: {stats['merged_file']}")
        
        print(f"소요 시간: {stats.get('elapsed_time', 0):.1f}초")
    
    def _print_crawl_result(self, result, saved_files):
        """기존 크롤링 결과 출력"""
        print("\n===== 크롤링 완료 =====")
        print(f"검색어: {result.query}")
        print(f"기간: {result.period}")
        print(f"수집된 URL: {len(result.urls)}개")
        print(f"추출된 기사: {len(result.articles)}개")
        
        if result.errors:
            print(f"오류 발생: {len(result.errors)}건")
        
        if saved_files['urls']:
            print(f"\nURL 저장: {saved_files['urls']}")
        if saved_files['articles']:
            print(f"기사 저장: {len(saved_files['articles'])}개 파일")
        if saved_files['stats']:
            print(f"통계 저장: {saved_files['stats']}")

def main():
    """CLI 메인 함수"""
    cli = CLI()
    args = cli.parse_arguments()
    return cli.run(args)

if __name__ == "__main__":
    exit(main())
