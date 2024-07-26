from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
# variable로 수정
dbid = Variable.get("conn_id")
def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id=dbid)
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn

# sql문을 배열로 넘기면 for문을 통해 돌림
def sql_execute_to_redshift(sqlList):
    conn = get_Redshift_connection()
    cur = conn.cursor()
    # list가 아닌 str으로 보냈을경우 처리
    if isinstance(sqlList, str) :
        sqlList = [sqlList]

    try:
        cur.execute("BEGIN;")   
        for sql in sqlList :
            cur.execute(sql)
        cur.execute("COMMIT;")
        print("done")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        cur.execute("ROLLBACK;")
    conn.close()
# str 받아서 처리
def sql_selecter(sql):
    conn = get_Redshift_connection()
    try:
        df = pd.read_sql_query(sql, conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def redshift_engine():
    hook = PostgresHook(postgres_conn_id=dbid)
    
    # SQLAlchemy 엔진 생성
    conn_str = hook.get_uri()
    
    # SQLAlchemy 엔진 반환
    return create_engine(conn_str)