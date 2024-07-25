import os
import psycopg2
from django.shortcuts import render


def test(request):
    return render(request, 'test.html')
# Redshift 연결 정보
redshift_user = os.environ.get('REDSHIFT_USER', 'admin')
redshift_password = os.environ.get('REDSHIFT_PASSWORD', 'Qwer1234')
redshift_host = os.environ.get('REDSHIFT_HOST', 'default-workgroup.590183894915.ap-northeast-2.redshift-serverless.amazonaws.com')

# Redshift 연결
try:
    conn = psycopg2.connect(
        dbname='dev',
        user=redshift_user,
        password=redshift_password,
        host=redshift_host,
        port='5439'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print("Redshift 연결 테스트 결과:", result)
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Redshift 연결 오류: {e}")
