from django import forms
from weather.models import musinsaData
from weather.models import weatherCategorizeData

class GenderFilterForm(forms.Form):
    GENDER_CHOICES = [
        ('w', '여성'),
        ('m', '남성'),
        ('unisex', 'Unisex')
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)

class CategoryForm(forms.Form):
    category = forms.ChoiceField(choices=[], label="Category", required=False)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = self.get_category_choices()

    def get_category_choices(self):
        categories = musinsaData.objects.using('redshift').values_list('category', flat=True).distinct()
        return [(category, category) for category in categories]
    
class WeatherInfoForm(forms.Form):
    weather_info = forms.ChoiceField(choices=[], label="weather_info", required=False)

    def __init__(self, *args, **kwargs):
        super(WeatherInfoForm, self).__init__(*args, **kwargs)
        self.fields['weather_info'].choices = self.get_category_choices()

    def get_category_choices(self):
        weatherInfos = weatherCategorizeData.objects.using('redshift').values_list('weather_info', flat=True)
        distinctWeatherInfos = sorted(set(weatherInfos))
        return [(weatherInfo, weatherInfo) for weatherInfo in distinctWeatherInfos]