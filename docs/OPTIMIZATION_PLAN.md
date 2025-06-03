# 네이버 뉴스 크롤러 최적화 방안

## 1. 즉시 수정 필요한 부분

### interactive.py 수정
```python
# 기존 (122행)
content_limit = self.get_input("본문 추출 개수 (0=전체)", "20")

# 수정안
content_limit = self.get_input("병합시 최종 추출 개수 (0=전체)", "0")

# 날짜별 수집 모드 안내 수정 (131행 부근)
if date_diff >= 1:
    print(f"\n*** 날짜별 수집 모드 ***")
    print(f"각 날짜별로 URL을 수집하고 본문을 추출합니다.")
    print(f"예상 수집 기간: {date_diff + 1}일")
    
    # 일별 수집 제한 별도 입력
    daily_limit = self.get_input("일별 최대 수집 개수", "30")
    print(f"총 예상 수집량: 최대 {int(daily_limit) * (date_diff + 1)}개")
```

### cli.py 수정
```python
# 기존 (234행)
daily_limit = args.content_limit if args.content_limit > 0 else 10

# 수정안
daily_limit = args.daily_limit if hasattr(args, 'daily_limit') else 30
```

### daily_collector.py 수정
```python
# _select_contents_by_mode 메서드에 balanced 지원 추가
elif extraction_mode == 'even_distribution' or extraction_mode == 'balanced':
    # 날짜별 균등 분배 (balanced는 even_distribution의 별칭)
    return self._distribute_evenly_by_date(all_contents, content_limit)
```

## 2. 설정 파일 구조 개선

### unified_config.json에 추가
```json
{
  "daily_collection": {
    "daily_url_limit": 50,
    "daily_content_limit": 30,
    "merge_limit": 0,
    "default_extraction_mode": "balanced",
    "save_intermediate": true,
    "cleanup_temp_files": false
  }
}
```

## 3. 사용자 경험 개선

### 명확한 용어 사용
- "본문 추출 개수" → "병합시 최종 추출 개수"
- "추출 방식" → "기사 선택 방식"
- balanced = even_distribution 통일

### 진행률 표시 개선
```python
from tqdm import tqdm

# 날짜별 수집시
for date in tqdm(date_list, desc="날짜별 수집 진행"):
    # 수집 로직
    pass

# URL별 본문 추출시
for url in tqdm(urls, desc="본문 추출 진행"):
    # 추출 로직
    pass
```

## 4. 성능 최적화 (장기)

### 병렬 처리 도입
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def extract_with_rate_limit(urls, max_workers=3, delay=1.0):
    """403 오류 방지를 위한 제한된 병렬 처리"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 작업을 시간차를 두고 제출
        futures = []
        for i, url in enumerate(urls):
            if i > 0 and i % max_workers == 0:
                time.sleep(delay)
            
            future = executor.submit(extract_content, url)
            futures.append((url, future))
        
        # 결과 수집
        for url, future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logger.error(f"추출 실패 {url}: {e}")
    
    return results
```

### 캐싱 메커니즘
```python
import hashlib
import pickle
from pathlib import Path

class URLCache:
    def __init__(self, cache_dir="data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url):
        cache_file = self.cache_dir / f"{self.get_cache_key(url)}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, url, content):
        cache_file = self.cache_dir / f"{self.get_cache_key(url)}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(content, f)
```

## 5. 에러 처리 강화

### 재시도 로직 개선
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def extract_content_with_retry(url):
    """지수 백오프를 사용한 재시도"""
    return extract_content(url)
```

### 부분 실패 복구
```python
def collect_with_recovery(date_list):
    """실패한 날짜만 재수집"""
    failed_dates = []
    
    for date in date_list:
        try:
            collect_single_date(date)
        except Exception as e:
            logger.error(f"{date} 수집 실패: {e}")
            failed_dates.append(date)
    
    # 실패한 날짜 재시도
    if failed_dates:
        logger.info(f"{len(failed_dates)}개 날짜 재시도")
        for date in failed_dates:
            try:
                collect_single_date(date)
            except Exception as e:
                logger.error(f"{date} 재수집도 실패: {e}")
```

## 6. 모니터링 및 통계

### 상세 통계 수집
```python
class CrawlStatistics:
    def __init__(self):
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_urls': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'error_types': {},
            'response_times': [],
            'content_sizes': []
        }
    
    def record_extraction(self, url, success, error=None, response_time=None):
        if success:
            self.stats['successful_extractions'] += 1
            if response_time:
                self.stats['response_times'].append(response_time)
        else:
            self.stats['failed_extractions'] += 1
            error_type = type(error).__name__ if error else 'Unknown'
            self.stats['error_types'][error_type] = \
                self.stats['error_types'].get(error_type, 0) + 1
    
    def get_summary(self):
        return {
            'duration': self.stats['end_time'] - self.stats['start_time'],
            'success_rate': self.stats['successful_extractions'] / 
                           (self.stats['successful_extractions'] + 
                            self.stats['failed_extractions']),
            'avg_response_time': sum(self.stats['response_times']) / 
                                len(self.stats['response_times'])
                                if self.stats['response_times'] else 0
        }
```

## 7. 테스트 및 검증

### 단위 테스트 추가
```python
import pytest

def test_balanced_extraction():
    """balanced 추출 방식 테스트"""
    contents = [
        {'date': '2025-01-01', 'title': 'A'},
        {'date': '2025-01-01', 'title': 'B'},
        {'date': '2025-01-02', 'title': 'C'},
        {'date': '2025-01-02', 'title': 'D'},
    ]
    
    result = select_contents_by_mode(contents, 2, 'balanced')
    
    # 각 날짜에서 1개씩 선택되었는지 확인
    dates = [r['date'] for r in result]
    assert len(set(dates)) == 2
```

## 구현 우선순위

1. **긴급 (즉시)**: 
   - content_limit 기본값 0으로 변경
   - balanced 추출 방식 지원
   - UI 안내 문구 수정

2. **단기 (1주일 내)**:
   - 일별 수집 제한 파라미터 분리
   - 진행률 표시 개선
   - 기본 재시도 로직

3. **중기 (1개월 내)**:
   - 병렬 처리 도입
   - 캐싱 메커니즘
   - 상세 통계 수집

4. **장기 (3개월 내)**:
   - 완전한 에러 복구 시스템
   - 성능 모니터링 대시보드
   - 자동화된 테스트 스위트
