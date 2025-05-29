# 네이버 뉴스 크롤러 v4.2.1

네이버 뉴스 검색 결과를 수집하고 본문을 추출하는 Python 기반 크롤러입니다.

## 주요 기능

- 🔍 네이버 뉴스 검색 및 URL 수집
- 📄 뉴스 본문 자동 추출
- ⚙️ 다양한 검색 옵션 지원
- 📊 균등 분포 추출 모드
- 💾 배치 저장 시스템
- 🖥️ CLI 및 대화형 인터페이스
- 🔄 복수 검색어 지원 (v4.1)
- 🏢 언론사 선택 기능 (v4.1)
- 📅 검색어×언론사×날짜 매트릭스 수집 (v4.1)
- 🛡️ 403 오류 대응 및 세션 풀 관리 (v4.2)
- ⚙️ 통합 설정 파일 시스템 (v4.2)
- 🔄 개선된 날짜별 수집 및 병합 기능 (v4.2)

## 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/MJDL2/news_crawler_ver_4.git
cd news_crawler_ver_4

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 간단한 검색
python main.py "검색어"

# 본문 추출 포함
python main.py "검색어" --extract-content

# 대화형 모드
python main.py -i

# Windows에서 대화형 모드 (권장)
run_interactive_v2.bat
# 또는 PowerShell
.\run_interactive.ps1

# 안전 모드 실행 (403 오류 방지)
run_safe_mode.bat

# 프록시를 통한 실행
run_with_proxy.bat  # 프록시 주소 설정 필요
```

### 설정 파일 (v4.2.0 업데이트)

**권장**: `unified_config.json` 사용 (모든 설정 통합)
**레거시**: `config.json` + `crawler_config.json` (하위 호환성 유지)

#### 주요 설정 항목

```json
{
  "network": {
    "timeout": 30,
    "retries": 3,
    "delay_between_requests": 2.0
  },
  "extraction": {
    "min_content_length": 100,
    "max_content_length": 50000
  },
  "advanced": {
    "session_management": {
      "max_sessions_pool": 3,
      "enable_cookie_persistence": true
    },
    "anti_403": {
      "enable_progressive_backoff": true,
      "max_backoff_seconds": 120
    }
  }
}
```

### 주요 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--period` | 검색 기간 | `1w`, `1m`, `custom` |
| `--extract-content` | 본문 추출 활성화 | - |
| `--content-limit` | 본문 추출 개수 제한 | `50` |
| `--extraction-mode` | 추출 방식 | `balanced`, `per_date` |

더 많은 옵션은 `python main.py --help` 참조

## 프로젝트 구조 (실제 검증됨 - 2025.05.29)

```
news_crawler_ver_4/
├── src/
│   ├── core/       # 핵심 비즈니스 로직
│   │   ├── crawler.py          # 메인 크롤링 엔진
│   │   ├── extractors.py       # URL 추출 모듈
│   │   ├── content_extractor.py # 본문 추출 모듈
│   │   └── daily_collector.py  # 날짜별 수집 모듈
│   ├── models/     # 데이터 모델
│   │   ├── news.py             # 뉴스 데이터 클래스
│   │   └── search_options.py   # 검색 옵션 클래스
│   ├── ui/         # 사용자 인터페이스
│   │   ├── cli.py              # 명령줄 인터페이스 ⚠️
│   │   └── interactive.py      # 대화형 인터페이스
│   └── utils/      # 유틸리티
│       ├── config.py           # 설정 관리
│       ├── file_saver.py       # 파일 저장 유틸리티
│       ├── balanced_extractor.py # 균등 추출 알고리즘
│       └── session_pool.py     # 세션 풀 관리 (v4.2)
├── data/           # 수집 데이터 저장
│   ├── news_data/  # 추출된 뉴스 본문
│   ├── url_data/   # 수집된 URL 목록
│   ├── test_results/ # 테스트 결과
│   └── temp/       # 임시 파일
├── docs/           # 프로젝트 문서
│   ├── ARCHITECTURE.md     # 아키텍처 설계
│   ├── DEVELOPMENT.md      # 개발 가이드
│   ├── PROGRESS.md         # 진행 상황
│   ├── USER_GUIDE.md       # 사용자 가이드
│   ├── CHANGELOG.md        # 변경 이력
│   ├── 403_ERROR_GUIDE.md  # 403 오류 해결
│   ├── PYTHON313_FIX.md    # Python 3.13 호환성
│   └── IMPROVEMENTS_v4.2.0.md # v4.2.0 개선사항
├── tests/          # 테스트 코드
├── test_scripts/   # 테스트 스크립트
├── config.json     # 레거시 설정 파일
├── crawler_config.json # 크롤링 설정 파일
├── unified_config.json # 통합 설정 파일 (v4.2 권장)
├── main.py         # 진입점
├── requirements.txt # 의존성 패키지
├── run_interactive_v2.bat # Windows 대화형 실행 (권장)
├── run_safe_mode.bat     # 403 오류 대응 모드
├── run_with_proxy.bat    # 프록시 실행 모드
└── run_interactive.ps1   # PowerShell 실행 스크립트
```

