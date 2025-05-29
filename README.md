# 네이버 뉴스 크롤러 v4.1

네이버 뉴스 검색 결과를 수집하고 본문을 추출하는 Python 기반 크롤러입니다.

## 주요 기능

- 🔍 네이버 뉴스 검색 및 URL 수집
- 📄 뉴스 본문 자동 추출
- ⚙️ 다양한 검색 옵션 지원
- 📊 균등 분포 추출 모드
- 💾 배치 저장 시스템
- 🖥️ CLI 및 대화형 인터페이스
- 🆕 복수 검색어 지원 (v4.1)
- 🆕 언론사 선택 기능 (v4.1)
- 🆕 검색어×언론사×날짜 매트릭스 수집 (v4.1)

## 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/news-crawler-v4.git
cd news-crawler-v4

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

### 주요 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--period` | 검색 기간 | `1w`, `1m`, `custom` |
| `--extract-content` | 본문 추출 활성화 | - |
| `--content-limit` | 본문 추출 개수 제한 | `50` |
| `--extraction-mode` | 추출 방식 | `balanced`, `per_date` |

더 많은 옵션은 `python main.py --help` 참조

## 프로젝트 구조

```
news_crawler_ver_4/
├── src/
│   ├── core/       # 핵심 비즈니스 로직
│   ├── models/     # 데이터 모델
│   ├── ui/         # 사용자 인터페이스
│   └── utils/      # 유틸리티
├── data/           # 수집 데이터 저장
├── dev/            # 개발 관련 파일
│   └── analysis/   # 구조 분석 스크립트
├── docs/           # 프로젝트 문서
├── tests/          # 테스트 코드
├── config.json     # 설정 파일
├── main.py         # 진입점
└── requirements.txt # 의존성 패키지
```

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

### 403 Forbidden 오류
네이버가 봇을 감지하여 차단하는 경우:
- 설정 파일(`crawler_config.json`)에서 `delay_between_requests`를 3.0 이상으로 증가
- 프록시 사용: `set HTTP_PROXY=http://your-proxy:port`
- 자세한 해결 방법은 [403 오류 가이드](docs/403_ERROR_GUIDE.md) 참조

### Windows 한글 깨짐
데이터는 정상이며 콘솔 표시만 깨지는 경우:
- `chcp 65001` 실행 후 프로그램 실행
- 또는 PowerShell 사용 권장

더 많은 문제 해결 방법은 [사용자 가이드](docs/USER_GUIDE.md#8-문제-해결)를 참조하세요.

## 라이선스 및 주의사항

- 이 프로젝트는 교육 및 연구 목적으로 제작되었습니다
- 수집된 데이터의 저작권은 각 언론사에 있습니다
- 과도한 요청으로 인한 서버 부하를 주의하세요
- 네이버 서비스 이용약관을 준수하세요

## 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다! [개발 가이드](docs/DEVELOPMENT.md)를 참고하세요.

## 문제 해결

일반적인 문제와 해결 방법은 [사용자 가이드](docs/USER_GUIDE.md#8-문제-해결)를 참조하세요.

---

Made with ❤️ by [claude with 장상현]