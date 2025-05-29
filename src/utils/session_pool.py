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
            self.blocked_until = None
            logger.info(f"세션 {self.session_id} 차단 해제됨")
            return True
        
        return False


class SessionPool:
    """세션 풀 관리 클래스"""
    
    def __init__(self, max_sessions: int = 3):
        self.max_sessions = max_sessions
        self.sessions: List[SessionInfo] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self._create_initial_sessions()
    
    def _create_initial_sessions(self):
        """초기 세션들 생성"""
        for i in range(self.max_sessions):
            session = self._create_session(i)
            session_info = SessionInfo(session, i)
            self.sessions.append(session_info)
            logger.debug(f"세션 {i} 생성됨")
    
    def _create_session(self, session_id: int) -> requests.Session:
        """새 세션 생성"""
        session = requests.Session()
        
        # 기본 헤더 설정
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        ]
        
        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 네이버 메인 페이지 방문하여 쿠키 획득
        try:
            session.get('https://www.naver.com', timeout=10)
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.warning(f"세션 {session_id} 초기화 중 경고: {e}")
        
        return session
    
    def get_session(self) -> requests.Session:
        """사용 가능한 세션 반환"""
        with self.lock:
            # 사용 가능한 세션 찾기
            for _ in range(self.max_sessions):
                session_info = self.sessions[self.current_index]
                self.current_index = (self.current_index + 1) % self.max_sessions
                
                if session_info.is_available():
                    session_info.mark_used()
                    return session_info.session
            
            # 모든 세션이 차단된 경우 가장 오래된 세션 사용
            logger.warning("모든 세션이 차단됨, 가장 오래된 세션 사용")
            oldest_session = min(self.sessions, key=lambda s: s.last_used)
            oldest_session.mark_used()
            return oldest_session.session
    
    def mark_error(self, session: requests.Session, error_code: int):
        """세션 에러 마킹"""
        with self.lock:
            for session_info in self.sessions:
                if session_info.session is session:
                    session_info.mark_error(error_code)
                    
                    # 403 에러가 많이 발생하면 새 세션으로 교체
                    if error_code == 403 and session_info.error_count >= 3:
                        logger.info(f"세션 {session_info.session_id} 교체")
                        new_session = self._create_session(session_info.session_id)
                        session_info.session = new_session
                        session_info.error_count = 0
                        session_info.is_blocked = False
                        session_info.blocked_until = None
                    break
    
    def get_stats(self) -> Dict[str, Any]:
        """세션 풀 통계 반환"""
        with self.lock:
            stats = {
                'total_sessions': len(self.sessions),
                'available_sessions': sum(1 for s in self.sessions if s.is_available()),
                'blocked_sessions': sum(1 for s in self.sessions if s.is_blocked),
                'sessions': []
            }
            
            for session_info in self.sessions:
                stats['sessions'].append({
                    'session_id': session_info.session_id,
                    'request_count': session_info.request_count,
                    'error_count': session_info.error_count,
                    'is_blocked': session_info.is_blocked,
                    'last_error': session_info.last_error
                })
            
            return stats


# 글로벌 세션 풀 인스턴스
_session_pool = None
_lock = threading.Lock()


def get_session_pool(max_sessions: int = 3) -> SessionPool:
    """세션 풀 인스턴스 반환 (싱글톤)"""
    global _session_pool
    
    if _session_pool is None:
        with _lock:
            if _session_pool is None:
                _session_pool = SessionPool(max_sessions)
                logger.info(f"세션 풀 초기화 완료 (최대 {max_sessions}개)")
    
    return _session_pool
