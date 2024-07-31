from django import forms
from weather.models import musinsaData

class genderFilterForm(forms.Form):
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