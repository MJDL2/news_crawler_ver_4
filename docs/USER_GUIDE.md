# 네이버 뉴스 크롤러 v4 - 사용자 가이드

## 목차

1. [설치 및 설정](#1-설치-및-설정)
2. [사용 방법](#2-사용-방법)
3. [검색 옵션 상세](#3-검색-옵션-상세)
4. [URL 수집과 본문 추출](#4-url-수집과-본문-추출)
5. [설정 파일 가이드](#5-설정-파일-가이드)
6. [고급 기능](#6-고급-기능)
7. [자주 묻는 질문](#7-자주-묻는-질문)
8. [문제 해결](#8-문제-해결)

## 1. 설치 및 설정

### 필수 요구사항

- Python 3.8 이상
- pip 패키지 관리자
- 인터넷 연결

### 설치 과정

```bash
# 1. 저장소 복제 또는 다운로드
git clone https://github.com/your-username/news-crawler-v4.git
cd news-crawler-v4

# 2. 가상환경 생성 (권장)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
```

### 초기 설정

프로젝트는 기본 설정으로 바로 사용 가능하지만, `config.json`을 통해 커스터마이징할 수 있습니다.

## 2. 사용 방법

### 기본 사용법

```bash
# 간단한 검색
python main.py "검색어"

# 본문 추출 포함
python main.py "검색어" --extract-content

# 기간 설정 및 본문 추출
python main.py "검색어" --period 1w --extract-content --content-limit 10
```

### Windows 환경 사용자 주의사항

Windows에서 한글 검색어 사용 시:
```bash
# Windows PowerShell에서 (권장)
python main.py "한글검색어" --extract-content

# Command Prompt에서 UTF-8 설정 후 사용
chcp 65001
python main.py "한글검색어" --extract-content
```

### 대화형 모드

대화형 모드는 단계별로 옵션을 선택할 수 있습니다:

```bash
python main.py -i
# 또는
python main.py --interactive
```

#### Windows 환경에서 대화형 모드 사용 시

Windows에서 대화형 모드가 제대로 작동하지 않는 경우:

1. **권장 방법 1**: PowerShell 스크립트 사용
```powershell
.\run_interactive.ps1
```

2. **권장 방법 2**: 개선된 배치 파일 사용
```bash
run_interactive_v2.bat
```

3. **대안 1**: Python을 unbuffered 모드로 실행
```bash
python -u main.py -i
```

4. **대안 2**: 환경 변수 설정 후 실행
```bash
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
python main.py -i
```

**참고**: 
- Windows 환경에서는 대화형 모드보다 명령줄 인자 방식이 더 안정적입니다.
- 입력 후 Enter를 누른 뒤에도 진행되지 않으면 Ctrl+C로 종료하고 배치 파일을 사용하세요.
python main.py "검색어" --extract-content

# 대화형 모드
python main.py -i
```

### 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--period` | 검색 기간 | all |
| `--sort` | 정렬 방식 | relevance |
| `--type` | 뉴스 유형 | all |
| `--pages` | 수집 페이지 수 | 0 (무제한) |
| `--max-urls` | 최대 URL 수 | 0 (무제한) |
| `--extract-content` | 본문 추출 여부 | False |
| `--content-limit` | 본문 추출 개수 | 0 (무제한) |
| `--extraction-mode` | 추출 방식 | sequential |
| `--start-date` | 시작일 (YYYYMMDD) | - |
| `--end-date` | 종료일 (YYYYMMDD) | - |

### 사용 예시

```bash
# 최근 1주일 뉴스, 최신순, 본문 50개 추출
python main.py "인공지능" --period 1w --sort recent --extract-content --content-limit 50

# 특정 기간 검색
python main.py "경제" --period custom --start-date 20240501 --end-date 20240531

# URL 100개만 수집 (본문 추출 안함)
python main.py "기술" --pages 5 --max-urls 100

# 균등 분포로 본문 30개 추출
python main.py "정치" --extract-content --content-limit 30 --extraction-mode balanced
```

## 3. 검색 옵션 상세

### 검색 기간 (--period)

| 값 | 설명 |
|----|------|
| all | 전체 기간 |
| 1h | 1시간 이내 |
| 1d | 1일 이내 |
| 1w | 1주일 이내 |
| 1m | 1개월 이내 |
| 3m | 3개월 이내 |
| 6m | 6개월 이내 |
| 1y | 1년 이내 |
| custom | 직접 날짜 지정 |

### 정렬 방식 (--sort)

- `relevance`: 관련도순 (기본값)
- `recent`: 최신순
- `oldest`: 오래된순

### 뉴스 유형 (--type)

- `all`: 전체 (기본값)
- `photo`: 포토
- `video`: 동영상
- `print`: 지면기사
- `press_release`: 보도자료
- `auto`: 자동생성

## 4. URL 수집과 본문 추출

### 2단계 프로세스 이해

```
[1단계: URL 수집]
네이버 검색 → URL 목록 추출 → JSON 파일 저장

[2단계: 본문 추출]
URL 파일 읽기 → 각 URL 방문 → 본문 추출 → JSON 파일 저장
```

### URL 수집 제한
- `--max-urls 0`: 검색 결과의 모든 URL 수집
- `--max-urls 100`: 최대 100개 URL만 수집

### 본문 추출 제한

- `--content-limit 0`: 수집된 모든 URL에서 본문 추출
- `--content-limit 50`: 최대 50개 본문만 추출

### 추출 모드 (--extraction-mode)

1. **sequential**: 목록 순서대로 추출
2. **balanced**: 전체 범위에서 균등 분포
3. **per_date**: 날짜별 균등 분포

예시:
```bash
# 500개 URL 수집, 균등하게 100개 본문 추출
python main.py "검색어" --max-urls 500 --extract-content --content-limit 100 --extraction-mode balanced
```

## 5. 설정 파일 가이드

### config.json 구조

```json
{
  "network": {
    "timeout": 10,
    "max_retries": 3,
    "retry_delay": 1,
    "user_agent": "Mozilla/5.0..."
  },
  "storage": {
    "url_data_dir": "url_data",
    "news_data_dir": "news_data",
    "max_articles_per_file": 100
  },
  "crawling": {
    "url_delay": 0.5,
    "content_delay": 1.0,
    "batch_size": 20
  },
  "ui": {
    "show_progress": true,
    "debug_mode": false
  }
}
```

### 주요 설정 항목

#### 네트워크 설정
- `timeout`: HTTP 요청 타임아웃 (초)
- `max_retries`: 실패 시 재시도 횟수
- `user_agent`: 사용자 에이전트 문자열

#### 저장소 설정
- `url_data_dir`: URL 파일 저장 디렉토리
- `news_data_dir`: 뉴스 본문 저장 디렉토리
- `max_articles_per_file`: 파일당 최대 기사 수

#### 크롤링 설정
- `url_delay`: URL 수집 간 지연 시간
- `content_delay`: 본문 추출 간 지연 시간
- `batch_size`: 배치 처리 크기

## 6. 고급 기능

### 날짜별 수집

특정 기간을 일별로 나누어 수집하는 기능입니다. 긴 기간의 뉴스를 고르게 수집할 때 유용합니다.

#### 자동 활성화 조건
- 검색 기간이 1주 이상일 때 자동으로 제안됩니다

#### 작동 방식
1. 전체 기간을 일 단위로 분할
2. 각 날짜별로 지정된 개수만큼 수집
3. 중간 결과를 임시 파일로 저장
4. 최종적으로 하나의 결과로 통합

#### 사용 예시
```bash
# 대화형 모드에서
python main.py -i
# 또는
.\run_interactive.ps1
```

설정 예시:
- 검색 기간: 1개월 (30일)
- 일별 수집 제한: 10개
- 예상 결과: 30일 × 10개 = 최대 300개 기사

#### 장점
- 특정 날짜에 뉴스가 집중되어도 고른 분포로 수집
- 중간에 중단되어도 수집된 데이터는 보존
- 날짜별 수집 현황을 실시간으로 확인 가능

#### 진행 상황 표시
```
날짜별 수집을 시작합니다...
  검색어: 원전
  기간: 2025-04-28 ~ 2025-05-28 (30일)
  일별 제한: 10개

[2025-04-28] 수집 중... URL 15개, 본문 10개 ✓
[2025-04-29] 수집 중... URL 23개, 본문 10개 ✓
[2025-04-30] 수집 중... URL 8개, 본문 8개 ✓
...

날짜별 수집 완료!
  총 URL: 450개
  총 본문: 300개
  소요 시간: 123.4초
```

### 대화형 모드 상세 가이드 (v4.1.0 업데이트)

대화형 모드는 5단계의 간단한 질문으로 수집을 설정합니다:

#### 1단계: 검색어 입력
```
검색어를 입력하세요 (쉼표로 구분): 원전, 에너지, 재생에너지
→ 검색어: 원전, 에너지, 재생에너지
    검색어별로 개별 수집하시겠습니까? (Y/n): Y
```

#### 2단계: 언론사 선택
```
언론사 선택
  1. 전체 언론사
  2. 주요 언론사 (연합뉴스, 한겨레, 매일경제, 조선일보, 중앙일보)
  3. 직접 선택
선택 [1]: 2
→ 주요 언론사: 연합뉴스, 한겨레, 매일경제, 조선일보, 중앙일보
    언론사별로 개별 수집하시겠습니까? (y/N): y
```

#### 3단계: 검색 기간
```
검색 기간 설정
  1. 최근 1주 (1w)
  2. 최근 1개월 (1m) - 기본값
  3. 최근 3개월 (3m)
  4. 사용자 지정 기간 (custom)
선택 [2]: 4
시작 날짜: 20250501
종료 날짜: 20250531
→ 기간: 20250501 ~ 20250531
    날짜별로 분할 수집하시겠습니까? (Y/n): Y
```

#### 4단계: 정렬 방식
```
정렬 방식
  1. 관련도순 (relevance) - 기본값
  2. 최신순 (recent)
  3. 오래된순 (oldest)
선택 [1]: 2
→ 정렬: recent
```

#### 5단계: 수집 설정
```
수집 설정
일별 기사 수 제한 (0=무제한) [10]: 20
→ 일별 기사 수: 20

수집 모드
  1. 빠른 수집 (URL만)
  2. 전체 수집 (URL + 본문) - 기본값
선택 [2]: 2
→ URL과 본문 동시 수집
```

#### 최종 확인
```
============================================================
설정 확인
============================================================
  검색어: 원전, 에너지, 재생에너지
  언론사: 연합뉴스, 한겨레, 매일경제, 조선일보, 중앙일보
  검색 기간: custom
  기간: 20250501 ~ 20250531
  정렬: recent
  일별 수집 제한: 20
  수집 모드: 전체 (URL+본문)
  날짜별 분할 수집: 활성화
  검색어별 개별 수집: 활성화
  언론사별 개별 수집: 활성화
============================================================

이대로 진행하시겠습니까? (Y/n): Y
```

### 배치 처리

대량의 본문 추출 시 자동으로 배치 파일로 분할 저장:

```
news_data/
├── 검색어_20240528_120000_batch_1.json  (100개)
├── 검색어_20240528_120000_batch_2.json  (100개)
└── 검색어_20240528_120000_batch_3.json  (50개)
```

## 7. 자주 묻는 질문

### Q: 크롤링 속도를 높일 수 있나요?

설정 파일에서 지연 시간을 조정할 수 있지만, 너무 빠르면 차단될 위험이 있습니다:
```json
{
  "crawling": {
    "url_delay": 0.3,
    "content_delay": 0.5
  }
}
```

### Q: 특정 언론사만 수집할 수 있나요?

네, v4.1.0부터 가능합니다! 대화형 모드에서 언론사를 선택할 수 있습니다:
- 전체 언론사
- 주요 언론사 프리셋 (연합뉴스, 한겨레, 매일경제 등)
- 직접 입력

명령줄에서는 아직 지원하지 않으며, 추후 업데이트 예정입니다.

### Q: 중단된 작업을 이어서 할 수 있나요?

수집된 URL 파일을 이용해 본문 추출만 다시 실행할 수 있습니다:
```bash
# URL은 이미 수집됨, 본문만 추출
python main.py "검색어" --extract-content --skip-url-collection
```

### Q: 메모리 부족 문제가 발생합니다

배치 크기를 줄여보세요:
```json
{
  "crawling": {
    "batch_size": 10
  }
}
```

## 8. 문제 해결

### 일반적인 오류와 해결책

#### ImportError
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

#### ConnectionError
- 인터넷 연결 확인
- 프록시 설정 확인
- 방화벽 설정 확인

#### 빈 결과
- 검색어 확인
- 기간 설정 확인
- 네이버에서 직접 검색해보기

#### 본문 추출 실패
- 언론사 사이트 구조 변경 가능성
- GitHub 이슈에 보고

### 디버그 모드

상세한 로그를 보려면:
```json
{
  "ui": {
    "debug_mode": true
  }
}
```

### 지원 및 문의

- GitHub Issues: 버그 리포트 및 기능 제안
- Wiki: 추가 문서 및 튜토리얼
- Email: support@example.com

---

이 가이드는 지속적으로 업데이트됩니다. 최신 버전은 GitHub 리포지토리를 참조하세요.