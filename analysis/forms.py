# analysis/forms.py
from django import forms

class LinkForm(forms.Form):
    link = forms.URLField(label='Введите ссылку на Reddit или YouTube', max_length=200)
