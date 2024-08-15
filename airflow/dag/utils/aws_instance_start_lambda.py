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
    
    # RDS 인스턴스 상태 확인 및 시작
    try:
        db = rds.describe_db_instances(DBInstanceIdentifier=rds_instance)
        response = db['DBInstances']
        
        for instance in response:
            rds_status = instance['DBInstanceStatus']
            if rds_status == 'stopped':
                rds.start_db_instance(DBInstanceIdentifier=rds_instance)
                print(f'Started RDS instance: {rds_instance}')
            else:
                print('RDS instance is already running or in a different state:', rds_status)
    except Exception as e:
        print(f'Error while starting RDS instance: {str(e)}')
        
    # Redshift 클러스터 상태 확인 및 시작
    try:
        redshift_response = redshift_client.describe_clusters(ClusterIdentifier=redshift_cluster)
        redshift_status = redshift_response['Clusters'][0]['ClusterStatus']
        
        if redshift_status == 'paused':
            redshift_client.resume_cluster(ClusterIdentifier=redshift_cluster)
            print(f'Resumed Redshift cluster: {redshift_cluster}')
        else:
            print('Redshift cluster is already running or in a different state:', redshift_status)
    except Exception as e:
        print(f'Error while resuming Redshift cluster: {str(e)}')

    return {
        'statusCode': 200,
        'body': 'Function executed successfully.'
    }
