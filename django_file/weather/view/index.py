from django.shortcuts import render
from weather.models import musinsaData


def weather_view(request):

    selected_gender = request.GET.get('gender')
    musinsaLists = musinsaData.objects.using('redshift').filter(gender = selected_gender)
    musinsaLists.order_by('rank')

    context = {
        'musinsa_lists': musinsaLists,
    }

    return render(request, 'index.html', context)