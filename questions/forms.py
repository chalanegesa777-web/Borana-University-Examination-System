from django import forms
from .models import Question, QuestionChoice


class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ('text', 'is_correct', 'order')
        widgets = {'text': forms.TextInput(attrs={'class': 'form-control'}), 'order': forms.NumberInput(attrs={'class': 'form-control'})}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'category', 'topic', 'difficulty', 'marks', 'status')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
