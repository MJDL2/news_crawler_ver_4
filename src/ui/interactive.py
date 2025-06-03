"""
대화형 인터페이스 모듈

사용자와 대화하며 크롤링 옵션을 설정하는 인터페이스를 제공합니다.
"""

import sys
from typing import Dict, Any, Optional

class InteractiveInterface:
    """대화형 인터페이스"""
    
    def __init__(self):
        pass
    
    def get_input(self, prompt: str, default: str = None, options: list = None) -> str:
        """사용자 입력 받기"""
        if options:
            prompt += f" ({'/'.join(options)})"
        if default:
            prompt += f" [기본값: {default}]"
        prompt += ": "
        
        try:
            value = input(prompt).strip()
            if not value and default:
                return default
            if options and value not in options:
                print(f"올바른 옵션을 선택해주세요: {', '.join(options)}")
                return self.get_input(prompt.split(':')[0], default, options)
            return value
        except (KeyboardInterrupt, EOFError):
            print("\n작업이 취소되었습니다.")
            return None
    
    def get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """예/아니오 입력 받기"""
        default_str = "Y" if default else "N"
        response = self.get_input(f"{prompt} (y/n)", default_str, ["y", "n", "Y", "N"])
        if response is None:
            return None
        return response.lower() in ['y', 'yes', '예']
    
    def run(self) -> Optional[Dict[str, Any]]:
        """대화형 모드 실행"""
        print("=" * 50)
        print("    네이버 뉴스 크롤러 v4.2.1")
        print("=" * 50)
        print()
        
        # 기본 옵션 수집
        query = self.get_input("검색어를 입력하세요")
        if query is None:
            return None
        
        period = self.get_input("검색 기간", "1w", ["1h", "1d", "1w", "1m", "3m", "6m", "1y", "custom"])
        if period is None:
            return None
        
        start_date = None
        end_date = None
        if period == "custom":
            start_date = self.get_input("시작일 (YYYYMMDD)")
            if start_date is None:
                return None
            end_date = self.get_input("종료일 (YYYYMMDD)")
            if end_date is None:
                return None
            
            # 날짜별 수집 안내
            try:
                from datetime import datetime
                start_dt = datetime.strptime(start_date, '%Y%m%d')
                end_dt = datetime.strptime(end_date, '%Y%m%d')
                date_diff = (end_dt - start_dt).days
                
                if date_diff >= 1:
                    print(f"\n*** 알림: {date_diff + 1}일간의 기간이 설정되어 날짜별 수집 모드가 사용됩니다 ***")
                    print("각 날짜별로 개별 검색하여 지정된 개수만큼 수집합니다.")
                    
            except ValueError:
                print("날짜 형식을 확인해주세요 (YYYYMMDD)")
                return None
        
        sort = self.get_input("정렬 방식", "relevance", ["relevance", "recent", "oldest"])
        if sort is None:
            return None
        
        news_type = self.get_input("뉴스 유형", "all", ["all", "photo", "video", "print"])
        if news_type is None:
            return None
        
        print("\n--- 수집 옵션 ---")
        max_pages = self.get_input("최대 페이지 수 (0=무제한)", "5")
        if max_pages is None:
            return None
        try:
            max_pages = int(max_pages)
        except ValueError:
            max_pages = 5
        
        max_urls = self.get_input("최대 URL 수 (0=무제한)", "50")
        if max_urls is None:
            return None
        try:
            max_urls = int(max_urls)
        except ValueError:
            max_urls = 50
        
        url_type = self.get_input("URL 유형", "all", ["all", "naver", "original"])
        if url_type is None:
            return None
        
        print("\n--- 본문 추출 옵션 ---")
        extract_content = self.get_yes_no("본문을 추출하시겠습니까?", True)
        if extract_content is None:
            return None
        
        content_limit = 0
        extraction_mode = "balanced"
        
        if extract_content:
            content_limit = self.get_input("병합시 최종 추출 개수 (0=전체)", "0")
            if content_limit is None:
                return None
            try:
                content_limit = int(content_limit)
            except ValueError:
                content_limit = 0
            
            # custom 기간에서 날짜별 수집 모드일 때 안내
            daily_limit = 0  # 기본값 설정
            if period == "custom" and start_date and end_date:
                try:
                    from datetime import datetime
                    start_dt = datetime.strptime(start_date, '%Y%m%d')
                    end_dt = datetime.strptime(end_date, '%Y%m%d')
                    date_diff = (end_dt - start_dt).days
                    
                    if date_diff >= 1:
                        print(f"\n*** 날짜별 수집 모드 ***")
                        print(f"검색 기간: {date_diff + 1}일 ({start_date} ~ {end_date})")
                        print(f"날짜별로 URL을 수집하고 본문을 추출합니다.")
                        
                        # 일별 수집 제한 입력
                        daily_limit = self.get_input("일별 최대 수집 개수", "30")
                        if daily_limit is None:
                            return None
                        try:
                            daily_limit = int(daily_limit)
                        except ValueError:
                            daily_limit = 30
                        
                        print(f"\n예상 수집량:")
                        print(f"  - 일별 최대: {daily_limit}개")
                        print(f"  - 전체 최대: {daily_limit * (date_diff + 1)}개")
                        
                        if content_limit > 0:
                            print(f"  - 병합시 최종: {content_limit}개로 제한")
                        else:
                            print(f"  - 병합시: 전체 포함")
                    else:
                        daily_limit = 0
                        
                except ValueError:
                    pass
            
            extraction_mode = self.get_input("추출 방식", "balanced", ["sequential", "balanced"])
            if extraction_mode is None:
                return None
        
        print("\n--- 저장 옵션 ---")
        output = self.get_input("본문 저장 디렉토리", "data/news_data")
        if output is None:
            return None
        
        url_output = self.get_input("URL 저장 디렉토리", "data/url_data")
        if url_output is None:
            return None
        
        # 설정 확인
        print("\n" + "=" * 50)
        print("설정 확인")
        print("=" * 50)
        print(f"검색어: {query}")
        print(f"기간: {period}")
        if start_date and end_date:
            print(f"날짜: {start_date} ~ {end_date}")
        print(f"정렬: {sort}")
        print(f"유형: {news_type}")
        print(f"최대 페이지: {max_pages}")
        print(f"최대 URL: {max_urls}")
        print(f"URL 유형: {url_type}")
        print(f"본문 추출: {'예' if extract_content else '아니오'}")
        if extract_content:
            if 'daily_limit' in locals() and daily_limit > 0:
                print(f"일별 수집: {daily_limit}개")
            print(f"병합시 제한: {content_limit if content_limit > 0 else '전체'}")
            print(f"추출 방식: {extraction_mode}")
        print(f"저장 위치: {output}")
        
        confirm = self.get_yes_no("\n이 설정으로 크롤링을 시작하시겠습니까?", True)
        if confirm is None or not confirm:
            return None
        
        return {
            'query': query,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'sort': sort,
            'news_type': news_type,
            'max_pages': max_pages,
            'max_urls': max_urls,
            'url_type': url_type,
            'extract_content': extract_content,
            'content_limit': content_limit,
            'extraction_mode': extraction_mode,
            'output': output,
            'url_output': url_output,
            'daily_limit': daily_limit if 'daily_limit' in locals() else 0
        }
