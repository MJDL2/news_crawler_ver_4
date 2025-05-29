"""
파일 저장 유틸리티

크롤링 결과를 파일로 저장하는 기능을 제공합니다.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.news import NewsURL, NewsArticle, CrawlResult
from ..utils.config import get_config

logger = logging.getLogger(__name__)

class FileSaver:
    """파일 저장 유틸리티"""
    
    def __init__(self):
        self.config = get_config()
    
    def save_urls(self, urls: List[NewsURL], 
                  query: str,
                  period: str,
                  output_dir: Optional[str] = None) -> Optional[str]:
        """URL 목록을 JSON 파일로 저장"""
        if not urls:
            logger.warning("저장할 URL이 없습니다.")
            return None
        
        # 테스트 쿼리인 경우 test_results 디렉토리 사용
        if output_dir is None:
            if query.lower() in ['테스트', 'test']:
                output_dir = os.path.join('data', 'test_results')
            else:
                output_dir = self.config.storage.url_data_dir
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"urls_{query}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        data = {
            "query": query,
            "period": period,
            "collection_timestamp": timestamp,
            "total_urls": len(urls),
            "urls": [url.to_dict() for url in urls]
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"URL {len(urls)}개 저장 완료: {filepath}")
            return filepath
        except IOError as e:
            logger.error(f"파일 저장 오류: {e}")
            return None
    
    def save_articles(self, articles: List[NewsArticle],
                     query: str,
                     period: str,
                     output_dir: Optional[str] = None) -> List[str]:
        """기사 목록을 배치 파일로 저장"""
        if not articles:
            logger.warning("저장할 기사가 없습니다.")
            return []
        
        # 테스트 쿼리인 경우 test_results 디렉토리 사용
        if output_dir is None:
            if query.lower() in ['테스트', 'test']:
                output_dir = os.path.join('data', 'test_results')
            else:
                output_dir = self.config.storage.news_data_dir
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        batch_size = self.config.storage.max_news_per_file
        
        # 배치 단위로 저장
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            filename = f"news_{query}_{timestamp}_batch{batch_num}.json"
            filepath = os.path.join(output_dir, filename)
            
            data = {
                "metadata": {
                    "query": query,
                    "period": period,
                    "extraction_timestamp": timestamp,
                    "batch_number": batch_num,
                    "total_batches": (len(articles) + batch_size - 1) // batch_size,
                    "articles_in_batch": len(batch)
                },
                "articles": [article.to_dict() for article in batch]
            }
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                saved_files.append(filepath)
                logger.info(f"배치 {batch_num} 저장 완료: {filepath}")
            except IOError as e:
                logger.error(f"파일 저장 오류: {e}")
        
        return saved_files
    
    def save_crawl_result(self, result: CrawlResult,
                         output_dir: Optional[str] = None) -> Dict[str, Any]:
        """크롤링 결과 전체 저장"""
        saved_files = {
            "urls": None,
            "articles": [],
            "stats": None
        }
        
        # URL 저장
        if result.collected_urls:
            saved_files["urls"] = self.save_urls(
                result.collected_urls,
                result.query,
                result.period,
                output_dir
            )
        
        # 기사 저장
        if result.extracted_articles:
            saved_files["articles"] = self.save_articles(
                result.extracted_articles,
                result.query,
                result.period,
                output_dir
            )
        
        # 통계 저장
        stats_file = self.save_stats(result, output_dir)
        saved_files["stats"] = stats_file
        
        return saved_files
    
    def save_stats(self, result: CrawlResult,
                  output_dir: Optional[str] = None) -> Optional[str]:
        """크롤링 통계 저장"""
        # 테스트 쿼리인 경우 test_results 디렉토리 사용
        if output_dir is None:
            if result.query.lower() in ['테스트', 'test']:
                output_dir = os.path.join('data', 'test_results')
            else:
                output_dir = self.config.storage.news_data_dir
        stats_dir = os.path.join(output_dir, "stats")
        os.makedirs(stats_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"crawl_stats_{result.query}_{timestamp}.json"
        filepath = os.path.join(stats_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.get_stats(), f, ensure_ascii=False, indent=2)
            logger.info(f"통계 저장 완료: {filepath}")
            return filepath
        except IOError as e:
            logger.error(f"통계 파일 저장 오류: {e}")
            return None