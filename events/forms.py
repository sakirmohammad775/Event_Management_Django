from django import forms
from .models import Event, Category

# ----------------------------
# Event Form
# ----------------------------
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'image', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border rounded px-2 py-1'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'border rounded px-2 py-1'}),
            'description': forms.Textarea(attrs={'class': 'border rounded px-2 py-1', 'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'border rounded px-2 py-1'}),
            'location': forms.TextInput(attrs={'class': 'border rounded px-2 py-1'}),
            'category': forms.Select(attrs={'class': 'border rounded px-2 py-1'}),
            'image': forms.FileInput(attrs={'class': 'border rounded px-2 py-1'}),
        }

# ----------------------------
# Category Form
# ----------------------------
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded px-2 py-1'}),
            'description': forms.Textarea(attrs={'class': 'border rounded px-2 py-1', 'rows': 3}),
        }
