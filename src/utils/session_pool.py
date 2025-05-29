"""
세션 풀 관리 모듈

403 오류 대응을 위한 세션 풀 관리 기능을 제공합니다.
"""

import time
import random
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import threading

import requests

from ..utils.config import get_config

logger = logging.getLogger(__name__)


class SessionInfo:
    """세션 정보 클래스"""
    
    def __init__(self, session: requests.Session, session_id: int):
        self.session = session
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_error = None
        self.is_blocked = False
        self.blocked_until = None
    
    def mark_used(self):
        """세션 사용 표시"""
        self.last_used = datetime.now()
        self.request_count += 1
    
    def mark_error(self, error_code: int = None):
        """에러 발생 표시"""
        self.error_count += 1
        self.last_error = error_code
        
        # 403 에러가 발생하면 일시적으로 차단
        if error_code == 403:
            self.is_blocked = True
            # 에러 횟수에 따라 차단 시간 증가
            block_minutes = min(self.error_count * 5, 30)  # 최대 30분
            self.blocked_until = datetime.now() + timedelta(minutes=block_minutes)
            logger.warning(f"세션 {self.session_id} 차단됨 ({block_minutes}분)")
    
    def is_available(self) -> bool:
        """세션 사용 가능 여부"""
        if not self.is_blocked:
            return True
        
        # 차단 시간이 지났는지 확인
        if self.blocked_until and datetime.now() > self.blocked_until:
            self.is_blocked = False
            self.error_count = 0  # 에러 카운트 리셋
            return True
        
        return False


class SessionPool:
    """세션 풀 관리 클래스"""
    
    def __init__(self, pool_size: int = 3):
        self.config = get_config()
        self.pool_size = pool_size
        self.sessions: List[SessionInfo] = []
        self.current_index = 0
        self.lock = threading.Lock()
        
        # 설정에서 세션 풀 크기 가져오기
        if hasattr(self.config, 'advanced') and self.config.advanced.session_management:
            self.pool_size = self.config.advanced.session_management.get('max_sessions_pool', pool_size)
        
        # 세션 풀 초기화
        self._initialize_pool()
    
    def _initialize_pool(self):
        """세션 풀 초기화"""
        logger.info(f"세션 풀 초기화 중 (크기: {self.pool_size})")
        
        for i in range(self.pool_size):
            session = self._create_session(i)
            session_info = SessionInfo(session, i)
            self.sessions.append(session_info)
            
            # 각 세션 초기화 사이에 지연
            if i < self.pool_size - 1:
                time.sleep(random.uniform(2, 4))
    
    def _create_session(self, session_id: int) -> requests.Session:
        """새 세션 생성"""
        session = requests.Session()
        
        # 헤더 설정 (User-Agent 다양화)
        headers = self.config.get_headers()
        session.headers.update(headers)
        
        # 프록시 설정
        proxies = self._get_proxy_config()
        if proxies:
            session.proxies = proxies
            logger.info(f"세션 {session_id}: 프록시 설정됨")
        
        # 네이버 초기 방문
        try:
            logger.info(f"세션 {session_id}: 네이버 초기화 중...")
            
            # 메인 페이지 방문
            main_response = session.get('https://www.naver.com', timeout=10)
            main_response.raise_for_status()
            time.sleep(random.uniform(0.5, 1.5))
            
            # 검색 페이지 방문
            search_response = session.get('https://search.naver.com', timeout=10)
            search_response.raise_for_status()
            
            logger.info(f"세션 {session_id}: 초기화 완료")
            
        except Exception as e:
            logger.warning(f"세션 {session_id} 초기화 경고: {e}")
        
        return session
    
    def _get_proxy_config(self) -> Optional[Dict[str, str]]:
        """프록시 설정 가져오기"""
        import os
        
        # 환경 변수에서 프록시 확인
        http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        
        if http_proxy or https_proxy:
            proxies = {}
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
            return proxies
        
        # 설정 파일에서 프록시 확인
        if hasattr(self.config, 'advanced') and self.config.advanced.anti_403:
            if self.config.advanced.anti_403.get('enable_proxy_rotation'):
                proxy_list = self.config.advanced.anti_403.get('proxy_list', [])
                if proxy_list:
                    proxy = random.choice(proxy_list)
                    return {'http': proxy, 'https': proxy}
        
        return None
    
    def get_session(self) -> requests.Session:
        """사용 가능한 세션 반환"""
        with self.lock:
            # 사용 가능한 세션 찾기
            available_sessions = [s for s in self.sessions if s.is_available()]
            
            if not available_sessions:
                logger.warning("사용 가능한 세션이 없습니다. 대기 중...")
                # 모든 세션이 차단된 경우, 가장 빨리 해제될 세션 대기
                wait_session = min(self.sessions, key=lambda s: s.blocked_until or datetime.max)
                if wait_session.blocked_until:
                    wait_seconds = (wait_session.blocked_until - datetime.now()).total_seconds()
                    if wait_seconds > 0:
                        logger.info(f"{wait_seconds:.0f}초 대기...")
                        time.sleep(wait_seconds)
                
                # 재시도
                available_sessions = [s for s in self.sessions if s.is_available()]
            
            # 라운드 로빈 방식으로 선택
            if available_sessions:
                # 가장 오래 사용하지 않은 세션 선택
                session_info = min(available_sessions, key=lambda s: s.last_used)
                session_info.mark_used()
                return session_info
            
            # 여전히 없으면 첫 번째 세션 강제 반환
            logger.warning("강제로 첫 번째 세션 반환")
            return self.sessions[0]
    
    def mark_error(self, session: requests.Session, error_code: int = None):
        """세션 에러 표시"""
        with self.lock:
            for session_info in self.sessions:
                if session_info.session == session:
                    session_info.mark_error(error_code)
                    break
    
    def refresh_session(self, session: requests.Session):
        """세션 갱신"""
        with self.lock:
            for i, session_info in enumerate(self.sessions):
                if session_info.session == session:
                    logger.info(f"세션 {session_info.session_id} 갱신 중...")
                    new_session = self._create_session(session_info.session_id)
                    self.sessions[i] = SessionInfo(new_session, session_info.session_id)
                    break
    
    def get_status(self) -> Dict[str, Any]:
        """세션 풀 상태 반환"""
        with self.lock:
            status = {
                'pool_size': self.pool_size,
                'available_sessions': len([s for s in self.sessions if s.is_available()]),
                'blocked_sessions': len([s for s in self.sessions if s.is_blocked]),
                'sessions': []
            }
            
            for session_info in self.sessions:
                status['sessions'].append({
                    'id': session_info.session_id,
                    'created_at': session_info.created_at.isoformat(),
                    'last_used': session_info.last_used.isoformat(),
                    'request_count': session_info.request_count,
                    'error_count': session_info.error_count,
                    'is_blocked': session_info.is_blocked,
                    'blocked_until': session_info.blocked_until.isoformat() if session_info.blocked_until else None
                })
            
            return status


# 전역 세션 풀 인스턴스
_session_pool = None


def get_session_pool() -> SessionPool:
    """전역 세션 풀 반환"""
    global _session_pool
    if _session_pool is None:
        _session_pool = SessionPool()
    return _session_pool
