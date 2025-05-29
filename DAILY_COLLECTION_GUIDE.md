# 날짜별 뉴스 수집 방법

현재 "일별 기사 수 제한" 설정이 제대로 작동하지 않는 문제가 있습니다. 이는 일반 크롤러가 날짜 정보를 고려하지 않고 전체 URL을 수집하기 때문입니다.

## 해결 방법

### 방법 1: 날짜별 수집 모드 사용 (권장)

날짜별로 균등하게 뉴스를 수집하려면 `--daily` 옵션을 사용하세요:

```bash
# 명령줄에서 실행
python main.py "원전" --period 1w --daily --daily-limit 10 --extract-content

# 또는 배치 파일 사용
run_daily_collection.bat
```

이 명령은:
- 일주일 동안 매일 최대 10개씩 뉴스를 수집합니다
- 7일 × 10개 = 최대 70개의 뉴스가 수집됩니다

### 방법 2: 대화형 모드에서 날짜별 수집

대화형 모드는 현재 일반 크롤러만 사용하므로, 날짜별 수집이 필요하면 명령줄을 사용해야 합니다.

### 명령줄 옵션 설명

```bash
python main.py [검색어] --daily [옵션들]
```

주요 옵션:
- `--daily`: 날짜별 수집 모드 활성화 (필수)
- `--daily-limit N`: 각 날짜별 최대 수집 개수 (기본값: 10)
- `--period 1w`: 수집 기간 (1w=1주일, 1m=1개월 등)
- `--extract-content`: 본문도 함께 추출
- `--content-limit N`: 전체 본문 추출 개수 제한
- `--extraction-mode`: 추출 방식
  - `sequential`: 순차적 (기본값)
  - `even_distribution`: 날짜별 균등 분배
  - `recent_first`: 최신순
  - `random`: 무작위

### 예시

1. **일주일간 매일 10개씩 수집 (본문 포함)**
   ```bash
   python main.py "원전" --period 1w --daily --daily-limit 10 --extract-content
   ```

2. **한 달간 매일 5개씩 수집**
   ```bash
   python main.py "원전" --period 1m --daily --daily-limit 5 --extract-content --content-limit 100
   ```

3. **특정 기간 날짜별 수집**
   ```bash
   python main.py "원전" --period custom --start-date 20250201 --end-date 20250207 --daily --daily-limit 15
   ```

## 결과 파일

날짜별 수집 모드에서는 다음과 같이 파일이 생성됩니다:

- `data/temp_daily/[query]_[date]_urls.json`: 일별 URL 목록
- `data/temp_daily/[query]_[date]_contents.json`: 일별 본문 데이터
- `data/news_data/[query]_[timestamp]_merged.json`: 병합된 최종 결과

## 현재 알려진 문제

1. 대화형 모드에서 날짜별 수집 설정이 작동하지 않음
2. 일반 크롤러는 날짜 정보를 고려하지 않음
3. 병합 기능이 부분적으로만 작동

## 권장 사항

- 날짜별 균등 수집이 필요하면 `--daily` 옵션을 사용하세요
- 대화형 모드는 단순 테스트용으로만 사용하세요
- 본문 추출 시 지연 시간을 충분히 두세요

---
*이 문제는 v4.2.1에서 수정 예정입니다.*