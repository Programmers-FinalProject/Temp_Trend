from utils import shop_29cm_utils
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

category = {"name": "여성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a'}

product_data = shop_29cm_utils.fetch_product_links(category)

product_data = shop_29cm_utils.fetch_product_info(product_data)

shop_29cm_utils.result_save_to_dir(product_data)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 1),
    'retries': 1,
}

dag = DAG(
    '29cm_female_acc_data_extract',
    default_args=default_args,
    description='29cm Website Data Extract - Female Accessories',
    schedule_interval='0 14 * * *',  # 매일 UTC 14시에 실행 (한국시간 23시)
)

with dag:
    # 태스크 정의
    fetch_links_task = PythonOperator(
        task_id='fetch_product_links',
        python_callable=shop_29cm_utils.fetch_product_links,
        provide_context=True,
        queue = 'queue1'
    )

    fetch_info_task = PythonOperator(
        task_id='fetch_product_info',
        python_callable=shop_29cm_utils.fetch_product_info,
        op_kwargs={'product_data': "{{ task_instance.xcom_pull(task_ids='fetch_product_links') }}"},
        queue = 'queue1'
    )

    save_task = PythonOperator(
        task_id='result_save_to_dir',
        python_callable=shop_29cm_utils.result_save_to_dir,
        op_kwargs={'product_data': "{{ task_instance.xcom_pull(task_ids='fetch_product_info') }}"},
        queue = 'queue1'
    )

    # 태스크 종속성 설정
    fetch_links_task >> fetch_info_task >> save_task