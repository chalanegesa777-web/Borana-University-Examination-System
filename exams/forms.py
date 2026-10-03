from django import forms
from django.utils import timezone
from .models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ('title', 'course', 'description', 'instructions', 'start_at', 'end_at', 'duration_minutes', 'total_questions', 'max_marks', 'passing_mark', 'question_selection', 'randomize_questions', 'randomize_choices', 'result_visibility', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_questions': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_mark': forms.NumberInput(attrs={'class': 'form-control'}),
            'question_selection': forms.Select(attrs={'class': 'form-select'}),
            'result_visibility': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        duration = cleaned_data.get('duration_minutes')
        total_questions = cleaned_data.get('total_questions')
        passing_mark = cleaned_data.get('passing_mark')
        max_marks = cleaned_data.get('max_marks')
        if start_at and end_at and start_at >= end_at:
            raise forms.ValidationError('End date must be after start date.')
        if duration and duration <= 0:
            raise forms.ValidationError('Duration must be greater than zero.')
        if total_questions and total_questions <= 0:
            raise forms.ValidationError('Total questions must be greater than zero.')
        if max_marks and max_marks <= 0:
            raise forms.ValidationError('Max marks must be greater than zero.')
        if passing_mark is not None and max_marks is not None and passing_mark > max_marks:
            raise forms.ValidationError('Passing mark cannot exceed max marks.')
        return cleaned_data
