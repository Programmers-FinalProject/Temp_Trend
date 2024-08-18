import boto3

region = 'ap-northeast-2'
ec2_instances = ['i-0600ecc91bbd08996', 'i-04a44debe7fa16f5c', 'i-0208e8cbb3159e23e']

# RDS 인스턴스
rds_instance = 'hori-1-airflow-metadb'
    
# Redshift 클러스터
redshift_cluster = 'team-hori-1-redshift-cluster'

ec2 = boto3.client('ec2', region_name=region)
rds = boto3.client('rds', region_name=region)
redshift_client = boto3.client('redshift', region_name=region)
ssm = boto3.client('ssm', region_name=region)  # SSM 클라이언트 추가

def lambda_handler(event, context):
    # EC2 인스턴스 상태 확인 및 시작
    ec2_response = ec2.describe_instances(InstanceIds=ec2_instances)
    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            ec2_status = instance['State']['Name']
            instance_id = instance['InstanceId']
            instance_name = None
            
            # 인스턴스의 태그에서 'Name'을 검색
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
            
            if ec2_status == 'stopped':
                ec2.start_instances(InstanceIds=[instance_id])
                print('Started EC2 instance: ' + str(instance_name) + ' (' + instance_id + ')')
            else:
                print('EC2 instance ' + str(instance_name) + ' (' + instance_id + ') is already running or in a different state:', ec2_status)
                
                # 실행할 명령어
                script_command = """
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
                aws s3 sync s3://team-hori-dags /home/ubuntu/apps/airflow/dags --delete --exclude "__pycache__/*" --exclude "*/__pycache__/*" >> "$LOG_FILE" 2>&1
                
                # 동기화가 성공했는지 실패했는지 여부를 로그 파일에 기록
                if [ $? -eq 0 ]; then
                    echo "Sync completed successfully at $(TZ='Asia/Seoul' date)" >> "$LOG_FILE"
                else
                    echo "Sync failed at $(TZ='Asia/Seoul' date)" >> "$LOG_FILE"
                fi
                """
            
                for instance_id in ec2_instances:
                    send_ssm_command(instance_id, script_command)
            
                return {
                    'statusCode': 200,
                    'body': 'Commands sent to EC2 instances successfully.'
                }
    
    return {
        'statusCode': 200,
        'body': 'EC2 instances started successfully.'
    }
    
def send_ssm_command(instance_id, command):
    ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",  # AWS에서 제공하는 기본 문서
        Parameters={'commands': [command]}
    )
