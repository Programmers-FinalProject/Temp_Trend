from utils import shop_29cm_utils
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 1),
    'retries': 1,
}

dag = DAG(
    '29cm_data_extract',
    default_args=default_args,
    description='29cm Website Data Extract',
    schedule_interval='0 14 * * *',  # 매일 UTC 14시 실행 (한국시간 23시)
)

categories = [
    {"name": "여성액세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[4]/a'},
    {"name": "여성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[2]/a'},
    {"name": "여성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a'},
    {"name": "여성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[3]/a'},
    {"name": "남성악세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[8]/a'},
    {"name": "남성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[6]/a'},
    {"name": "남성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[5]/a'},
    {"name": "남성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[7]/a'},
]

category_eng = {
    '여성액세서리':'female_acc',
    '여성가방':'female_bags',
    '여성의류':'female_clothes',
    '여성신발':'female_shoes',
    '남성악세서리':'male_acc',
    '남성가방':'male_bags',
    '남성의류':'male_clothes',
    '남성신발':'male_shoes',
}

for category in categories:
    category_name = category_eng[category["name"]]
    
    # 태스크 정의
    fetch_links_task = PythonOperator(
        task_id=f'fetch_product_links_{category_name}',
        python_callable=shop_29cm_utils.fetch_product_links,
        op_kwargs={'category': category},
        queue='queue1',
        dag=dag,
    )

    fetch_info_task = PythonOperator(
        task_id=f'fetch_product_info_{category_name}',
        python_callable=shop_29cm_utils.fetch_product_info,
        op_kwargs={'product_data': "{{ task_instance.xcom_pull(task_ids='fetch_product_links_" + category_name + "') }}"},
        queue='queue1',
        dag=dag,
    )

    save_task = PythonOperator(
        task_id=f'result_save_to_dir_{category_name}',
        python_callable=shop_29cm_utils.result_save_to_dir,
        op_kwargs={'product_data': "{{ task_instance.xcom_pull(task_ids='fetch_product_info_" + category_name + "') }}"},
        queue='queue1',
        dag=dag,
    )

    # 태스크 종속성 설정
    fetch_links_task >> fetch_info_task >> save_task