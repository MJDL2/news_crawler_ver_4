"""
네이버 뉴스 크롤러 대화형 인터페이스 모듈

사용자와 대화형 인터페이스로 검색 옵션을 설정하고 
뉴스 URL 및 본문 수집을 실행하는 기능을 제공합니다.
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from ..utils.config import get_config
from ..models.search_options import NaverNewsSearchOption

logger = logging.getLogger('interactive_ui')


class InteractiveInterface:
    """네이버 뉴스 크롤러 대화형 인터페이스 클래스"""
    
    def __init__(self):
        """인터페이스 초기화 및 기본 옵션 설정"""
        self.config = get_config()
        self.options = {
            'queries': [],  # 복수 검색어 지원
            'news_office': [],  # 언론사 리스트
            'output': self.config.storage.news_data_dir,
            'url_output': self.config.storage.url_data_dir,
            'period': '1m',  # 기본 검색 기간: 1개월
            'start_date': None,  # period='custom'일 때 사용
            'end_date': None,    # period='custom'일 때 사용
            'sort': 'relevance', # 기본 정렬: 관련도순
            'collect_and_extract': True,  # 수집과 추출 통합
            'daily_limit': 10,  # 일별 기사 수 제한
            'separate_by_query': True,  # 검색어별 개별 수집
            'separate_by_press': False,  # 언론사별 개별 수집
            'daily_collect': False,  # 날짜별 분할 수집
        }
        
    def print_header(self):
        """헤더 출력"""
        print("\n" + "="*60)
        print("       네이버 뉴스 크롤러 - 대화형 인터페이스       ")
        print("="*60)
        print("각 단계별로 옵션을 설정하여 뉴스를 수집합니다.")
        print("기본값을 사용하려면 Enter를 누르세요.\n")    
    def get_search_queries(self):
        """검색어 입력 받기 (복수 가능)"""
        while True:
            queries = input("검색어를 입력하세요 (쉼표로 구분): ").strip()
            
            if queries:
                self.options['queries'] = [q.strip() for q in queries.split(',')]
                print(f"  → 검색어: {', '.join(self.options['queries'])}")
                
                # 복수 검색어인 경우 개별 수집 여부 확인
                if len(self.options['queries']) > 1:
                    separate = input("    검색어별로 개별 수집하시겠습니까? (Y/n): ").strip().lower()
                    self.options['separate_by_query'] = separate != 'n'
                break
            else:
                print("  ! 검색어는 필수입니다.")
    
    def get_press_selection(self):
        """언론사 선택"""
        print("\n언론사 선택")
        print("  1. 전체 언론사")
        print("  2. 주요 언론사 (연합뉴스, 한겨레, 매일경제, 조선일보, 중앙일보)")
        print("  3. 직접 선택")
        
        choice = input("선택 [1]: ").strip() or '1'
        
        if choice == '1':
            self.options['news_office'] = []
            print("  → 전체 언론사")
        elif choice == '2':
            self.options['news_office'] = ['연합뉴스', '한겨레', '매일경제', '조선일보', '중앙일보']
            print(f"  → 주요 언론사: {', '.join(self.options['news_office'])}")
        elif choice == '3':
            press_input = input("언론사 이름 (쉼표로 구분): ").strip()
            self.options['news_office'] = [p.strip() for p in press_input.split(',')]
            print(f"  → 선택 언론사: {', '.join(self.options['news_office'])}")
            
        # 언론사별 개별 수집 여부
        if self.options['news_office']:
            separate = input("    언론사별로 개별 수집하시겠습니까? (y/N): ").strip().lower()
            self.options['separate_by_press'] = separate == 'y'
    def get_search_period(self):
        """검색 기간 설정"""
        print("\n검색 기간 설정")
        print("  1. 최근 1주 (1w)")
        print("  2. 최근 1개월 (1m) - 기본값")
        print("  3. 최근 3개월 (3m)")
        print("  4. 사용자 지정 기간 (custom)")
        
        choice = input("선택 [2]: ").strip() or '2'
        
        period_map = {
            '1': '1w', '2': '1m', '3': '3m', '4': 'custom'
        }
        
        if choice in period_map:
            self.options['period'] = period_map[choice]
            print(f"  → 검색 기간: {period_map[choice]}")
            
            if period_map[choice] == 'custom':
                self._get_custom_dates()
                
            # 1주 이상인 경우 날짜별 수집 자동 활성화
            if self.options['period'] in ['1m', '3m', 'custom']:
                daily = input("    날짜별로 분할 수집하시겠습니까? (Y/n): ").strip().lower()
                self.options['daily_collect'] = daily != 'n'
        else:
            print("  → 기본값 사용: 1개월 (1m)")
    
    def _get_custom_dates(self):
        """사용자 지정 날짜 입력"""
        print("\n날짜 형식: YYYYMMDD (예: 20240101)")
        
        # 시작 날짜
        while True:
            start = input("시작 날짜: ").strip()
            if self._validate_date(start):
                self.options['start_date'] = start
                break        
        # 종료 날짜
        while True:
            end = input("종료 날짜: ").strip()
            if self._validate_date(end):
                self.options['end_date'] = end
                break
        
        print(f"  → 기간: {self.options['start_date']} ~ {self.options['end_date']}")
    
    def _validate_date(self, date_str: str) -> bool:
        """날짜 형식 검증"""
        if len(date_str) != 8:
            print("  ! 날짜는 8자리 숫자여야 합니다.")
            return False
        
        try:
            datetime.strptime(date_str, '%Y%m%d')
            return True
        except ValueError:
            print("  ! 올바른 날짜 형식이 아닙니다.")
            return False
    
    def get_sort_option(self):
        """정렬 옵션 설정"""
        print("\n정렬 방식")
        print("  1. 관련도순 (relevance) - 기본값")
        print("  2. 최신순 (recent)")
        print("  3. 오래된순 (oldest)")
        
        choice = input("선택 [1]: ").strip() or '1'
        
        sort_map = {'1': 'relevance', '2': 'recent', '3': 'oldest'}
        
        if choice in sort_map:
            self.options['sort'] = sort_map[choice]
            print(f"  → 정렬: {sort_map[choice]}")
        else:
            print("  → 기본값 사용: 관련도순")    
    def get_collection_settings(self):
        """수집 설정"""
        print("\n수집 설정")
        
        # 일별 수집 제한
        daily_limit = input("일별 기사 수 제한 (0=무제한) [10]: ").strip()
        if daily_limit.isdigit():
            self.options['daily_limit'] = int(daily_limit)
        print(f"  → 일별 기사 수: {self.options['daily_limit']}")
        
        # 수집 모드
        print("\n수집 모드")
        print("  1. 빠른 수집 (URL만)")
        print("  2. 전체 수집 (URL + 본문) - 기본값")
        
        mode = input("선택 [2]: ").strip() or '2'
        
        if mode == '1':
            self.options['collect_and_extract'] = False
            print("  → URL만 수집")
        else:
            self.options['collect_and_extract'] = True
            print("  → URL과 본문 동시 수집")

    
    def confirm_options(self) -> bool:
        """설정 확인"""
        print("\n" + "="*60)
        print("설정 확인")
        print("="*60)
        
        print(f"  검색어: {', '.join(self.options['queries'])}")
        if self.options['news_office']:
            print(f"  언론사: {', '.join(self.options['news_office'])}")
        else:
            print(f"  언론사: 전체")
        print(f"  검색 기간: {self.options['period']}")
        if self.options['period'] == 'custom':
            print(f"  기간: {self.options['start_date']} ~ {self.options['end_date']}")
        print(f"  정렬: {self.options['sort']}")
        print(f"  일별 수집 제한: {self.options['daily_limit']}")
        print(f"  수집 모드: {'전체 (URL+본문)' if self.options['collect_and_extract'] else 'URL만'}")
        if self.options['daily_collect']:
            print(f"  날짜별 분할 수집: 활성화")
        if self.options['separate_by_query']:
            print(f"  검색어별 개별 수집: 활성화")
        if self.options['separate_by_press']:
            print(f"  언론사별 개별 수집: 활성화")
        
        print("="*60)
        
        confirm = input("\n이대로 진행하시겠습니까? (Y/n): ").strip().lower()
        return confirm != 'n'
    def run(self) -> Dict[str, Any]:
        """대화형 인터페이스 실행"""
        self.print_header()
        
        # 단계별 옵션 설정
        self.get_search_queries()  # 복수 검색어
        self.get_press_selection()  # 언론사 선택
        self.get_search_period()
        self.get_sort_option()
        self.get_collection_settings()  # 수집 설정
        
        # 설정 확인
        if self.confirm_options():
            # CLI가 기대하는 형식으로 옵션 변환
            cli_options = {
                'query': self.options['queries'][0] if self.options['queries'] else '',  # 첫 번째 검색어
                'period': self.options['period'],
                'start_date': self.options.get('start_date'),
                'end_date': self.options.get('end_date'),
                'sort': self.options['sort'],
                'news_type': 'all',  # 기본값
                'max_pages': 0,  # 무제한
                'max_urls': 0,  # 무제한
                'url_type': 'all',  # 모든 URL 타입
                'extract_content': self.options['collect_and_extract'],
                'content_limit': 0 if self.options['daily_collect'] else self.options['daily_limit'],  # 날짜별 수집 시 전체 제한 없음
                'extraction_mode': 'balanced',  # 기본 추출 모드
                'output': self.options['output'],
                'url_output': self.options['url_output'],
                # 추가 정보 (나중에 활용할 수 있도록)
                '_all_queries': self.options['queries'],
                '_news_office': self.options['news_office'],
                '_daily_collect': self.options['daily_collect'],
                '_daily_limit': self.options['daily_limit'],  # 일별 제한 추가
                '_separate_by_query': self.options['separate_by_query'],
                '_separate_by_press': self.options['separate_by_press'],
            }
            return cli_options
        else:
            print("\n작업이 취소되었습니다.")
            return None
    
    def get_options(self) -> Dict[str, Any]:
        """현재 설정된 옵션 반환"""
        return self.options.copy()