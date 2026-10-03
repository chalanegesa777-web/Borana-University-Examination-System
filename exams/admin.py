from django.contrib import admin
from .models import Exam, ExamQuestion, Attempt, AttemptQuestion, Answer, AttemptEvent

admin.site.register(Exam)
admin.site.register(ExamQuestion)
admin.site.register(Attempt)
admin.site.register(AttemptQuestion)
admin.site.register(Answer)
admin.site.register(AttemptEvent)
