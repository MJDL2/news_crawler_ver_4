"""
URL 추출 모듈

네이버 뉴스 검색 결과에서 URL을 추출하는 기능을 제공합니다.
"""

import re
import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup

from ..utils.config import get_config
from ..models.news import NewsURL

logger = logging.getLogger(__name__)

class URLExtractor:
    """URL 추출 기본 클래스"""
    
    def __init__(self):
        self.config = get_config()
        self._session = None
    
    @property
    def session(self) -> requests.Session:
        """요청 세션 반환 (지연 생성)"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(self.config.get_headers())
            # 쿠키 정책 설정 제거 - Python 3.13 호환성 문제
            # self._session.cookies.set_policy(None)
            
            # 프록시 설정 (환경 변수에서 읽기)
            import os
            http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
            https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
            
            if http_proxy or https_proxy:
                proxies = {}
                if http_proxy:
                    proxies['http'] = http_proxy
                if https_proxy:
                    proxies['https'] = https_proxy
                self._session.proxies = proxies
                logger.info(f"프록시 설정됨: {proxies}")
            
            # 네이버 메인 페이지 먼저 방문하여 쿠키 획득
            try:
                logger.info("네이버 메인 페이지 방문 중...")
                main_response = self._session.get('https://www.naver.com', timeout=10)
                main_response.raise_for_status()
                
                # 검색 페이지도 방문
                search_response = self._session.get('https://search.naver.com', timeout=10)
                search_response.raise_for_status()
                
                logger.info("세션 초기화 완료")
                time.sleep(1)  # 잠시 대기
            except Exception as e:
                logger.warning(f"세션 초기화 중 경고: {e}")
                
        return self._session
    
    def get_page_content(self, url: str) -> Optional[str]:
        """URL에서 HTML 가져오기"""
        for attempt in range(self.config.network.retries):
            try:
                if attempt > 0:
                    sleep_time = self.config.network.backoff_factor ** attempt
                    time.sleep(sleep_time)
                
                response = self.session.get(
                    url, 
                    timeout=self.config.network.timeout
                )
                response.raise_for_status()
                return response.text
                
            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    logger.error(f"403 Forbidden 오류 - 네이버가 요청을 차단했습니다.")
                    logger.error(f"URL: {url}")
                    logger.error(f"응답 헤더: {e.response.headers}")
                    logger.error(f"쿠키: {self.session.cookies.get_dict()}")
                    
                    # 403 오류 시 특별 처리
                    if attempt < self.config.network.retries - 1:
                        # 점진적으로 증가하는 대기 시간
                        wait_time = min(30 + (attempt * 20), 120)  # 최대 2분
                        logger.info(f"{wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        
                        # 세션 재생성 시도
                        if attempt >= 1:
                            logger.info("세션을 재생성합니다...")
                            self._session = None  # 기존 세션 제거
                            _ = self.session  # 새 세션 생성
                            time.sleep(5)  # 추가 대기
                    else:
                        # 최종 시도에서도 실패하면 None 반환
                        return None
                else:
                    logger.warning(f"HTTP 오류 {e.response.status_code}: {e} (시도 {attempt + 1}/{self.config.network.retries})")
                    
            except requests.RequestException as e:
                logger.warning(f"요청 오류 {e} (시도 {attempt + 1}/{self.config.network.retries})")
                
        logger.error(f"재시도 실패: {url}")
        return None

    def is_similar_title(self, title1: str, title2: str, 
                        threshold: Optional[float] = None) -> bool:
        """두 제목의 유사도 검사"""
        if threshold is None:
            threshold = self.config.crawling.similarity_threshold
            
        if not title1 or not title2:
            return False
            
        # 짧은 제목들은 정확히 일치해야 함
        if len(title1) <= 6 or len(title2) <= 6:
            return title1 == title2
            
        similarity = SequenceMatcher(None, title1, title2).ratio()
        return similarity >= threshold


class NaverNewsURLExtractor(URLExtractor):
    """네이버 뉴스 URL 추출기"""
    
    NAVER_PATTERN = re.compile(r"https?://n\.news\.naver\.com/.+/article/")
    
    def extract_news_urls(self, html: str) -> List[NewsURL]:
        """검색 결과 HTML에서 기사 URL 목록 추출"""
        soup = BeautifulSoup(html, "html.parser")
        results: List[NewsURL] = []
        seen_urls = set()
        seen_titles = set()

        # 네이버 뉴스 URL을 모두 찾기
        naver_links = soup.find_all("a", href=self.NAVER_PATTERN)
        logger.debug(f"네이버 뉴스 링크 {len(naver_links)}개 발견")
        
        for link in naver_links:
            href = link.get("href", "")
            if href in seen_urls:
                continue
                
            # 제목 찾기 - 부모 요소들을 탐색
            title = None
            current = link
            
            # 5단계 위까지 탐색하여 제목 찾기
            for _ in range(5):
                parent = current.parent
                if parent and parent.name in ['div', 'li', 'article']:
                    # 해당 컨테이너 내의 모든 텍스트 추출
                    texts = []
                    for elem in parent.find_all(string=True, recursive=True):
                        text = elem.strip()
                        if text and len(text) > 20 and not text.startswith('http') and '네이버뉴스' not in text:
                            texts.append(text)
                    
                    # 첫 번째 긴 텍스트를 제목으로 사용
                    if texts:
                        title = texts[0]
                        break
                current = parent
            
            # URL과 제목을 수집
            if title and title not in seen_titles:
                results.append(NewsURL(url=href, type="naver", title=title))
                seen_urls.add(href)
                seen_titles.add(title)
                logger.debug(f"URL 추가 (제목 있음): {title[:30]}...")
            elif not title:  # 제목을 찾지 못한 경우도 URL은 저장
                results.append(NewsURL(url=href, type="naver"))
                seen_urls.add(href)
                logger.debug(f"URL 추가 (제목 없음): {href}")
        
        logger.info(f"extract_news_urls: {len(results)}개 URL 추출")
        
        # 기존 구조도 함께 처리 (호환성) - 결과가 없을 때만
        if not results:
            logger.debug("새 구조에서 URL을 찾지 못함, 기존 구조 시도")
            # 원본 기사 URL 추출 (기존 방식)
            selectors = [
                "div.news_area a.news_tit[href]",
                "div.news_wrap a.news_tit[href]",
                "a.news_tit[href]"  # 더 간단한 셀렉터 추가
            ]
            
            for selector in selectors:
                for a in soup.select(selector):
                    href = a.get("href", "")
                    title = a.text.strip()
                    if href not in seen_urls:
                        results.append(NewsURL(
                            url=href, 
                            type="original" if not self.NAVER_PATTERN.search(href) else "naver",
                            title=title if title else None
                        ))
                        seen_urls.add(href)
        
        return results
    
    def collect_from_search(self, search_url: str, 
                           max_pages: int = 0,
                           delay_sec: float = 1.0,
                           max_urls: int = 0,
                           url_type_filter: Optional[str] = None,
                           search_date: Optional[str] = None) -> List[NewsURL]:
        """네이버 검색 결과에서 URL 수집"""
        collected_urls: List[NewsURL] = []
        page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        while True:
            # 페이지 URL 생성
            current_url = f"{search_url}&start={(page - 1) * 10 + 1}"
            logger.info(f"페이지 {page} 스캔 중: {current_url}")
            print(f"  페이지 {page} 스캔 중...", end='\r')
            
            # HTML 가져오기
            html_content = self.get_page_content(current_url)
            if not html_content:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_consecutive_empty:
                    break
                page += 1
                if max_pages > 0 and page > max_pages:
                    break
                time.sleep(delay_sec + random.uniform(0, 0.5))
                continue
            
            # URL 추출
            extracted_urls = self.extract_news_urls(html_content)
            logger.debug(f"페이지 {page}에서 추출된 URL: {len(extracted_urls)}개")
            
            # 유형 필터링
            if url_type_filter and url_type_filter != 'all':
                before_filter = len(extracted_urls)
                extracted_urls = [url for url in extracted_urls 
                                if url.type == url_type_filter]
                logger.debug(f"유형 필터링 ({url_type_filter}): {before_filter}개 → {len(extracted_urls)}개")
            
            # 새 URL 추가
            new_urls_count = 0
            for url in extracted_urls:
                if search_date:
                    url.search_date = search_date
                    
                # 중복 체크
                is_duplicate = any(u.url == url.url for u in collected_urls)
                if not is_duplicate:
                    collected_urls.append(url)
                    new_urls_count += 1
                    logger.debug(f"새 URL 추가: {url.title[:30] if url.title else url.url[:50]}...")
                else:
                    logger.debug(f"중복 URL 스킵: {url.url[:50]}...")
                    
                    if max_urls > 0 and len(collected_urls) >= max_urls:
                        logger.info(f"URL 수집 제한({max_urls}개) 도달")
                        return collected_urls
            
            # 종료 조건 확인
            if new_urls_count > 0:
                logger.info(f"페이지 {page}: {new_urls_count}개 신규 URL (총 {len(collected_urls)}개)")
                consecutive_empty_pages = 0
            else:
                consecutive_empty_pages += 1
            
            if consecutive_empty_pages >= max_consecutive_empty:
                logger.info(f"연속 {max_consecutive_empty}페이지 빈 결과")
                break
            
            if max_pages > 0 and page >= max_pages:
                break
            
            page += 1
            time.sleep(delay_sec + random.uniform(0, 1))
        
        return collected_urls