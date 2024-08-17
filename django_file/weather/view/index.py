from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from weather.models import musinsaData
import requests
from django.shortcuts import redirect
from django.db.models import Q
import pandas as pd
import boto3
from io import StringIO


def weather_view(request):

        return render(request, 'index.html')
    
def musinsajjj(request):
    # S3 클라이언트 생성
    s3 = boto3.client('s3')
    bucket_name = 'team-hori-1-bucket'
    prefix = 'model/full29_processed/df_full_'  # 파일 경로의 공통 부분
    # S3 버킷에서 지정된 prefix로 시작하는 파일 리스트 가져오기
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    # 파일 리스트 중에서 가장 최근 파일 찾기
    files = [content['Key'] for content in response.get('Contents', [])]
    recent_file_key = max(files, key=lambda x: x.split('_')[-1].split('.')[0])
    # 가장 최근 파일 읽기
    response = s3.get_object(Bucket=bucket_name, Key=recent_file_key)
    content = response['Body'].read().decode('utf-8')
    # DataFrame으로 변환
    s3_df = pd.read_csv(StringIO(content))
    
    # 세션에서 추천된 제품 가져오기
    learn_data = request.session.get('learn_data')
    if not learn_data:
        return JsonResponse({'error': 'No learn data in session'}, status=400)
    
    recommended_products = learn_data.get('recommended_products')
    if not recommended_products:
        return JsonResponse({'error': 'No recommended products found'}, status=400)
    
    dic = {}
    for i in recommended_products:
        category2 = i['category2']  # 셔츠/블라우스 등
        category1 = i['category']   # 상의, 하의, 신발, 아이템 등
        product_gender = i['gender']  # 'm', 'w', 'unisex' 등
        # Redshift에서 데이터 필터링
        if product_gender :
            musinsa_lists = musinsaData.objects.using('redshift').all().values()
            musinsa_df = pd.DataFrame(list(musinsa_lists))
            combined_df = pd.concat([musinsa_df, s3_df], ignore_index=True)
            filtered_df = combined_df[
            (combined_df['gender'] == product_gender) &
            (combined_df['category'] == category2)
            ]
            filtered_df = filtered_df.sort_values(by='rank')
        for _, j in filtered_df.iterrows():
                if category1 not in dic:
                    dic[category1] = []
                dic[category1].append(j.to_dict())  # 행을 딕셔너리로 변환하여 추가
    return JsonResponse({'products': dic})

    

'''
dic = { "상의" : {~~~}, {~~~},
       "하의" : {~~~},{~~~},}'''