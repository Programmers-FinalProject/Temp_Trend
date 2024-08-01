from django.shortcuts import render
from weather.models import musinsaData
from weather.musinsa_forms import ProductFilterForm

def musinsa_list(request):
    form = ProductFilterForm(request.GET or None)
    products = []

    if form.is_valid():
        gender = form.cleaned_data.get('gender')
        category = form.cleaned_data.get('category')
        products = musinsaData.objects.using('redshift').filter(gender=gender, category=category).order_by('rank')

    return render(request, 'musinsa_list.html', {'form': form, 'products': products})
# 
