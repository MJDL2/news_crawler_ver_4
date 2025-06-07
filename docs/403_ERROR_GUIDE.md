# 403 Forbidden 오류 해결 가이드 (v4.2.7)

## 오류 원인

네이버가 봇/크롤러로 인식하여 요청을 차단하는 경우 발생합니다.

## v4.2.x 자동 대응 기능

v4.2.0부터 추가되고 v4.2.7까지 안정화된 기능들:

- **세션 풀 관리**: 차단된 세션을 자동으로 교체
- **점진적 백오프**: 오류 발생 시 대기 시간 자동 증가
- **세션 재생성**: 반복 오류 시 새 세션 생성

## 즉시 해결 방법

### 1. 안전 모드 실행 (가장 권장)

```bash
run_safe_mode.bat
```

이 방법은:
- 지연 시간 3.5초 설정
- 최대 페이지 5개로 제한
- 본문 추출 지연 4.0초

### 2. 통합 설정 파일 수정

`unified_config.json` 파일에서 다음 설정 조정:

```json
{
  "crawling": {
    "delay_between_requests": 3.0
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

### 3. 명령줄에서 직접 지연 시간 설정

```bash
python main.py "검색어" --delay 3.0 --content-delay 4.0 --pages 5
```

### 4. 프록시 사용

v4.2.0에서 프록시 지원이 개선되었습니다:

```bash
# 환경 변수 설정
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port

# 또는 배치 파일 사용
run_with_proxy.bat
```

### 5. 소량 분할 수집

```bash
# 작은 단위로 나누어 수집
python main.py "검색어" --max-urls 30 --delay 3.0
```

## 고급 해결 방법

### 세션 풀 상태 모니터링

v4.2.0에서는 세션 상태를 자동으로 관리하지만, 필요시 수동 조정 가능:

```json
{
  "advanced": {
    "session_management": {
      "max_sessions_pool": 5,  // 더 많은 세션 사용
      "session_refresh_interval": 600  // 10분마다 세션 갱신
    }
  }
}
```

### 점진적 백오프 설정

```json
{
  "advanced": {
    "anti_403": {
      "enable_progressive_backoff": true,
      "max_backoff_seconds": 300  // 최대 5분 대기
    }
  }
}
```

## 권장 수집 전략

### 1. 시간대별 수집
- 새벽 시간대 (2-6시) 활용
- 점심 시간대 (12-14시) 피하기

### 2. 검색어별 간격
- 검색어마다 5-10분 간격 두기
- 동일 검색어 반복 수집 시 더 긴 간격

### 3. 단계적 수집
```bash
# 1단계: URL만 수집
python main.py "검색어" --max-urls 50

# 2단계: 본문 추출 (소량)
python main.py "검색어" --extract-content --content-limit 20 --delay 4.0
```

## 문제별 대응책

### 즉시 차단되는 경우
1. `run_safe_mode.bat` 실행
2. VPN 사용 고려
3. 다른 시간대에 재시도

### 간헐적 차단
1. `delay_between_requests` 값 증가
2. `max_sessions_pool` 값 증가
3. 세션 풀 기능 활용

### 완전 차단
1. IP 변경 (VPN/프록시)
2. 24시간 후 재시도
3. 다른 검색어로 테스트

## 예방책

### 기본 설정 권장값
```json
{
  "crawling": {
    "delay_between_requests": 2.5,
    "max_urls_per_search": 50
  }
}
```

### 안전 모드 설정
```json
{
  "crawling": {
    "delay_between_requests": 4.0,
    "max_urls_per_search": 30
  }
}
```

## 응급 처치

403 오류 발생 시 즉시 실행할 명령어:

```bash
# Windows
run_anti_403.bat

# 또는 직접 실행
python main.py "테스트" --delay 4.0 --content-delay 4.5 --max-urls 10
```

## v4.2.7 추가 개선사항

✅ **설정 파일 통합** (v4.2.6)
- 모든 403 관련 설정이 `unified_config.json` 하나로 통합
- 설정 관리 단순화 및 일관성 확보

✅ **코드 품질 개선** (v4.2.7)
- 미사용 import 정리로 성능 최적화
- PEP 8 스타일 적용으로 코드 안정성 향상

---

**중요**: v4.2.7의 안정화된 대응 기능을 활용하되, 적절한 사용량을 유지하여 서비스에 부담을 주지 않도록 주의하세요.

**최종 업데이트**: 2025-06-07 (v4.2.7)
