from django import forms
from .models import Event, Category

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name','description','date','time','location','category','image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']
