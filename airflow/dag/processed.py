from airflow import DAG
from airflow.decorators import task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import numpy as np
from io import StringIO
import pytz
from datetime import datetime, timedelta
from airflow.sensors.external_task_sensor import ExternalTaskSensor

def get_execution_date_to_check(dt):
    # dt = 현재 DAG의 실행 날짜/시간.(airflow가 전달하는 값.)
    #이전 날의 14:00:00 실행을 확인하려고 함.
    target_dt = (dt - timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    print(f"Checking for execution date: {target_dt}")
    return target_dt

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 15, 00, 00, 0),  # UTC 기준 15:00
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='s3_data_preprocessing_and_upload',
    default_args=default_args,
    schedule_interval='00 15 * * *',  # 매일 UTC 1500 (한국 시간 00:00)에 실행
    catchup=False,
) as dag:
    
    wait_for_task = ExternalTaskSensor(
        task_id='wait_for_dag',
        external_dag_id='29cm_data_extract',
        allowed_states=['success'],
        mode='reschedule',
        timeout=3600,  # 1시간
        poke_interval=300,  # 5분
        execution_date_fn=get_execution_date_to_check,
        check_existence=True,
        queue='queue1'
    )

    @task(queue='queue1')
    def preprocess_data():
        today = datetime.now() - timedelta(days=1)
        today = today.strftime("%Y%m%d")
        print(today)

        bucket_name = 'team-hori-1-bucket'
        file_key = f'crawling/29cm_bestitem_{today}.csv'

        s3_hook = S3Hook(aws_conn_id='MyS3Conn')

        try:
            # S3에서 객체 가져오기
            response = s3_hook.get_key(file_key, bucket_name)
            csv_content = response.get()['Body'].read().decode('utf-8')

            # DataFrame 생성 및 전처리
            df = pd.read_csv(StringIO(csv_content))
            
            # 전처리 작업
            bag_only_mask = df['category1'].str.contains('가방')
            df.loc[bag_only_mask & df['category2'].notna(), 'category3'] = df.loc[bag_only_mask & df['category2'].notna(), 'category2']
            df.loc[bag_only_mask, 'category1'] = '아이템'
            df.loc[bag_only_mask, 'category2'] = '가방'
            
            bag_only_mask = df['category1'].str.contains('액세서리')
            df.loc[bag_only_mask, 'category1'] = '아이템'
            
            clothing_mask = df['category1'].str.contains('의류')
            df.loc[clothing_mask, 'category1'] = df.loc[clothing_mask, 'category2']
            df.loc[clothing_mask, 'category2'] = df.loc[clothing_mask, 'category3']
            df['category1'] = df['category1'].str.replace('^(여성|남성)', '', regex=True)

            overseas_brand_mask = df['category1'] == '해외브랜드'
            df.loc[overseas_brand_mask, ['category1', 'category2']] = df.loc[overseas_brand_mask, ['category2', 'category2']].values

            exclusive_mask = df['category1'] == 'EXCLUSIVE'
            df.loc[exclusive_mask, 'category1'] = df.loc[exclusive_mask, 'category2']

            mask_item = df['category1'].isin(['이너웨어', '홈웨어'])
            df.loc[mask_item, 'category3'] = df.loc[mask_item, 'category2']
            df.loc[mask_item, 'category2'] = df.loc[mask_item, 'category1']
            df.loc[mask_item, 'category1'] = '아이템'

            mask_bottom = df['category1'].isin(['바지', '스커트'])
            df.loc[mask_bottom, 'category3'] = df.loc[mask_bottom, 'category2']
            df.loc[mask_bottom, 'category2'] = df.loc[mask_bottom, 'category1']
            df.loc[mask_bottom, 'category1'] = '하의'

            mask_top = df['category1'].isin(['원피스', '점프수트', '액티브웨어', '아우터', '니트웨어', '셋업'])
            df.loc[mask_top, 'category3'] = df.loc[mask_top, 'category2']
            df.loc[mask_top, 'category2'] = df.loc[mask_top, 'category1']
            df.loc[mask_top, 'category1'] = '상의'

            df.dropna(subset=['category1'], inplace=True)
            df.loc[df['category2'] == df['category3'], 'category3'] = np.nan
            df['category2'] = df['category2'] + df['category3'].apply(lambda x: f"/{x}" if pd.notna(x) else "")
            df['category2'] = df['category2'].fillna(df['category1'])
            df['gender'] = df['gender'].replace({'men': 'm', 'women': 'w'})
            
            duplicated_product_names = df[df.duplicated(subset='product_name', keep=False)]['product_name']
            df.loc[df['product_name'].isin(duplicated_product_names), 'gender'] = 'unisex'
            df = df.drop_duplicates(subset='product_name', keep='first')


            # df2: 필요한 열만 선택
            df2 = df[['category1', 'category2', 'gender']].drop_duplicates(subset=['category1', 'category2', 'gender']).reset_index(drop=True)

            # df: 모든 열이 포함된 데이터프레임에서 category1, category3을 제외한 나머지 열 선택
            df_full = df.drop(columns=['category1', 'category3'])
            

            # df_full에서 category2 열의 이름을 category로 변경
            df_full = df_full.rename(columns={'category2': 'category'})
            
            df2_csv_buffer = StringIO()
            df2.to_csv(df2_csv_buffer, index=False)
            df_full_csv_buffer = StringIO()
            df_full.to_csv(df_full_csv_buffer, index=False)
            s3_hook = S3Hook(aws_conn_id='my_amazon_conn')
            s3_hook.load_string(df2_csv_buffer.getvalue(), key= f'model/file29/df2_{today}.csv', bucket_name='team-hori-1-bucket', replace=True)
            s3_hook.load_string(df_full_csv_buffer.getvalue(), key= f'model/full29_processed/df_full_{today}.csv', bucket_name='team-hori-1-bucket', replace=True)
            
            return "성공"
        except Exception as e:
            print(f"오류 발생: {e}")
            return "실패"
        
    S3_ETL_and_upload_S3 = preprocess_data()
    
    wait_for_task >> S3_ETL_and_upload_S3