"""
네이버 뉴스 검색 옵션 모델

네이버 뉴스 검색의 다양한 옵션을 관리하고
검색 조건에 맞는 URL을 생성하는 기능을 제공합니다.
"""

import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, List

class NaverNewsSearchOption:
    """네이버 뉴스 검색 옵션 클래스"""
    
    # 기본 검색 URL
    BASE_URL = "https://search.naver.com/search.naver"
    
    # 정렬 방식
    SORT_BY_RELEVANCE = "0"  # 관련도순
    SORT_BY_RECENT = "1"     # 최신순
    SORT_BY_OLDEST = "2"     # 오래된순
    
    # 기간 설정
    PERIOD_ALL = "0"        # 전체
    PERIOD_1HOUR = "1"      # 1시간
    PERIOD_1DAY = "2"       # 1일
    PERIOD_1WEEK = "3"      # 1주
    PERIOD_1MONTH = "4"     # 1개월
    PERIOD_3MONTHS = "5"    # 3개월
    PERIOD_6MONTHS = "6"    # 6개월
    PERIOD_1YEAR = "7"      # 1년
    PERIOD_CUSTOM = "8"     # 직접입력
    
    # 유형 설정
    TYPE_ALL = "0"          # 전체
    TYPE_PHOTO = "1"        # 포토
    TYPE_VIDEO = "2"        # 동영상
    TYPE_PRINT = "3"        # 지면기사
    TYPE_PRESS_RELEASE = "4"  # 보도자료
    TYPE_AUTO_GENERATED = "5"  # 자동생성기사
    
    # 서비스 영역
    SERVICE_ALL = "0"       # 전체
    SERVICE_MOBILE_MAIN = "1"  # 모바일 메인 언론사
    SERVICE_PC_MAIN = "2"   # PC 메인 언론사
    
    def __init__(self, query: str):
        """
        네이버 뉴스 검색 옵션 객체 초기화
        
        Args:
            query: 검색할 키워드
        """
        self.query = query
        self.sort = self.SORT_BY_RELEVANCE  # 기본값: 관련도순
        self.period = self.PERIOD_ALL       # 기본값: 전체기간
        self.start_date: Optional[str] = None  # 직접입력 시작일
        self.end_date: Optional[str] = None    # 직접입력 종료일
        self.news_type = self.TYPE_ALL      # 기본값: 전체유형
        self.service_area = self.SERVICE_ALL  # 기본값: 전체 서비스 영역
        self.news_office: List[str] = []    # 선택된 언론사 목록
        self.reporter: Optional[str] = None  # 기자명
        
    def set_sort(self, sort_type: str) -> 'NaverNewsSearchOption':
        """정렬 방식 설정"""
        self.sort = sort_type
        return self
    
    def set_period(self, period_type: str, 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> 'NaverNewsSearchOption':
        """기간 설정"""
        self.period = period_type
        
        if period_type == self.PERIOD_CUSTOM:
            if not start_date or not end_date:
                raise ValueError("직접입력 기간을 선택할 경우 시작일과 종료일을 반드시 지정해야 합니다.")
            self.start_date = start_date
            self.end_date = end_date
        else:
            self.start_date = None
            self.end_date = None
            
        return self
        
    def set_news_type(self, news_type: str) -> 'NaverNewsSearchOption':
        """뉴스 유형 설정"""
        self.news_type = news_type
        return self
    
    def set_service_area(self, service_area: str) -> 'NaverNewsSearchOption':
        """서비스 영역 설정"""
        self.service_area = service_area
        return self
    
    def set_news_office(self, news_office_list: List[str]) -> 'NaverNewsSearchOption':
        """특정 언론사 설정"""
        self.news_office = news_office_list
        return self
        
    def set_reporter(self, reporter_name: str) -> 'NaverNewsSearchOption':
        """기자명 설정"""
        self.reporter = reporter_name
        return self
    
    def _get_period_param(self) -> str:
        """기간 설정 파라미터 생성"""
        period_params = {
            self.PERIOD_ALL: "p:all",
            self.PERIOD_1HOUR: "p:1h",
            self.PERIOD_1DAY: "p:1d",
            self.PERIOD_1WEEK: "p:1w",
            self.PERIOD_1MONTH: "p:1m",
            self.PERIOD_3MONTHS: "p:3m",
            self.PERIOD_6MONTHS: "p:6m",
            self.PERIOD_1YEAR: "p:1y"
        }
        
        if self.period == self.PERIOD_CUSTOM:
            return f"p:from{self.start_date}to{self.end_date}"
        
        return period_params.get(self.period, "p:all")
    
    def build_url(self) -> str:
        """설정된 옵션으로 네이버 뉴스 검색 URL 생성"""
        # 날짜 형식 변환 (YYYYMMDD → YYYY.MM.DD)
        ds_formatted = ""
        de_formatted = ""
        if self.start_date:
            ds_formatted = f"{self.start_date[:4]}.{self.start_date[4:6]}.{self.start_date[6:8]}"
        if self.end_date:
            de_formatted = f"{self.end_date[:4]}.{self.end_date[4:6]}.{self.end_date[6:8]}"
            
        params = {
            "ssc": "tab.news.all",
            "query": self.query,
            "sm": "tab_opt",
            "sort": self.sort,
            "photo": "0" if self.news_type == self.TYPE_ALL else "1" if self.news_type == self.TYPE_PHOTO else "0",
            "field": "0",
            "pd": "3" if self.period == self.PERIOD_CUSTOM else self.period,  # 직접입력은 pd=3
            "ds": ds_formatted,
            "de": de_formatted,
            "docid": "",
            "related": "0",
            "mynews": "0",
            "office_type": "0",
            "office_section_code": "0",
            "news_office_checked": ",".join(self.news_office) if self.news_office else "",
            "nso": f"so:r,p:{self._get_period_param()},a:all",  # 정상적인 형식으로 변경
            "is_sug_officeid": "0",
            "office_category": "",
            "service_area": "",
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}?{query_string}"

    @staticmethod
    def get_date_str(days_ago: int = 0, format: str = "%Y%m%d") -> str:
        """특정 날짜의 문자열 반환"""
        target_date = datetime.now() - timedelta(days=days_ago)
        return target_date.strftime(format)
