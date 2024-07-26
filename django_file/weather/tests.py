import os
import psycopg2
from django.shortcuts import render


def test(request):
    return render(request, 'test.html')

# 환경 변수에서 Redshift 사용자 이름, 비밀번호 및 호스트를 가져옴
redshift_user = os.environ.get('REDSHIFT_USER', 'awsuser')
redshift_password = os.environ.get('REDSHIFT_PASSWORD', 'Hori1proj!')
redshift_host = os.environ.get('REDSHIFT_HOST', 'team-hori-1-redshift-cluster.cvkht4jvd430.ap-northeast-2.redshift.amazonaws.com')

print(f"Redshift 연결 정보: 사용자={redshift_user}, 호스트={redshift_host}")

# Redshift 연결
try:
    conn = psycopg2.connect(
        dbname='dev',
        user=redshift_user,
        password=redshift_password,
        host=redshift_host,
        port='5439'
    )
    print("Redshift에 성공적으로 연결되었습니다.")
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print("Redshift 연결 테스트 결과:", result)
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Redshift 연결 오류: {e}")
