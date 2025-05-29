# 403 Forbidden 오류 해결 가이드

## 오류 원인

네이버가 봇/크롤러로 인식하여 요청을 차단하는 경우 발생합니다.

## 해결 방법

### 1. 설정 파일 수정 (즉시 적용 가능)

`crawler_config.json` 파일을 생성하거나 수정하여 지연 시간을 늘립니다:

```json
{
  "crawling": {
    "delay_between_requests": 3.0  // 기본값 1.0 → 3.0초로 증가
  }
}
```

### 2. 수동으로 지연 시간 설정

명령줄에서 직접 지연 시간을 지정:

```bash
python main.py "검색어" --delay 3.0 --content-delay 3.5
```

### 3. 프록시 사용 (고급)

현재 버전에서는 프록시를 직접 지원하지 않지만, 시스템 프록시를 설정하면 사용 가능합니다.

#### Windows에서 프록시 설정:
```bash
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port
python main.py "검색어"
```

### 4. VPN 사용

IP 차단이 의심되는 경우 VPN을 사용하여 IP를 변경합니다.

### 5. 소량 수집

한 번에 많은 페이지를 수집하지 말고 소량씩 나누어 수집:

```bash
# 2페이지씩만 수집
python main.py "검색어" --pages 2

# 10개 URL만 수집
python main.py "검색어" --max-urls 10
```

### 6. 시간대 변경

네이버 트래픽이 적은 시간대(새벽)에 수집을 시도합니다.

## 개선된 설정 예시

다음 설정으로 403 오류를 최소화할 수 있습니다:

```json
{
  "network": {
    "timeout": 30,
    "retries": 5,
    "backoff_factor": 3
  },
  "crawling": {
    "delay_between_requests": 3.5,
    "max_urls_per_search": 50
  }
}
```

## 추가 팁

1. **날짜별 수집 사용**: 긴 기간의 데이터는 날짜별로 나누어 수집
   ```bash
   python main.py -i  # 대화형 모드에서 날짜별 분할 수집 선택
   ```

2. **재시도 간격 두기**: 403 오류 발생 시 5-10분 후 재시도

3. **User-Agent 로테이션**: 이미 구현되어 있으므로 자동으로 처리됨

## 근본적 해결책

지속적으로 403 오류가 발생한다면:

1. Selenium을 사용한 브라우저 자동화 방식으로 전환
2. 네이버 공식 API 사용 검토
3. 프록시 풀 서비스 활용

---

*참고: 크롤링 시 네이버 서비스 이용약관을 준수하고, 과도한 요청으로 서버에 부담을 주지 않도록 주의하세요.*