## ⚠️ 알려진 문제 (v4.2.1)

**CLI 실행 주의사항**: `python main.py --help` 명령이 무한 대기 상태가 됩니다.

**권장 실행 방법**:
- `run_interactive_v2.bat` (Windows 배치파일)
- `python main.py -i` (대화형 모드 직접 진입)
- `.\run_interactive.ps1` (PowerShell 스크립트)

## 문서

- 📖 [사용자 가이드](docs/USER_GUIDE.md) - 상세한 사용 방법
- 🏗️ [아키텍처 문서](docs/ARCHITECTURE.md) - 프로젝트 구조 및 설계
- 💻 [개발 가이드](docs/DEVELOPMENT.md) - 개발 및 기여 방법
- 📝 [변경 이력](docs/CHANGELOG.md) - 버전별 변경사항
- 📊 [진행 상황](docs/PROGRESS.md) - 현재 개발 상태 및 계획

## 예시

### 최근 1주일 AI 뉴스 수집
```bash
python main.py "인공지능" --period 1w --sort recent --extract-content --content-limit 50
```

### 특정 기간 뉴스 균등 추출
```bash
python main.py "경제" --period custom --start-date 20240501 --end-date 20240531 --extract-content --extraction-mode balanced
```

## 출력 형식

수집된 데이터는 JSON 형식으로 저장됩니다:

- **URL 파일**: `url_data/검색어_YYYYMMDD_HHMMSS.json`
- **본문 파일**: `news_data/검색어_YYYYMMDD_HHMMSS_batch_N.json`

## 요구사항

- Python 3.8 이상
- 인터넷 연결
- 필수 패키지: `requests`, `beautifulsoup4`, `tqdm`

## 문제 해결

### 403 Forbidden 오류 (v4.2.0 개선)
네이버가 봇을 감지하여 차단하는 경우:
- **자동 대응**: 세션 풀 관리로 차단된 세션 자동 교체
- **설정 조정**: `unified_config.json`에서 `delay_between_requests`를 3.0 이상으로 증가
- **프록시 사용**: 환경 변수 설정 `set HTTP_PROXY=http://your-proxy:port`
- **안전 모드**: `run_safe_mode.bat` 실행
- 자세한 해결 방법은 [403 오류 가이드](docs/403_ERROR_GUIDE.md) 참조

### Windows 한글 깨짐
데이터는 정상이며 콘솔 표시만 깨지는 경우:
- `chcp 65001` 실행 후 프로그램 실행
- 또는 PowerShell 사용 권장: `.\run_interactive.ps1`

### Python 3.13 호환성
Python 3.13 사용 시 cookiejar 오류가 발생하는 경우:
- 자동 패치가 적용되어 있지만, 문제 지속 시 [Python 3.13 수정 가이드](docs/PYTHON313_FIX.md) 참조
- 권장: Python 3.11 또는 3.12 사용

### 설정 파일 관련
- **v4.2.0**: `unified_config.json` 사용 권장 (모든 설정 통합)
- **이전 버전**: `config.json` + `crawler_config.json` (하위 호환성 유지)
- 설정 충돌 시: `unified_config.json`이 우선 적용

더 많은 문제 해결 방법은 [사용자 가이드](docs/USER_GUIDE.md#8-문제-해결)를 참조하세요.

## 라이선스 및 주의사항

- 이 프로젝트는 교육 및 연구 목적으로 제작되었습니다
- 수집된 데이터의 저작권은 각 언론사에 있습니다
- 과도한 요청으로 인한 서버 부하를 주의하세요
- 네이버 서비스 이용약관을 준수하세요
- v4.2.0부터 403 오류 자동 대응 기능이 추가되었으나, 적절한 사용을 권장합니다

## 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다!

### 주요 개발 영역
- 403 오류 대응 개선 (v4.2.0에서 크게 개선됨)
- 다른 뉴스 사이트 지원 추가
- 비동기 처리 도입
- 웹 인터페이스 개발

자세한 내용은 [개발 가이드](docs/DEVELOPMENT.md)를 참고하세요.

## 버전 히스토리

- **v4.2.1 (2025-05-29)**: 날짜별 수집 문제 분석, issues 디렉토리 추가
- **v4.2.0 (2025-05-29)**: 통합 설정 파일, 세션 풀 관리, 403 오류 대응 강화
- **v4.1.x (2025-05-28)**: 복수 검색어, 언론사 선택, 대화형 인터페이스 개선
- **v4.0.0 (2025-05-28)**: 전면 리팩토링, 모듈화 아키텍처
- **v3.x**: 균등 추출, 날짜별 수집 기능
- **v2.x**: 본문 추출, 배치 저장 시스템
- **v1.x**: 기본 크롤링 기능

전체 변경 이력은 [CHANGELOG.md](docs/CHANGELOG.md)를 참조하세요.

---

Made with ❤️ by [Claude AI & 개발팀]

*최종 업데이트: 2025-05-29 (v4.2.0)*