from django.shortcuts import render
from weather.models import musinsaData, weatherCategorizeData
from weather.musinsa_forms import GenderFilterForm, CategoryForm, WeatherInfoForm

def musinsa_list(request):
    genderForm = GenderFilterForm(request.GET)
    categoryForm = CategoryForm(request.GET)
    products = musinsaData.objects.using('redshift').all()

    if genderForm.is_valid() and categoryForm.is_valid():
        gender = genderForm.cleaned_data.get('gender')
        selected_category = categoryForm.cleaned_data.get('category')
        
        if gender:
            products = products.filter(gender=gender)
        if selected_category:
            products = products.filter(category=selected_category)
            
    products = products.order_by('rank')
    
    return render(request, 'musinsa_list.html', {'g_form': genderForm, 'c_form': categoryForm, 'products': products})

def categorize(requset):
    weatherInfoForm = WeatherInfoForm(requset.GET)
    products = []
    if weatherInfoForm.is_valid():
        weatherInfo = weatherInfoForm.cleaned_data.get('weather_info')
        if weatherInfo:
            categorys = weatherCategorizeData.objects.using('redshift').filter(weather_info = weatherInfo).values_list('category', flat=True)
            for category in categorys:
                product = musinsaData.objects.using('redshift').filter(category = category)
                product = product.order_by('rank')
                products += product

    return render(requset, 'musinsa_categorize.html' ,{'form' : weatherInfoForm, 'products': products})
