# 네이버 뉴스 크롤러 v4 - 아키텍처 문서

## 프로젝트 개요

네이버 뉴스 크롤러는 네이버 뉴스 검색 결과를 수집하고 본문을 추출하는 자동화 시스템입니다. 모듈화된 구조와 계층화된 설계를 통해 유지보수성과 확장성을 극대화했습니다.

## 디렉토리 구조

```
news_crawler_ver_4/
├── main.py                    # 프로그램 진입점
├── requirements.txt           # 의존성 패키지 목록
├── unified_config.json       # 통합 설정 파일
│
├── src/                       # 소스 코드 디렉토리
│   ├── core/                  # 핵심 비즈니스 로직
│   │   ├── crawler.py         # 크롤링 엔진
│   │   ├── extractors.py      # URL 추출 모듈
│   │   ├── content_extractor.py  # 본문 추출 모듈
│   │   └── daily_collector.py    # 날짜별 수집 모듈
│   │
│   ├── models/                # 데이터 모델
│   │   ├── news.py            # 뉴스 데이터 클래스
│   │   └── search_options.py  # 검색 옵션 클래스
│   │
│   ├── ui/                    # 사용자 인터페이스
│   │   ├── cli.py             # 명령줄 인터페이스
│   │   └── interactive.py     # 대화형 인터페이스
│   │
│   └── utils/                 # 유틸리티 모듈
│       ├── config.py          # 설정 관리
│       ├── file_saver.py      # 파일 저장 유틸리티
│       └── balanced_extractor.py  # 균등 추출 유틸리티
│
├── data/                      # 데이터 저장 디렉토리
│   ├── news_data/             # 추출된 뉴스 본문
│   └── url_data/              # 수집된 URL 목록
│
├── docs/                      # 문서 디렉토리
└── tests/                     # 테스트 코드
```

## 아키텍처 설계 원칙

### 1. 계층화 (Layered Architecture)

```
┌─────────────────────────────────────┐
│          UI Layer (UI)               │
│    (CLI, Interactive Interface)      │
├─────────────────────────────────────┤
│      Business Logic Layer (Core)     │
│  (Crawler, Extractors, Collectors)   │
├─────────────────────────────────────┤
│         Data Layer (Models)          │
│    (News, SearchOptions, etc.)       │
├─────────────────────────────────────┤
│       Utility Layer (Utils)          │
│ (Config, FileSaver, BalancedExtractor)│
└─────────────────────────────────────┘
```

### 2. 모듈 간 의존성

```
main.py
    ├── ui/cli.py
    ├── ui/interactive.py
    └── core/crawler.py
            ├── models/search_options.py
            ├── core/extractors.py
            │       └── utils/config.py
            ├── core/content_extractor.py
            │       ├── utils/config.py
            │       ├── utils/file_saver.py
            │       └── utils/balanced_extractor.py
            └── core/daily_collector.py
                    └── utils/config.py
```

## 핵심 모듈 설명

### Core 모듈

#### crawler.py
- **역할**: 전체 크롤링 프로세스 오케스트레이션
- **주요 클래스**: `NewsCrawler`
- **주요 메서드**:
  - `run()`: 크롤링 실행
  - `collect_urls()`: URL 수집 단계
  - `extract_content()`: 본문 추출 단계

#### extractors.py
- **역할**: 네이버 검색 결과에서 URL 추출
- **주요 클래스**: `NaverNewsURLExtractor`
- **주요 기능**:
  - HTML 파싱 및 뉴스 링크 추출
  - 페이지네이션 처리
  - URL 메타데이터 수집

#### content_extractor.py
- **역할**: 네이버 뉴스 페이지에서 본문 추출
- **주요 클래스**: `NaverNewsContentExtractor`
- **추출 대상**:
  - 제목, 본문, 기자명, 언론사, 날짜

#### daily_collector.py
- **역할**: 날짜 범위별 뉴스 수집
- **주요 클래스**: `NaverNewsDailyCollector`
- **특징**: 대용량 데이터 수집 최적화

### Models 모듈

#### news.py
- **NewsURL**: URL 메타데이터 저장
- **NewsArticle**: 뉴스 기사 데이터 저장
- **CrawlResult**: 크롤링 결과 통계

#### search_options.py
- **NaverNewsSearchOption**: 네이버 검색 매개변수 관리

### Utils 모듈

#### config.py
- 통합 설정 파일(unified_config.json) 관리
- 환경별 설정 지원

#### file_saver.py
- 다양한 형식으로 파일 저장 (JSON, CSV, TXT)
- 파일명 중복 처리

## 데이터 플로우

```
1. 검색 쿼리 입력
    ↓
2. SearchOption 객체 생성
    ↓
3. URL 수집 (extractors.py)
    ↓
4. 본문 추출 (content_extractor.py)
    ↓
5. 데이터 저장 (file_saver.py)
    ↓
6. 결과 반환
```

## 확장 포인트

### 1. 새로운 사이트 지원
- `URLExtractor` 클래스 상속
- `ContentExtractor` 클래스 상속

### 2. 새로운 출력 형식
- `file_saver.py`에 새로운 포매터 추가

### 3. 새로운 UI
- `ui/` 디렉토리에 새로운 인터페이스 추가

## 성능 최적화

### 1. 네트워크 최적화
- 요청 간 지연 시간 조절
- 세션 재사용
- 프록시 지원

### 2. 메모리 최적화
- 스트리밍 처리
- 배치 저장

### 3. 오류 처리
- 재시도 메커니즘
- 403 오류 특별 처리

## 설정 관리

### unified_config.json 구조
```json
{
  "network": {
    "timeout": 30,
    "retries": 3,
    "request_delay_min": 1.0,
    "request_delay_max": 3.0
  },
  "crawling": {
    "max_pages_per_search": 10,
    "max_urls_per_search": 100
  },
  "storage": {
    "root_dir": "data",
    "news_data_dir": "data/news_data"
  }
}
```

## 보안 고려사항

1. **Rate Limiting**: 서버 부하 방지
2. **User-Agent 로테이션**: 탐지 회피
3. **프록시 지원**: IP 차단 대응
4. **쿠키 관리**: 세션 유지

## 테스트 전략

1. **단위 테스트**: 각 모듈별 기능 테스트
2. **통합 테스트**: 전체 워크플로우 테스트
3. **부하 테스트**: 대용량 데이터 처리 테스트

## 배포 및 운영

1. **환경 설정**: requirements.txt 기반 의존성 관리
2. **로깅**: 상세한 실행 로그 기록
3. **모니터링**: 성공률 및 오류율 추적