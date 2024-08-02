#!/bin/bash

# S3 버킷 이름
BUCKET_NAME="team-hori-dags"

# 로컬 디렉터리
LOCAL_DAGS_PATH="/home/ubuntu/apps/airflow/dags"

# 로그 파일 경로
LOG_FILE="/home/ubuntu/s3_sync/s3_sync.log"

# 현재 날짜와 시간을 로그 파일에 기록
echo "Sync started at $(TZ='Asia/Seoul' date)" >> "$LOG_FILE"

# S3에서 로컬로 파일 동기화
# S3 버킷의 $S3_PATH 경로와 로컬의 $LOCAL_DAGS_PATH 경로를 동기화
# 동기화 과정에서 발생하는 출력과 에러 메시지를 $LOG_FILE에 기록
# 파이캐시 폴더권한때문에 계속 오류가 발생해서 무시하는 코드 추가
aws s3 sync s3://team-hori-dags /home/ubuntu/apps/airflow/dags --delete --exclude "__pycache__/*" --exclude "*/__pycache__/*" >> "$LOG_FILE" 2>&1

# 동기화가 성공했는지 실패했는지 여부를 로그 파일에 기록
if [ $? -eq 0 ]; then
    echo "Sync completed successfully at $(TZ='Asia/Seoul' date)" >> "$LOG_FILE"
else
    echo "Sync failed at $(TZ='Asia/Seoul' date)" >> "$LOG_FILE"
fi