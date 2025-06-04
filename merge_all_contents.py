#!/usr/bin/env python
"""
모든 일별 수집 파일을 하나로 병합하는 스크립트
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리
project_root = r"C:\Users\xxxwj\Documents\GitHub\news_crawler_ver_4"
temp_dir = os.path.join(project_root, "data", "temp_daily")
output_dir = os.path.join(project_root, "data", "news_data")

def merge_all_contents(keyword, start_date, end_date):
    """특정 키워드의 모든 일별 컨텐츠를 병합"""
    
    all_contents = []
    date_count = {}
    
    # temp_daily 디렉토리의 모든 파일 확인
    for filename in os.listdir(temp_dir):
        if filename.startswith(f"contents_{keyword}_") and filename.endswith(".json"):
            file_path = os.path.join(temp_dir, filename)
            
            # 파일에서 날짜 추출
            date_str = filename.replace(f"contents_{keyword}_", "").replace(".json", "")
            
            try:
                # 날짜가 범위 내에 있는지 확인
                if start_date <= date_str <= end_date:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents = json.load(f)
                        
                    # 각 컨텐츠에 수집 날짜 추가
                    for content in contents:
                        content['collection_date'] = date_str
                        all_contents.append(content)
                    
                    date_count[date_str] = len(contents)
                    logger.info(f"  {date_str}: {len(contents)}개 로드")
                    
            except Exception as e:
                logger.warning(f"  파일 {filename} 로드 실패: {e}")
    
    # 날짜순으로 정렬
    all_contents.sort(key=lambda x: x.get('collection_date', ''))
    
    # 전체 병합 파일 저장
    timestamp = datetime.now().strftime('%H%M%S')
    output_filename = f"merged_all_contents_{keyword}_{start_date}_{end_date}_{timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_contents, f, ensure_ascii=False, indent=2)
    
    logger.info("병합 완료:")
    logger.info(f"  총 {len(all_contents)}개 기사")
    logger.info(f"  저장 위치: {output_path}")
    
    logger.info("날짜별 분포:")
    for date in sorted(date_count.keys()):
        logger.info(f"  {date}: {date_count[date]}개")
    
    return output_path, len(all_contents)

def main():
    logger.info("=== 전체 일별 수집 파일 병합 ===")
    
    # 방산 키워드 병합
    logger.info("방산 키워드 병합 중...")
    merge_all_contents("방산", "20250520", "20250603")
    
    logger.info("="*50)
    
    # 원전 키워드도 있다면 병합
    if any(f.startswith("contents_원전_") for f in os.listdir(temp_dir)):
        logger.info("원전 키워드 병합 중...")
        merge_all_contents("원전", "20250520", "20250529")
    
    logger.info("="*50)
    
    # 조선 키워드도 있다면 병합
    if any(f.startswith("contents_조선_") for f in os.listdir(temp_dir)):
        logger.info("조선 키워드 병합 중...")
        merge_all_contents("조선", "20250525", "20250529")

if __name__ == "__main__":
    main()
