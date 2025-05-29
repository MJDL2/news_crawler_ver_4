"""
뉴스 콘텐츠 추출 모듈

네이버 뉴스 URL에서 본문 내용을 추출하는 기능을 제공합니다.
"""

import re
import logging
from typing import Dict, List, Optional, Union
from bs4 import BeautifulSoup

from .extractors import URLExtractor
from ..models.news import NewsArticle
from ..utils.config import get_config

logger = logging.getLogger(__name__)

class ContentExtractor(URLExtractor):
    """콘텐츠 추출 기본 클래스"""
    
    def extract_text_from_element(self, element) -> str:
        """요소에서 텍스트 추출"""
        if not element:
            return ""
            
        # 설정에서 불필요한 요소 목록 가져오기
        config = get_config()
        remove_elements = config.extraction.remove_elements
        
        # 불필요한 요소 제거
        for selector in remove_elements:
            for tag in element.select(selector):
                tag.decompose()
            
        # 단락별 텍스트 추출
        paragraphs = []
        for p in element.find_all(['p', 'div'], recursive=False):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
                
        return "\n".join(paragraphs) if paragraphs else element.get_text(strip=True)


class NaverNewsContentExtractor(ContentExtractor):
    """네이버 뉴스 콘텐츠 추출기"""
    
    def __init__(self):
        super().__init__()
        # 설정에서 CSS 선택자 로드
        self._load_selectors()
    
    def _load_selectors(self):
        """설정 파일에서 CSS 선택자를 로드합니다."""
        config = get_config()
        selectors = config.extraction.content_selectors
        
        self.TITLE_SELECTORS = selectors.get('title', [])
        self.PRESS_SELECTORS = selectors.get('press', [])
        self.CONTENT_SELECTORS = selectors.get('content', [])
        self.REPORTER_SELECTORS = selectors.get('reporter', [])
        
        # 날짜 선택자는 특별한 형식이므로 변환
        date_selectors = selectors.get('date', [])
        self.DATE_SELECTORS = []
        for item in date_selectors:
            if isinstance(item, dict):
                self.DATE_SELECTORS.append((item.get('selector'), item.get('attribute')))
            else:
                self.DATE_SELECTORS.append((item, None))
    
    def extract_news_content(self, url: str) -> NewsArticle:
        """단일 뉴스 URL에서 콘텐츠 추출"""
        logger.debug(f"콘텐츠 추출 시도: {url}")
        article = NewsArticle(url=url)
        
        html_content = self.get_page_content(url)
        if not html_content:
            return article
            
        try:
            soup = BeautifulSoup(html_content, 'lxml')
        except:
            # lxml 파서가 없을 경우 기본 파서 사용
            soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # 설정 다시 로드 (런타임 중 변경될 수 있음)
            self._load_selectors()
            config = get_config()
            
            # 제목 추출
            for selector in self.TITLE_SELECTORS:
                elem = soup.select_one(selector)
                if elem:
                    article.title = elem.get_text(separator=' ', strip=True)
                    break
            
            # 언론사 추출
            for selector in self.PRESS_SELECTORS:
                elem = soup.select_one(selector)
                if elem and elem.get('alt'):
                    article.press = elem['alt'].strip()
                    break
            
            # 날짜 추출
            for selector, attr in self.DATE_SELECTORS:
                elem = soup.select_one(selector)
                if elem:
                    if attr and elem.has_attr(attr):
                        article.date = elem[attr].strip()
                    else:
                        article.date = elem.get_text(strip=True)
                    break
            
            # 본문 추출
            for selector in self.CONTENT_SELECTORS:
                elem = soup.select_one(selector)
                if elem:
                    content_text = self.extract_text_from_element(elem)
                    # 본문 길이 검증
                    content_length = len(content_text)
                    if content_length >= config.extraction.min_content_length:
                        if content_length <= config.extraction.max_content_length:
                            article.content = content_text
                        else:
                            # 최대 길이 초과 시 잘라내기
                            article.content = content_text[:config.extraction.max_content_length]
                            logger.warning(f"본문이 너무 길어 잘라냈습니다: {url}")
                        break
                    else:
                        logger.debug(f"본문이 너무 짧음 ({content_length}자): {selector}")
            
            # 기자 추출
            for selector in self.REPORTER_SELECTORS:
                elem = soup.select_one(selector)
                if elem:
                    article.reporter = elem.get_text(strip=True)
                    break
            
            # 본문에서 기자 정보 추출 시도
            if not article.reporter and article.content:
                try:
                    reporter_pattern = r'([가-힣]{2,5}\s*(기자|특파원))'
                    match = re.search(reporter_pattern, article.content)
                    if match:
                        article.reporter = match.group(1).strip()
                except (AttributeError, TypeError) as e:
                    logger.debug(f"기자명 추출 중 오류 무시: {e}")
            
            if article.title:
                logger.debug(f"콘텐츠 추출 성공: {article.title[:30]}...")
            else:
                logger.warning(f"콘텐츠 추출 실패: {url}")
                
        except Exception as e:
            logger.error(f"콘텐츠 파싱 중 예외 발생 ({url}): {e}", exc_info=True)
        
        return article
