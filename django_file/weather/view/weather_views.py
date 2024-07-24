from django.shortcuts import render
from datetime import datetime
from weather.models import WeatherData

def we_data_test(request):
    test = WeatherData.objects.filter(nx='33')
    context = {'test' : test}
    return render(request, 'wedatatest.html', context)