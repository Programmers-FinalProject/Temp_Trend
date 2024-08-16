from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from weather.models import musinsaData
import requests
from django.shortcuts import redirect



def weather_view(request):

        return render(request, 'index.html')
    
def musinsajjj(request):
    # 세션에서 성별 선택 가져오기
    selected_gender = request.session.get('selectedGender')
    
    if not selected_gender:
        return JsonResponse({'error': 'Gender not selected'}, status=400)
    
    # Redshift에서 데이터 필터링
    musinsaLists = musinsaData.objects.using('redshift').filter(gender=selected_gender).order_by('rank').values()
    
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
        for j in musinsaLists:
                    if category2 == j["category"]:
                        if category1 not in dic:
                            dic[category1] = []
                        dic[category1].append(j)
    return JsonResponse({'products': dic})

    

'''
dic = { "상의" : {~~~}, {~~~},
       "하의" : {~~~},{~~~},}'''