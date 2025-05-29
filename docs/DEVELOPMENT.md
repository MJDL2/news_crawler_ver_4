# 네이버 뉴스 크롤러 v4 - 개발 가이드

## 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [코드 스타일 가이드](#2-코드-스타일-가이드)
3. [테스트](#3-테스트)
4. [새 기능 추가하기](#4-새-기능-추가하기)
5. [디버깅](#5-디버깅)
6. [기여 가이드라인](#6-기여-가이드라인)

## 1. 개발 환경 설정

### 개발 도구

- Python 3.8+
- VS Code 또는 PyCharm (권장)
- Git

### 개발 환경 구성

```bash
# 1. 저장소 포크 및 클론
git clone https://github.com/your-username/news-crawler-v4.git
cd news-crawler-v4

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt
```

## 2. 코드 스타일 가이드

### Python 스타일

- PEP 8 준수
- Type hints 사용 권장
- 문서화 문자열 작성

### 명명 규칙

- 클래스: PascalCase (예: `NewsCrawler`)
- 함수/메서드: snake_case (예: `extract_content`)
- 상수: UPPER_SNAKE_CASE (예: `MAX_RETRIES`)

### 문서화 예시

```python
def extract_news_content(url: str, timeout: int = 10) -> Optional[Dict[str, str]]:
    """
    뉴스 페이지에서 본문을 추출합니다.
    
    Args:
        url: 뉴스 기사 URL
        timeout: HTTP 요청 타임아웃 (초)
        
    Returns:
        추출된 뉴스 정보 딕셔너리 또는 None
    """
    pass
```

## 3. 테스트

### 단위 테스트 실행

```bash
# 전체 테스트 실행
python -m pytest

# 특정 모듈 테스트
python -m pytest tests/test_extractors.py
```

### 테스트 작성 예시

```python
import pytest
from src.core.extractors import NaverNewsURLExtractor

class TestNaverNewsURLExtractor:
    def test_extract_urls_from_html(self):
        extractor = NaverNewsURLExtractor()
        html = '<a href="https://n.news.naver.com/article/001/0001234">'
        urls = extractor.extract_urls(html)
        assert len(urls) == 1
```

## 4. 새 기능 추가하기

### 새로운 추출 모드 추가

1. `src/utils/` 에 새 추출기 클래스 생성
2. `src/core/content_extractor.py` 에 모드 추가
3. CLI 옵션에 선택지 추가

### 새로운 뉴스 사이트 지원

1. 파서 클래스 생성: `src/core/parsers/`
2. 팩토리 패턴으로 파서 선택 로직 추가
3. 테스트 케이스 작성

## 5. 디버깅

### 로깅 설정

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### 일반적인 디버깅 시나리오

- **URL 추출 문제**: HTML 구조 확인
- **본문 추출 실패**: CSS 셀렉터 테스트
- **403 오류**: 헤더 및 요청 간격 점검

## 6. 기여 가이드라인

### Pull Request 과정

1. 이슈 생성 또는 기존 이슈 확인
2. 기능 브랜치 생성: `feature/issue-number-description`
3. 코드 작성 및 테스트
4. 커밋 메시지 형식:
   ```
   type: 간단한 설명
   
   - 상세 내용
   - 변경 사항
   
   Fixes #123
   ```

### 커밋 타입

- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `refactor`: 리팩토링
- `test`: 테스트 추가

### 주요 개발 영역

1. **403 오류 대응 개선** (v4.2.0에서 크게 개선됨)
2. **다른 뉴스 사이트 지원 추가**
3. **비동기 처리 도입**
4. **웹 인터페이스 개발**

더 자세한 내용은 [PROGRESS.md](./PROGRESS.md)를 참조하세요.

---

*최종 업데이트: 2025-05-29*