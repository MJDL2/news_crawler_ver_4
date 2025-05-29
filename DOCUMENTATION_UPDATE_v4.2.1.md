# v4.2.1 문서화 업데이트 완료

## 수행된 작업

### 1. issues 디렉토리 재생성
- `docs/issues/` 디렉토리 생성
- `docs/issues/README.md` - 이슈 디렉토리 안내 문서
- `docs/issues/DAILY_COLLECTION_ISSUE_20250529.md` - 날짜별 수집 문제 분석

### 2. 기존 문서 업데이트

#### README.md
- 버전 번호: v4.2.0 → v4.2.1
- 프로젝트 구조에 issues 디렉토리 추가
- 버전 히스토리에 v4.2.1 추가

#### docs/ARCHITECTURE.md
- 문서 디렉토리 구조에 issues 폴더 추가

#### docs/USER_GUIDE.md
- 섹션 9 "알려진 이슈" 추가
- issues 디렉토리로의 링크 제공
- 각 이슈별 상세 문서 연결

#### docs/PROGRESS.md
- 현재 상태를 v4.2.1로 업데이트
- 날짜별 수집 문제 분석 항목 추가

## 문서 구조

```
docs/
├── issues/                        # 이슈 추적 디렉토리 (NEW)
│   ├── README.md                  # 이슈 디렉토리 안내
│   └── DAILY_COLLECTION_ISSUE_20250529.md  # 날짜별 수집 문제 분석
├── ARCHITECTURE.md                # 아키텍처 설계 (수정됨)
├── DEVELOPMENT.md                 # 개발 가이드
├── PROGRESS.md                    # 진행 상황 (수정됨)
├── USER_GUIDE.md                  # 사용자 가이드 (수정됨)
├── 403_ERROR_GUIDE.md             # 403 오류 해결
├── PYTHON313_FIX.md               # Python 3.13 호환성
├── CHANGELOG.md                   # 변경 이력
└── TEST_CHECKLIST.md              # 테스트 체크리스트
```

## 주요 내용

### 날짜별 수집 문제 분석
1. **통계 표시 오류**: CLI에서 최근 5일만 표시 (실제로는 8일 모두 수집됨)
2. **URL/본문 불일치**: 일별 10개 설정 시 URL 20개 수집
3. **병합 파일 미생성**: content_limit=0으로 병합 스킵

### 문서화 원칙
- 체계적인 이슈 관리를 위한 별도 디렉토리 운영
- 각 이슈별 상세 분석 문서 작성
- 기존 문서들과의 연계성 확보

## GitHub 커밋 준비 완료

모든 문서가 업데이트되었으며, GitHub에 푸시할 준비가 완료되었습니다.