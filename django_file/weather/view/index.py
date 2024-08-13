from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from weather.models import musinsaData
from weather.view import learningmodel
import requests



def weather_view(request):
    selected_gender = request.GET.get('gender')
    musinsaLists = musinsaData.objects.using('redshift').filter(gender=selected_gender).order_by('rank')
    response = requests.get('https://34.64.100.195/learn') #https://34.64.100.195/learn(배포) http://127.0.0.1:8000/learn(로컬)
    if response.status_code == 200:
        data = response.json()
        recommended_products = data['recommended_products']
        # 이후로 recommended_products를 사용한 로직 처리
        dic = {}
        for i in recommended_products:
            category2 = i['category2']  # 셔츠/블라우스 이런거
            category1 = i['category'] #상의,하의,신발,아이템
            for j in musinsaLists:
                if category2 == j.category:
                    if category1 not in dic:
                        dic[category1] = []
                    dic[category1].append(j)
        return render(request, 'index.html', {'products': dic})
    else:
        return HttpResponse("Failed to retrieve data", status=500)
    
    

    

'''
dic = { "상의" : {~~~}, {~~~},
       "하의" : {~~~},{~~~},}'''