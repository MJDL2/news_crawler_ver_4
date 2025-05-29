# Python 3.13 호환성 문제 해결 가이드

## 문제 설명

Python 3.13에서 네이버 뉴스 크롤러 실행 시 다음과 같은 오류가 발생합니다:

```
AttributeError: 'NoneType' object has no attribute '_now' and no **dict** for setting new attributes
```

이 오류는 `requests` 라이브러리의 쿠키 처리 과정에서 발생하며, Python 3.13의 변경된 속성 설정 규칙과 관련이 있습니다.

## 원인 분석

1. **Python 3.13의 변경사항**: Python 3.13에서는 `__dict__`가 없는 객체에 대한 속성 설정이 더 엄격해졌습니다.

2. **쿠키 정책 문제**: `extractors.py`에서 `session.cookies.set_policy(None)`으로 쿠키 정책을 None으로 설정하면, 나중에 `cookiejar`가 None 객체에 `_now` 속성을 설정하려고 시도할 때 오류가 발생합니다.

3. **requests 라이브러리 호환성**: 현재 버전의 requests 라이브러리가 Python 3.13의 새로운 속성 설정 규칙을 완전히 지원하지 않을 수 있습니다.

## 해결 방법

### 1. 즉시 적용 가능한 수정사항 (이미 적용됨)

1. **쿠키 정책 설정 제거**
   - `extractors.py`의 35번째 줄에서 `self._session.cookies.set_policy(None)` 라인을 제거 또는 주석 처리

2. **Python 3.13 호환성 패치 추가**
   - `main.py`에 cookiejar 호환성 패치 코드 추가

### 2. 대체 해결 방법

만약 여전히 문제가 발생한다면:

1. **Python 버전 다운그레이드**
   ```
   Python 3.11 또는 3.12 사용을 권장합니다.
   ```

2. **requests 라이브러리 업데이트**
   ```bash
   pip install --upgrade requests
   ```

3. **대체 세션 초기화 방법**
   ```python
   # extractors.py에서
   self._session = requests.Session()
   self._session.headers.update(self.config.get_headers())
   # 쿠키 정책을 명시적으로 설정
   from http.cookiejar import DefaultCookiePolicy
   self._session.cookies.set_policy(DefaultCookiePolicy())
   ```

## 테스트 방법

수정 후 다음 명령으로 테스트:

```bash
run_interactive.bat
```

또는 직접 실행:

```bash
python main.py --keyword "테스트" --days 1
```

## 추가 권장사항

1. **가상 환경 사용**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Python 버전 확인**
   ```bash
   python --version
   ```

3. **라이브러리 버전 확인**
   ```bash
   pip show requests
   ```

## 문제가 지속될 경우

1. 오류 로그 전체를 수집
2. Python 버전과 requests 버전 정보 확인
3. 다른 Python 버전(3.11 또는 3.12)에서 테스트

---

*최종 업데이트: 2025-05-29*