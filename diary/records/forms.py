from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    new_tag = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder':'Добавить новый тег'
        })
    )
    class Meta:
        model = Record
        fields = ['title', 'content', 'tags']
    widgets = {
        'title': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введи заголовок',
        }),
        'content': forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Напишите запись...',
            'rows': 6
        }),
        'tags': forms.CheckboxSelectMultiple()
    }