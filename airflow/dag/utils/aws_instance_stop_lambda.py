import boto3
region = 'ap-northeast-2'
ec2_instances = ['i-0600ecc91bbd08996', 'i-04a44debe7fa16f5c', 'i-0208e8cbb3159e23e']

# RDS 인스턴스
rds_instance = 'hori-1-airflow-metadb'
    
# Redshift 클러스터
redshift_cluster = 'team-hori-1-redshift-cluster'

ec2 = boto3.client('ec2', region_name=region)
 # RDS 클라이언트 생성
rds = boto3.client('rds', region_name='ap-northeast-2')

redshift_client = boto3.client('redshift',region_name=region)

def lambda_handler(event, context):
    # EC2 인스턴스 상태 확인 및 중지
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
            
            if ec2_status == 'running':
                ec2.stop_instances(InstanceIds=[instance_id])
                print('Stopped EC2 instance: ' + str(instance_name) + ' (' + instance_id + ')')
            else:
                print('EC2 instance ' + str(instance_name) + ' (' + instance_id + ') is already stopped or in a different state:', ec2_status)
    
    # RDS 인스턴스 상태 확인 및 중지
    try:
        db = rds.describe_db_instances(DBInstanceIdentifier=rds_instance)
        response = db['DBInstances']
        
        for instance in response:
            rds_status = instance['DBInstanceStatus']
            if rds_status == 'available':
                rds.stop_db_instance(DBInstanceIdentifier=rds_instance)
                print(f'Stopped RDS instance: {rds_instance}')
            else:
                print('RDS instance is already stopped or in a different state:', rds_status)
    except Exception as e:
        print(f'Error while stopping RDS instance: {str(e)}')
        
    # Redshift 클러스터 상태 확인 및 일시 중지
    try:
        redshift_response = redshift_client.describe_clusters(ClusterIdentifier=redshift_cluster)
        redshift_status = redshift_response['Clusters'][0]['ClusterStatus']
        
        if redshift_status == 'available':
            redshift_client.pause_cluster(ClusterIdentifier=redshift_cluster)
            print(f'Paused Redshift cluster: {redshift_cluster}')
        else:
            print('Redshift cluster is already paused or in a different state:', redshift_status)
    except Exception as e:
        print(f'Error while pausing Redshift cluster: {str(e)}')

    return {
        'statusCode': 200,
        'body': 'Function executed successfully.'
    }
    
    