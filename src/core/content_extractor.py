"""
뉴스 콘텐츠 추출 모듈

네이버 뉴스 URL에서 본문 내용을 추출하는 기능을 제공합니다.
"""

import re
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from .extractors import URLExtractor
from ..models.news import NewsArticle

logger = logging.getLogger(__name__)

class ContentExtractor(URLExtractor):
    """콘텐츠 추출 기본 클래스"""
    
    def extract_text_from_element(self, element) -> str:
        """요소에서 텍스트 추출"""
        if not element:
            return ""
            
        # 불필요한 요소 제거
        for tag in element.select('.ad_wrap, .link_news_relation, script, style'):
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
    
    # 제목 선택자
    TITLE_SELECTORS = [
        'h2.media_end_head_headline',
        'div.media_end_head_title .media_end_head_headline',
        '#ct > div.media_end_head.go_trans > div.media_end_head_title > h2',
        '.article_header h3',
        '.content h3.tit_view'
    ]
    
    # 언론사 선택자
    PRESS_SELECTORS = [
        'a.media_end_head_top_logo img',
        'div.press_logo img',
        '.article_header .logo img',
        '.press_logo_wrap img'
    ]
    
    # 날짜 선택자
    DATE_SELECTORS = [
        ('span.media_end_head_info_datestamp_time', 'data-date-time'),
        ('div.media_end_head_info_datestamp_time', 'data-date-time'),
        ('span.media_end_head_info_datestamp_time', 'data-modify-date-time'),
        ('div.article_info em', None),
        ('.article_header .date', None),
        ('.article_info span.time', None)
    ]
    
    # 본문 선택자
    CONTENT_SELECTORS = [
        'div#newsct_article',
        'div#articleBodyContents',
        'div.article_body_contents',
        'div#articeBody',
        'div.news_content',
        'div.article_view_contents',
        '#articleBody'
    ]
    
    # 기자 선택자
    REPORTER_SELECTORS = [
        '.media_end_head_journalist_name',
        '.byline',
        '.journalist',
        '.article_footer .name',
        '.reporter'
    ]
    
    def extract_news_content(self, url: str) -> NewsArticle:
        """단일 뉴스 URL에서 콘텐츠 추출"""
        logger.debug(f"콘텐츠 추출 시도: {url}")
        article = NewsArticle(url=url)
        
        html_content = self.get_page_content(url)
        if not html_content:
            return article
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
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
                    article.content = self.extract_text_from_element(elem)
                    break
            
            # 기자 추출
            for selector in self.REPORTER_SELECTORS:
                elem = soup.select_one(selector)
                if elem:
                    article.reporter = elem.get_text(strip=True)
                    break
            
            # 본문에서 기자 정보 추출 시도
            if not article.reporter and article.content:
                reporter_pattern = r'([가-힣]{2,5}\s*(기자|특파원))'
                match = re.search(reporter_pattern, article.content)
                if match:
                    article.reporter = match.group(1).strip()
            
            if article.title:
                logger.debug(f"콘텐츠 추출 성공: {article.title[:30]}...")
            else:
                logger.warning(f"콘텐츠 추출 실패: {url}")
                
        except Exception as e:
            logger.error(f"콘텐츠 파싱 중 예외 발생 ({url}): {e}", exc_info=True)
        
        return article