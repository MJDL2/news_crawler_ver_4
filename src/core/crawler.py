"""
네이버 뉴스 크롤러 엔진

전체 크롤링 프로세스를 관리하는 핵심 모듈입니다.
"""

import logging
import time
import random
from typing import List, Optional, Dict, Any
from datetime import datetime
from tqdm import tqdm

from .extractors import NaverNewsURLExtractor
from .content_extractor import NaverNewsContentExtractor
from ..models.news import CrawlResult, NewsURL, NewsArticle
from ..models.search_options import NaverNewsSearchOption
from ..utils.config import get_config

logger = logging.getLogger(__name__)

class NewsCrawler:
    """뉴스 크롤러 엔진"""
    
    def __init__(self):
        self.config = get_config()
        self.url_extractor = NaverNewsURLExtractor()
        self.content_extractor = NaverNewsContentExtractor()
    
    def crawl(self, 
             query: str,
             period: str = "1m",
             start_date: Optional[str] = None,
             end_date: Optional[str] = None,
             sort: str = "relevance",
             news_type: str = "all",
             max_pages: int = 0,
             max_urls: int = 0,
             url_type_filter: Optional[str] = None,
             extract_content: bool = False,
             content_limit: int = 0,
             extraction_mode: str = "sequential",
             request_delay: float = 1.0,
             content_delay: float = 1.5) -> CrawlResult:
        """
        뉴스 크롤링 실행
        
        Args:
            query: 검색어
            period: 검색 기간
            start_date: 시작일 (period=custom일 때)
            end_date: 종료일 (period=custom일 때)
            sort: 정렬 방식
            news_type: 뉴스 유형
            max_pages: 최대 페이지 수
            max_urls: 최대 URL 수
            url_type_filter: URL 유형 필터
            extract_content: 본문 추출 여부
            content_limit: 본문 추출 제한
            extraction_mode: 추출 모드
            request_delay: URL 요청 지연
            content_delay: 본문 추출 지연
            
        Returns:
            CrawlResult: 크롤링 결과
        """
        # 결과 객체 생성
        result = CrawlResult(query=query, period=period)
        
        try:
            # 검색 옵션 설정
            search_option = self._build_search_option(
                query, period, start_date, end_date, sort, news_type
            )
            search_url = search_option.build_url()
            logger.info(f"검색 URL: {search_url}")
            print(f"\n검색 URL 생성 완료")
            
            # URL 수집
            logger.info("URL 수집 시작...")
            print(f"\nURL 수집 중...")
            start_time = time.time()
            collected_urls = self.url_extractor.collect_from_search(
                search_url,
                max_pages=max_pages,
                delay_sec=request_delay,
                max_urls=max_urls,
                url_type_filter=url_type_filter,
                search_date=start_date
            )
            
            for url in collected_urls:
                result.add_url(url)
            
            elapsed = time.time() - start_time
            logger.info(f"URL {len(collected_urls)}개 수집 완료")
            print(f"[완료] URL {len(collected_urls)}개 수집 완료 (소요시간: {elapsed:.1f}초)")
            
            # 본문 추출
            if extract_content and collected_urls:
                logger.info("본문 추출 시작...")
                print(f"\n본문 추출 시작 (총 {len(collected_urls)}개 중 {content_limit if content_limit > 0 else '전체'} 추출)")
                
                extracted_articles = self._extract_contents(
                    collected_urls,
                    content_limit,
                    extraction_mode,
                    content_delay
                )
                
                for article in extracted_articles:
                    result.add_article(article)
                
                logger.info(f"본문 {len(extracted_articles)}개 추출 완료")
                print(f"\n[완료] 본문 {len(extracted_articles)}개 추출 완료")
            
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
            result.add_error("crawl_error", str(e))
        
        finally:
            result.complete()
        
        return result
    
    def _build_search_option(self, query: str, period: str,
                           start_date: Optional[str],
                           end_date: Optional[str],
                           sort: str, news_type: str) -> NaverNewsSearchOption:
        """검색 옵션 객체 생성"""
        option = NaverNewsSearchOption(query)
        
        # 정렬 방식 매핑
        sort_map = {
            'relevance': NaverNewsSearchOption.SORT_BY_RELEVANCE,
            'recent': NaverNewsSearchOption.SORT_BY_RECENT,
            'oldest': NaverNewsSearchOption.SORT_BY_OLDEST
        }
        option.set_sort(sort_map.get(sort, NaverNewsSearchOption.SORT_BY_RELEVANCE))
        
        # 기간 설정 매핑
        period_map = {
            'all': NaverNewsSearchOption.PERIOD_ALL,
            '1h': NaverNewsSearchOption.PERIOD_1HOUR,
            '1d': NaverNewsSearchOption.PERIOD_1DAY,
            '1w': NaverNewsSearchOption.PERIOD_1WEEK,
            '1m': NaverNewsSearchOption.PERIOD_1MONTH,
            '3m': NaverNewsSearchOption.PERIOD_3MONTHS,
            '6m': NaverNewsSearchOption.PERIOD_6MONTHS,
            '1y': NaverNewsSearchOption.PERIOD_1YEAR,
            'custom': NaverNewsSearchOption.PERIOD_CUSTOM
        }
        period_code = period_map.get(period, NaverNewsSearchOption.PERIOD_1MONTH)
        
        if period_code == NaverNewsSearchOption.PERIOD_CUSTOM:
            option.set_period(period_code, start_date, end_date)
        else:
            option.set_period(period_code)
        
        # 뉴스 유형 매핑
        type_map = {
            'all': NaverNewsSearchOption.TYPE_ALL,
            'photo': NaverNewsSearchOption.TYPE_PHOTO,
            'video': NaverNewsSearchOption.TYPE_VIDEO,
            'print': NaverNewsSearchOption.TYPE_PRINT,
            'press_release': NaverNewsSearchOption.TYPE_PRESS_RELEASE,
            'auto': NaverNewsSearchOption.TYPE_AUTO_GENERATED
        }
        option.set_news_type(type_map.get(news_type, NaverNewsSearchOption.TYPE_ALL))
        
        return option
    
    def _extract_contents(self, urls: List[NewsURL],
                         content_limit: int,
                         extraction_mode: str,
                         delay_sec: float) -> List[NewsArticle]:
        """본문 추출 처리"""
        articles = []
        
        # 추출할 URL 선택
        if extraction_mode == "balanced" and content_limit > 0:
            urls_to_extract = self._select_balanced_urls(urls, content_limit)
        else:
            urls_to_extract = urls[:content_limit] if content_limit > 0 else urls
        
        # 본문 추출
        for i, url_obj in enumerate(urls_to_extract):
            if i > 0:
                time.sleep(delay_sec + random.uniform(0, 0.5))
            
            logger.info(f"본문 추출 중 ({i+1}/{len(urls_to_extract)}): {url_obj.url}")
            print(f"  본문 추출 중 ({i+1}/{len(urls_to_extract)})...", end='\r', flush=True)
            article = self.content_extractor.extract_news_content(url_obj.url)
            
            if article.is_valid():
                articles.append(article)
            else:
                logger.warning(f"유효하지 않은 콘텐츠: {url_obj.url}")
        
        return articles
    
    def _select_balanced_urls(self, urls: List[NewsURL], limit: int) -> List[NewsURL]:
        """균등 분포로 URL 선택"""
        if len(urls) <= limit:
            return urls
        
        # 균등 간격으로 선택
        step = len(urls) / limit
        selected = []
        
        for i in range(limit):
            index = int(i * step)
            selected.append(urls[index])
        
        return selected
