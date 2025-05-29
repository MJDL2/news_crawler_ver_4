"""
네이버 뉴스 크롤러 설정 관리 모듈

프로젝트 전체에서 사용되는 설정값들을 중앙에서 관리합니다.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class NetworkConfig:
    """네트워크 관련 설정"""
    timeout: int = 10
    retries: int = 3
    backoff_factor: float = 2.0
    user_agents: List[str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0'
            ]

@dataclass
class StorageConfig:
    """데이터 저장 관련 설정"""
    news_data_dir: str = "data/news_data"
    url_data_dir: str = "data/url_data"
    test_results_dir: str = "data/test_results"
    max_news_per_file: int = 20
    file_encoding: str = "utf-8"
    
    def ensure_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        dirs = [self.news_data_dir, self.url_data_dir, self.test_results_dir]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"디렉토리 확인/생성: {dir_path}")

@dataclass
class CrawlingConfig:
    """크롤링 관련 설정"""
    max_urls_per_search: int = 100
    delay_between_requests: float = 1.0
    similarity_threshold: float = 0.8
    enable_progress_bar: bool = True
    log_level: str = "INFO"
    
@dataclass
class UIConfig:
    """사용자 인터페이스 관련 설정"""
    default_search_period: str = "1w"
    show_detailed_logs: bool = False
    confirm_before_extraction: bool = True

class Config:
    """네이버 뉴스 크롤러 설정 관리 클래스"""
    
    _instance = None
    _config_file = "crawler_config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.network = NetworkConfig()
        self.storage = StorageConfig()
        self.crawling = CrawlingConfig()
        self.ui = UIConfig()
        
        self._initialized = True
        self.load_config()
    
    def load_config(self, config_file: Optional[str] = None) -> None:
        """설정 파일에서 설정을 로드합니다."""
        config_path = config_file or self._config_file
        
        if not os.path.exists(config_path):
            logger.info(f"설정 파일이 없습니다. 기본 설정을 사용합니다: {config_path}")
            self.save_config()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 각 설정 섹션 업데이트
            if 'network' in data:
                self._update_dataclass(self.network, data['network'])
            if 'storage' in data:
                self._update_dataclass(self.storage, data['storage'])
            if 'crawling' in data:
                self._update_dataclass(self.crawling, data['crawling'])
            if 'ui' in data:
                self._update_dataclass(self.ui, data['ui'])
            
            logger.info(f"설정 파일 로드 완료: {config_path}")
            
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류: {e}")
            logger.info("기본 설정을 사용합니다.")
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """현재 설정을 파일에 저장합니다."""
        config_path = config_file or self._config_file
        
        try:
            config_data = {
                'network': asdict(self.network),
                'storage': asdict(self.storage),
                'crawling': asdict(self.crawling),
                'ui': asdict(self.ui)
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"설정 파일 저장 완료: {config_path}")
            
        except Exception as e:
            logger.error(f"설정 파일 저장 중 오류: {e}")
    
    def _update_dataclass(self, obj, data: Dict[str, Any]) -> None:
        """데이터클래스 객체를 딕셔너리 데이터로 업데이트합니다."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def get_headers(self) -> Dict[str, str]:
        """네트워크 요청용 헤더를 반환합니다."""
        import random
        return {
            'User-Agent': random.choice(self.network.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://search.naver.com/search.naver'
        }
    
    def setup_logging(self) -> None:
        """로깅 설정을 적용합니다."""
        logging.basicConfig(
            level=getattr(logging, self.crawling.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
    
    def initialize_environment(self) -> None:
        """실행 환경을 초기화합니다."""
        self.storage.ensure_directories()
        self.setup_logging()
        logger.info("크롤러 환경 초기화 완료")

# 싱글턴 인스턴스 생성
config = Config()

def get_config() -> Config:
    """설정 인스턴스를 반환합니다."""
    return config