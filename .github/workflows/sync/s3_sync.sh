#!/bin/bash

# S3 버킷, 경로 설정
S3_BUCKET="your-s3-bucket-name"
S3_PATH="dags/"
LOCAL_DAGS_PATH="/path/to/airflow/dags"

# 로그 파일 경로 설정
LOG_FILE="/home/ubuntu/s3_sync.log"

# 현재 날짜와 시간을 로그 파일에 기록
echo "Sync started at $(date)" >> "$LOG_FILE"

# S3에서 로컬로 파일 동기화
# S3 버킷의 $S3_PATH 경로와 로컬의 $LOCAL_DAGS_PATH 경로를 동기화합니다.
# 동기화 과정에서 발생하는 출력과 에러 메시지를 $LOG_FILE에 기록합니다.
aws s3 sync "s3://$S3_BUCKET/$S3_PATH" "$LOCAL_DAGS_PATH" >> "$LOG_FILE" 2>&1

# 동기화 결과 기록
# 동기화가 성공했는지 실패했는지 여부를 로그 파일에 기록합니다.
if [ $? -eq 0 ]; then
    echo "Sync completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Sync failed at $(date)" >> "$LOG_FILE"
fi

# 로그 파일 크기 제한 (선택 사항, 예: 1MB 이상이면 잘라내기)
# 로그 파일의 크기가 1MB를 초과하면 마지막 1MB만 남기고 잘라냅니다.
MAX_LOG_SIZE=$((1024 * 1024))  # 1MB
if [ $(stat -c%s "$LOG_FILE") -ge $MAX_LOG_SIZE ]; then
    tail -c $MAX_LOG_SIZE "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi
