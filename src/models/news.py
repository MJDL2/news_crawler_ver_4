"""
뉴스 데이터 모델

뉴스 관련 데이터 구조를 정의합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class NewsURL:
    """뉴스 URL 데이터 모델"""
    url: str
    type: str  # 'naver' or 'original'
    title: Optional[str] = None
    search_date: Optional[str] = None
    collected_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'url': self.url,
            'type': self.type,
            'title': self.title,
            'search_date': self.search_date,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

@dataclass
class NewsArticle:
    """뉴스 기사 데이터 모델"""
    url: str
    title: str = ''
    press: str = ''
    date: str = ''
    content: str = ''
    reporter: str = ''
    extracted_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'url': self.url,
            'title': self.title,
            'press': self.press,
            'date': self.date,
            'content': self.content,
            'reporter': self.reporter,
            'extracted_at': self.extracted_at.isoformat() if self.extracted_at else None
        }
    
    def is_valid(self) -> bool:
        """기사 데이터가 유효한지 확인"""
        return bool(self.title and self.content and len(self.content.strip()) > 50)

@dataclass 
class CrawlResult:
    """크롤링 결과 데이터 모델"""
    query: str
    period: str
    urls: List[NewsURL] = field(default_factory=list)
    articles: List[NewsArticle] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    start_time: Optional[datetime] = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    def add_url(self, url: NewsURL):
        """URL 추가"""
        self.urls.append(url)
    
    def add_article(self, article: NewsArticle):
        """기사 추가"""
        self.articles.append(article)
    
    def add_error(self, error_type: str, message: str):
        """에러 추가"""
        self.errors.append({
            'type': error_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def complete(self):
        """크롤링 완료 처리"""
        self.end_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'query': self.query,
            'period': self.period,
            'urls': [url.to_dict() for url in self.urls],
            'articles': [article.to_dict() for article in self.articles],
            'errors': self.errors,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'stats': {
                'total_urls': len(self.urls),
                'total_articles': len(self.articles),
                'total_errors': len(self.errors)
            }
        }
