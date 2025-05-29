"""
네이버 뉴스 크롤러 메인 모듈

프로그램의 진입점입니다.
"""

import sys
import os
import platform
import locale

# Windows에서 버퍼링 문제 해결
if platform.system() == 'Windows':
    # UTF-8 코드 페이지 설정
    os.system('chcp 65001 > nul 2>&1')
    
    # 환경 변수 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # 로케일 설정
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass

import logging

# Python 3.13 cookiejar 호환성 패치
import http.cookiejar
import time

def _patch_cookiejar():
    """Python 3.13 cookiejar 호환성 패치"""
    def _now_getter(self):
        return int(time.time())
    
    def _now_setter(self, value):
        pass
    
    # DefaultCookiePolicy 클래스에 _now 속성 추가
    if hasattr(http.cookiejar, 'DefaultCookiePolicy'):
        http.cookiejar.DefaultCookiePolicy._now = property(_now_getter, _now_setter)
    
    # CookieJar 클래스에도 _now 속성 추가
    if hasattr(http.cookiejar, 'CookieJar'):
        http.cookiejar.CookieJar._now = property(_now_getter, _now_setter)

# 패치 적용
_patch_cookiejar()
from src.ui.cli import main as cli_main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def main():
    """메인 함수"""
    # 대화형 모드인지 확인
    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive']:
        # 대화형 모드에서는 로깅 완전 비활성화
        logging.disable(logging.CRITICAL)
        # 모든 로거의 핸들러 제거
        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            logger.handlers = []
            logger.propagate = False
    
    return cli_main()

if __name__ == "__main__":
    sys.exit(main())