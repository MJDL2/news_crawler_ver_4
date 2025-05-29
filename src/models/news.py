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
        """유효한 기사인지 확인"""
        return bool(self.title or self.content)

@dataclass
class CrawlResult:
    """크롤링 결과 데이터 모델"""
    query: str
    period: str
    collected_urls: List[NewsURL] = field(default_factory=list)
    extracted_articles: List[NewsArticle] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_url(self, url: NewsURL):
        """URL 추가"""
        self.collected_urls.append(url)
    
    def add_article(self, article: NewsArticle):
        """기사 추가"""
        self.extracted_articles.append(article)
    
    def add_error(self, error_type: str, message: str, details: Optional[Dict] = None):
        """에러 추가"""
        self.errors.append({
            'type': error_type,
            'message': message,
            'details': details or {},
            'occurred_at': datetime.now().isoformat()
        })
    
    def complete(self):
        """크롤링 완료 처리"""
        self.completed_at = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        duration = None
        if self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            
        return {
            'query': self.query,
            'period': self.period,
            'urls_collected': len(self.collected_urls),
            'articles_extracted': len(self.extracted_articles),
            'errors_count': len(self.errors),
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': duration
        }