# Python 3.13 호환성 수정 가이드

## 문제 설명

Python 3.13에서 `http.cookiejar` 모듈의 변경으로 인해 다음 오류가 발생할 수 있습니다:

```
AttributeError: 'DefaultCookiePolicy' object has no attribute '_now'
```

## 자동 해결

v4.2.0부터 `main.py`에 자동 패치가 적용되어 있습니다:

```python
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
```

## 수동 해결 (경우에 따라)

만약 자동 패치가 작동하지 않는 경우:

### 방법 1: Python 버전 다운그레이드 (권장)

```bash
# Python 3.11 또는 3.12 사용
pyenv install 3.12.0
pyenv local 3.12.0

# 또는 conda 사용
conda create -n news_crawler python=3.12
conda activate news_crawler
```

### 방법 2: 수동 패치 적용

`fix_python313.py` 파일을 생성하고 다음 코드 입력:

```python
#!/usr/bin/env python3
"""
Python 3.13 cookiejar 호환성 패치
"""

import http.cookiejar
import time
import sys

def patch_cookiejar():
    """Python 3.13에서 cookiejar 모듈 호환성 문제 해결"""
    
    # Python 3.13 버전 확인
    if sys.version_info >= (3, 13):
        print(f"Python {sys.version_info.major}.{sys.version_info.minor} 감지, cookiejar 패치 적용 중...")
        
        def _now_getter(self):
            return int(time.time())
        
        def _now_setter(self, value):
            pass
        
        # DefaultCookiePolicy 클래스에 _now 속성 추가
        if hasattr(http.cookiejar, 'DefaultCookiePolicy'):
            http.cookiejar.DefaultCookiePolicy._now = property(_now_getter, _now_setter)
            print("DefaultCookiePolicy 패치 완료")
        
        # CookieJar 클래스에도 _now 속성 추가
        if hasattr(http.cookiejar, 'CookieJar'):
            http.cookiejar.CookieJar._now = property(_now_getter, _now_setter)
            print("CookieJar 패치 완료")
            
        print("Python 3.13 cookiejar 호환성 패치 다료!")
    else:
        print(f"Python {sys.version_info.major}.{sys.version_info.minor} - 패치 불필요")

if __name__ == "__main__":
    patch_cookiejar()
```

그리고 메인 코드 실행 전에 패치 실행:

```bash
python fix_python313.py
python main.py "검색어"
```

### 방법 3: 환경 변수 설정

```bash
# 환경 변수로 호환성 모드 활성화
export PYTHON_LEGACY_COOKIEJAR=1
python main.py "검색어"
```

## 검증 방법

패치가 제대로 적용되었는지 확인:

```python
import http.cookiejar

# _now 속성 존재 확인
cookie_policy = http.cookiejar.DefaultCookiePolicy()
print(hasattr(cookie_policy, '_now'))  # True여야 함

cookie_jar = http.cookiejar.CookieJar()
print(hasattr(cookie_jar, '_now'))  # True여야 함
```

## 버전별 상태

| Python 버전 | 상태 | 바치 필요 |
|----------------|------|----------|
| 3.8 - 3.10 | 정상 작동 | 없음 |
| 3.11 - 3.12 | 정상 작동 | 없음 |
| 3.13+ | 오류 발생 가능 | 필요 (자동 적용됨) |

## 권장 사항

1. **Python 3.11 또는 3.12 사용 권장**
2. 자동 패치가 적용되어 있으므로 별도 작업 불필요
3. 문제 지속 시 Python 버전 다운그레이드 고려

---

**최종 업데이트**: 2025-05-29 (v4.2.1)