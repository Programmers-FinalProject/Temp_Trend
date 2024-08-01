# myapp/forms.py
from django import forms

class ProductFilterForm(forms.Form):
    GENDER_CHOICES = [
        ('w', '여성'),
        ('m', '남성'),
        ('unisex', 'Unisex')
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    category = forms.CharField(max_length=100, required=True)
