# 네이버 뉴스 크롤러 v4.2.7 - 사용자 가이드

## 🚨 중요: 안전한 실행 방법 (v4.2.7)

### ✅ 도움말 보기
```bash
show_help.bat                  # Windows에서 도움말 보기
python main.py --help          # 직접 도움말 확인 (v4.2.4~v4.2.7에서 안정화됨)
```

### ✅ 권장 실행 방법

#### 1순위: Windows 배치 파일 사용 (가장 안전)
```bash
run_interactive_v2.bat         # 대화형 모드 (권장)
run_safe_mode.bat             # 안전 모드 (403 방지)
```

#### 2순위: PowerShell 스크립트
```powershell
.\run_interactive.ps1         # PowerShell 대화형
.\run_with_proxy.ps1         # PowerShell 프록시 모드
```

#### 3순위: 직접 실행 (완전한 옵션 제공 시에만)
```bash
python main.py -i             # 대화형 모드로 직접 진입
python main.py "검색어" --extract-content --period 1w  # 완전한 인자 제공
```

⚠️ **주의**: CLI help 시스템에 버그가 있어 불완전한 명령어 실행 시 무한 대기 상태가 될 수 있습니다.

---

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
git clone https://github.com/MJDL2/news_crawler_ver_4.git
cd news_crawler_ver_4

# 2. 가상환경 생성 (권장)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
```

### 초기 설정

프로젝트는 기본 설정으로 바로 사용 가능하지만, `unified_config.json`을 통해 커스터마이징할 수 있습니다.

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

### Windows 환경 사용자 권장 방법

Windows에서는 다음 배치 파일들을 사용하는 것을 권장합니다:

```bash
# 대화형 모드 (가장 권장)
run_interactive_v2.bat

# 안전 모드 (403 오류 방지)
run_safe_mode.bat

# PowerShell 스크립트
run_interactive.ps1
```

### 대화형 모드

대화형 모드는 단계별로 옵션을 선택할 수 있습니다:

```bash
python main.py -i
# 또는
python main.py --interactive
```

## 3. 검색 옵션 상세

### 검색 기간 설정

| 옵션 | 설명 | 예시 |
|------|------|------|
| `all` | 전체 기간 | `--period all` |
| `1h` | 최근 1시간 | `--period 1h` |
| `1d` | 최근 1일 | `--period 1d` |
| `1w` | 최근 1주일 | `--period 1w` |
| `1m` | 최근 1개월 | `--period 1m` |
| `3m` | 최근 3개월 | `--period 3m` |
| `6m` | 최근 6개월 | `--period 6m` |
| `1y` | 최근 1년 | `--period 1y` |
| `custom` | 직접 지정 | `--period custom --start-date 20240101 --end-date 20240131` |

### 정렬 방식

- `relevance`: 관련도순 (기본값)
- `recent`: 최신순
- `oldest`: 오래된순

### 뉴스 유형

- `all`: 전체 (기본값)
- `photo`: 포토 뉴스
- `video`: 동영상 뉴스
- `print`: 지면 기사

## 4. URL 수집과 본문 추출

### URL 수집 옵션

```bash
# 최대 페이지 수 제한
python main.py "검색어" --pages 5

# 최대 URL 수 제한
python main.py "검색어" --max-urls 50

# URL 유형 필터링
python main.py "검색어" --url-type naver  # 네이버 뉴스만
python main.py "검색어" --url-type original  # 원본 사이트만
```

### 본문 추출 옵션

```bash
# 본문 추출 활성화
python main.py "검색어" --extract-content

# 추출할 본문 수 제한
python main.py "검색어" --extract-content --content-limit 20

# 추출 방식 선택
python main.py "검색어" --extract-content --extraction-mode balanced
```

### 추출 모드 설명

- `sequential`: 순차적 추출 (기본값)
- `balanced`: 균등 분포 추출 (전체 기간에서 고르게 선택)

## 5. 설정 파일 가이드

### v4.2.7 통합 설정: unified_config.json

v4.2.6에서 설정 파일이 완전히 통합되어 하나의 파일로 모든 설정을 관리합니다:

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

### 주요 설정 항목

- `delay_between_requests`: 요청 간 지연 시간 (403 오류 방지)
- `max_sessions_pool`: 세션 풀 크기 (403 오류 대응)
- `enable_progressive_backoff`: 점진적 백오프 활성화

## 6. 고급 기능

### 403 오류 대응

v4.2.0부터 자동 403 오류 대응 기능이 추가되었습니다:

- 세션 풀을 통한 자동 세션 교체
- 점진적 백오프 전략
- 프록시 지원

### 프록시 사용

```bash
# 환경 변수 설정
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port

# 또는 배치 파일 사용
run_with_proxy.bat
```

### 안전 모드

403 오류를 최소화하는 안전한 설정으로 실행:

```bash
run_safe_mode.bat
```

## 7. 자주 묻는 질문

### Q: Windows에서 한글이 깨져 보입니다.

A: 다음 방법을 시도해보세요:
1. `chcp 65001` 명령어 실행 후 프로그램 실행
2. PowerShell 사용: `run_interactive.ps1`
3. 배치 파일 사용: `run_interactive_v2.bat`

### Q: 403 Forbidden 오류가 발생합니다.

A: v4.2.7의 안정화된 대응 기능을 활용하세요:
1. `run_safe_mode.bat` 실행
2. `unified_config.json`에서 `delay_between_requests` 값 증가
3. 프록시 사용 고려 (v4.2.x에서 크게 개선됨)

### Q: Python 3.13에서 오류가 발생합니다.

A: 자동 패치가 적용되어 있지만, 문제 지속 시:
1. Python 3.11 또는 3.12 사용 권장
2. `docs/PYTHON313_FIX.md` 참조

## 8. 문제 해결

### 일반적인 문제들

1. **모듈을 찾을 수 없다는 오류**
   ```bash
   pip install -r requirements.txt
   ```

2. **인코딩 오류 (Windows)**
   ```bash
   set PYTHONIOENCODING=utf-8
   python main.py "검색어"
   ```

3. **대화형 모드가 응답하지 않음**
   ```bash
   python -u main.py -i
   ```

### 고급 문제 해결

자세한 문제 해결 방법은 다음 문서들을 참조하세요:
- `docs/403_ERROR_GUIDE.md` - 403 오류 해결
- `docs/PYTHON313_FIX.md` - Python 3.13 호환성
- `403_QUICK_FIX.md` - 즉시 해결 방법

### 지원 및 문의

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해주세요.

---

**마지막 업데이트: 2025-06-07 (v4.2.7)**
