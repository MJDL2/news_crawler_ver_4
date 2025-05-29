"""
네이버 뉴스 날짜별 수집 모듈

날짜 범위별로 뉴스를 수집하는 기능을 제공합니다.
"""

import os
import logging
from datetime import datetime, timedelta
import time
import random
import json
from typing import List, Dict, Tuple, Optional, Any

# tqdm 프로그레스 바 지원
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from ..models.search_options import NaverNewsSearchOption
from ..models.news import NewsArticle
from ..utils.config import get_config
from .extractors import NaverNewsURLExtractor
from .content_extractor import NaverNewsContentExtractor

logger = logging.getLogger('daily_news_collector')


class NaverNewsDailyCollector:
    """네이버 뉴스 날짜별 수집 클래스"""
    
    def __init__(self):
        """초기화"""
        self.config = get_config()
        self.url_extractor = NaverNewsURLExtractor()
        self.content_extractor = NaverNewsContentExtractor()
        # root_dir 대신 news_data_dir의 상위 디렉토리 사용
        root_dir = os.path.dirname(self.config.storage.news_data_dir)
        self.temp_dir = os.path.join(root_dir, 'temp_daily')
        
        # 임시 디렉토리 생성
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def collect_date_range(
        self,
        query: str,
        start_date: datetime,
        end_date: datetime,
        sort: str = 'recent',        news_type: str = 'all',
        extract_content: bool = True,
        content_limit: int = 0,
        extraction_mode: str = 'sequential',
        daily_limit: int = 0,
        save_intermediate: bool = True
    ) -> Dict[str, Any]:
        """
        날짜 범위에 대해 일별로 뉴스를 수집
        
        Args:
            query: 검색어
            start_date: 시작 날짜
            end_date: 종료 날짜
            sort: 정렬 방식
            news_type: 뉴스 유형
            extract_content: 본문 추출 여부
            content_limit: 전체 본문 추출 개수 제한
            extraction_mode: 추출 방식
            daily_limit: 일별 추출 개수 제한
            save_intermediate: 중간 결과 저장 여부
            
        Returns:
            수집 결과 통계
        """
        # 날짜 리스트 생성
        date_list = self._generate_date_list(start_date, end_date)
        total_days = len(date_list)
        
        logger.info(f"날짜별 수집 시작: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} ({total_days}일)")
        logger.info(f"검색어: {query}, 정렬: {sort}, 유형: {news_type}")
        print(f"\n날짜별 수집을 시작합니다...")
        print(f"  검색어: {query}")
        print(f"  기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} ({total_days}일)")
        print(f"  일별 제한: {daily_limit}개")
        
        # 통계 초기화
        stats = {
            'query': query,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_days': total_days,
            'daily_results': [],
            'total_urls': 0,
            'total_contents': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'in_progress'
        }
        
        # 프로그레스 바 설정
        progress_bar = tqdm(date_list, desc="날짜별 수집") if TQDM_AVAILABLE else None        
        # 날짜별로 수집
        for date in (progress_bar if progress_bar else date_list):
            try:
                if progress_bar:
                    progress_bar.set_description(f"날짜별 수집 - {date.strftime('%Y-%m-%d')}")
                
                daily_result = self.collect_single_day(
                    query=query,
                    date=date,
                    sort=sort,
                    news_type=news_type,
                    extract_content=extract_content,
                    daily_limit=daily_limit,
                    save_intermediate=save_intermediate
                )
                
                stats['daily_results'].append(daily_result)
                stats['total_urls'] += daily_result.get('urls_collected', 0)
                stats['total_contents'] += daily_result.get('contents_extracted', 0)
                
                # 지연 시간 적용
                delay = self.config.crawling.delay_between_requests + random.uniform(0, 0.5)
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"날짜 {date.strftime('%Y-%m-%d')} 수집 실패: {e}")
                print(f" 실패: {e}")
                stats['daily_results'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        if progress_bar:
            progress_bar.close()
        
        # 통계 업데이트
        end_time = datetime.now()
        start_time = datetime.fromisoformat(stats['start_time'])
        stats['end_time'] = end_time.isoformat()
        stats['status'] = 'completed'
        stats['elapsed_time'] = (end_time - start_time).total_seconds()
        
        print(f"\n\n날짜별 수집 완료!")
        print(f"  총 URL: {stats['total_urls']}개")
        print(f"  총 본문: {stats['total_contents']}개")
        print(f"  소요 시간: {stats['elapsed_time']:.1f}초")
        
        # 통계 저장
        self._save_statistics(stats)
        
        # 최종 병합 처리
        if extract_content and content_limit > 0:
            self._merge_daily_contents(stats, content_limit, extraction_mode)
        
        return stats    
    def collect_single_day(
        self,
        query: str,
        date: datetime,
        sort: str = 'recent',
        news_type: str = 'all',
        extract_content: bool = True,
        daily_limit: int = 0,
        save_intermediate: bool = True
    ) -> Dict[str, Any]:
        """
        특정 날짜의 뉴스를 수집
        
        Args:
            query: 검색어
            date: 수집 날짜
            sort: 정렬 방식
            news_type: 뉴스 유형
            extract_content: 본문 추출 여부
            daily_limit: 일별 추출 개수 제한
            save_intermediate: 중간 결과 저장 여부
            
        Returns:
            수집 결과
        """
        date_str = date.strftime('%Y%m%d')
        logger.info(f"날짜 {date.strftime('%Y-%m-%d')} 수집 시작")
        print(f"\n[{date.strftime('%Y-%m-%d')}] 수집 중...", end='', flush=True)
        
        # 검색 옵션 설정
        search_option = NaverNewsSearchOption(query)
        search_option.set_period(NaverNewsSearchOption.PERIOD_CUSTOM, start_date=date_str, end_date=date_str)
        
        # 정렬 방식 매핑
        sort_map = {
            'relevance': NaverNewsSearchOption.SORT_BY_RELEVANCE,
            'recent': NaverNewsSearchOption.SORT_BY_RECENT,
            'oldest': NaverNewsSearchOption.SORT_BY_OLDEST
        }
        search_option.set_sort(sort_map.get(sort, NaverNewsSearchOption.SORT_BY_RELEVANCE))
        
        # 뉴스 유형 매핑
        type_map = {
            'all': NaverNewsSearchOption.TYPE_ALL,
            'photo': NaverNewsSearchOption.TYPE_PHOTO,
            'video': NaverNewsSearchOption.TYPE_VIDEO,
            'print': NaverNewsSearchOption.TYPE_PRINT,
            'press_release': NaverNewsSearchOption.TYPE_PRESS_RELEASE,
            'auto': NaverNewsSearchOption.TYPE_AUTO_GENERATED
        }
        search_option.set_news_type(type_map.get(news_type, NaverNewsSearchOption.TYPE_ALL))
        
        # URL 수집 - daily_limit을 URL 수집에도 적용
        url_file = None
        if save_intermediate:
            url_file = os.path.join(self.temp_dir, f"urls_{query}_{date_str}.json")
        
        # daily_limit이 있으면 URL 수집도 해당 개수로 제한
        max_urls_to_collect = daily_limit if daily_limit > 0 else 0
        
        urls = self.url_extractor.collect_from_search(
            search_url=search_option.build_url(),
            max_pages=0,  # 무제한
            max_urls=max_urls_to_collect,
            delay_sec=self.config.crawling.delay_between_requests
        )
        
        result = {
            'date': date.strftime('%Y-%m-%d'),
            'status': 'success',
            'urls_collected': len(urls),
            'url_file': url_file
        }
        
        # URL 중간 결과 저장
        if save_intermediate and urls:
            with open(url_file, 'w', encoding='utf-8') as f:
                url_data = [{'url': url.url, 'type': url.type, 'title': getattr(url, 'title', None)} for url in urls]
                json.dump(url_data, f, ensure_ascii=False, indent=2)
        
        # 본문 추출
        if extract_content and urls:
            content_file = None
            if save_intermediate:
                content_file = os.path.join(self.temp_dir, f"contents_{query}_{date_str}.json")
            
            # URL이 이미 daily_limit으로 제한되어 있으므로 모든 URL에서 본문 추출
            contents = []
            
            for i, url in enumerate(urls):
                if i > 0:
                    time.sleep(self.config.crawling.delay_between_requests)
                    
                article = self.content_extractor.extract_news_content(url.url)
                if article:
                    contents.append(article)
            
            # 중간 결과 저장
            if save_intermediate and contents:
                article_data = []
                for article in contents:
                    if article:
                        article_data.append(article.to_dict())
                
                with open(content_file, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            result['contents_extracted'] = len(contents)
            result['content_file'] = content_file
        
        logger.info(f"날짜 {date.strftime('%Y-%m-%d')} 수집 완료: URL {result['urls_collected']}개, 본문 {result.get('contents_extracted', 0)}개")
        print(f" URL {result['urls_collected']}개, 본문 {result.get('contents_extracted', 0)}개 [완료]")
        
        return result
    
    def _generate_date_list(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """날짜 리스트 생성"""
        date_list = []
        current_date = start_date
        
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        return date_list
    
    def _save_statistics(self, stats: Dict[str, Any]):
        """통계 정보 저장"""
        stats_dir = os.path.join(self.config.storage.news_data_dir, 'stats')
        os.makedirs(stats_dir, exist_ok=True)
        
        stats_file = os.path.join(
            stats_dir,
            f"daily_collection_stats_{stats['query']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"수집 통계 저장: {stats_file}")
    
    def _merge_daily_contents(self, stats: Dict[str, Any], content_limit: int, extraction_mode: str):
        """
        일별 수집된 컨텐츠를 병합
        
        Args:
            stats: 수집 통계 정보
            content_limit: 최종 병합할 컨텐츠 개수 제한
            extraction_mode: 병합 방식 ('sequential', 'even_distribution', 'recent_first')
        """
        logger.info(f"컨텐츠 병합 시작: {content_limit}개, 방식: {extraction_mode}")
        print(f"\n컨텐츠 병합 중... (최대 {content_limit}개, 방식: {extraction_mode})")
        
        # 모든 일별 컨텐츠 파일 수집
        all_contents = []
        content_files = []
        
        for daily_result in stats['daily_results']:
            if daily_result.get('status') == 'success' and daily_result.get('content_file'):
                content_file = daily_result['content_file']
                date = daily_result['date']
                
                if os.path.exists(content_file):
                    try:
                        with open(content_file, 'r', encoding='utf-8') as f:
                            daily_contents = json.load(f)
                            
                        # 각 컨텐츠에 날짜 정보 추가
                        for content in daily_contents:
                            content['collection_date'] = date
                            all_contents.append(content)
                        
                        content_files.append(content_file)
                        logger.info(f"날짜 {date}: {len(daily_contents)}개 컨텐츠 로드")
                        
                    except Exception as e:
                        logger.error(f"컨텐츠 파일 {content_file} 로드 실패: {e}")
        
        if not all_contents:
            logger.warning("병합할 컨텐츠가 없습니다.")
            print("  병합할 컨텐츠가 없습니다.")
            return
        
        logger.info(f"총 {len(all_contents)}개 컨텐츠 수집됨")
        print(f"  총 {len(all_contents)}개 컨텐츠 수집됨")
        
        # 병합 방식에 따른 컨텐츠 선택
        selected_contents = self._select_contents_by_mode(all_contents, content_limit, extraction_mode)
        
        # 최종 파일 저장
        merged_filename = f"merged_contents_{stats['query']}_{stats['start_date']}_{stats['end_date']}_{datetime.now().strftime('%H%M%S')}.json"
        merged_file = os.path.join(self.config.storage.news_data_dir, merged_filename)
        
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(selected_contents, f, ensure_ascii=False, indent=2)
        
        logger.info(f"병합 완료: {len(selected_contents)}개 컨텐츠 → {merged_file}")
        print(f"  병합 완료: {len(selected_contents)}개 컨텐츠")
        print(f"  저장 위치: {merged_file}")
        
        # 통계 업데이트
        stats['merged_file'] = merged_file
        stats['merged_contents'] = len(selected_contents)
        
        # 임시 파일 정리 (선택사항)
        if hasattr(self.config, 'cleanup_temp_files') and self.config.cleanup_temp_files:
            self._cleanup_temp_files(content_files)
    
    def _select_contents_by_mode(self, all_contents: List[Dict], content_limit: int, extraction_mode: str) -> List[Dict]:
        """
        병합 방식에 따라 컨텐츠 선택
        
        Args:
            all_contents: 모든 컨텐츠 리스트
            content_limit: 선택할 컨텐츠 개수
            extraction_mode: 선택 방식
            
        Returns:
            선택된 컨텐츠 리스트
        """
        if len(all_contents) <= content_limit:
            return all_contents
        
        if extraction_mode == 'sequential':
            # 순차적 선택 (날짜 순서대로)
            return all_contents[:content_limit]
            
        elif extraction_mode == 'recent_first':
            # 최신 날짜 우선 선택
            all_contents.sort(key=lambda x: x.get('collection_date', ''), reverse=True)
            return all_contents[:content_limit]
            
        elif extraction_mode == 'even_distribution':
            # 날짜별 균등 분배
            return self._distribute_evenly_by_date(all_contents, content_limit)
            
        else:
            # 기본값: sequential
            logger.warning(f"알 수 없는 추출 방식 '{extraction_mode}', sequential 방식 사용")
            return all_contents[:content_limit]
    
    def _distribute_evenly_by_date(self, all_contents: List[Dict], content_limit: int) -> List[Dict]:
        """
        날짜별로 균등하게 컨텐츠 분배
        
        Args:
            all_contents: 모든 컨텐츠 리스트
            content_limit: 선택할 컨텐츠 개수
            
        Returns:
            균등 분배된 컨텐츠 리스트
        """
        # 날짜별로 그룹화
        date_groups = {}
        for content in all_contents:
            date = content.get('collection_date', 'unknown')
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(content)
        
        dates = sorted(date_groups.keys())
        total_dates = len(dates)
        
        # 날짜별 할당량 계산
        base_quota = content_limit // total_dates
        extra_quota = content_limit % total_dates
        
        selected_contents = []
        
        for i, date in enumerate(dates):
            # 이 날짜의 할당량
            quota = base_quota + (1 if i < extra_quota else 0)
            
            # 해당 날짜의 컨텐츠에서 선택
            date_contents = date_groups[date]
            selected_from_date = date_contents[:quota] if len(date_contents) >= quota else date_contents
            selected_contents.extend(selected_from_date)
        
        logger.info(f"균등 분배 완료: {total_dates}개 날짜에서 {len(selected_contents)}개 선택")
        return selected_contents
    
    def _cleanup_temp_files(self, file_list: List[str]):
        """임시 파일 정리"""
        cleaned_count = 0
        for file_path in file_list:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"임시 파일 {file_path} 삭제 실패: {e}")
        
        logger.info(f"임시 파일 {cleaned_count}개 정리 완료")