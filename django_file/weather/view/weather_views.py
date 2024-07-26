from django.shortcuts import render
from datetime import datetime
from weather.models import WeatherData

def we_data_test(request):
    test = WeatherData.objects.using('redshift').all()
    context = {'test' : test}
    return render(request, 'wedatatest.html', context)