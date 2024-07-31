from django.shortcuts import render
from weather.models import musinsaData
from weather.musinsa_forms import genderFilterForm, CategoryForm

def musinsa_list(request):
    genderForm = genderFilterForm(request.GET)
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