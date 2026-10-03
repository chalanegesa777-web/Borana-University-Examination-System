from django.urls import path
from .views import exam_list_view, exam_create_view, exam_detail_view, start_exam_view, take_exam_view, exam_auto_save_view, submit_exam_view, attempt_result_view, grade_attempts_view, exam_results_view

urlpatterns = [
    path('', exam_list_view, name='exam_list'),
    path('new/', exam_create_view, name='exam_create'),
    path('<int:pk>/', exam_detail_view, name='exam_detail'),
    path('<int:pk>/start/', start_exam_view, name='start_exam'),
    path('attempt/<int:pk>/', take_exam_view, name='take_exam'),
    path('attempt/<int:pk>/autosave/', exam_auto_save_view, name='exam_auto_save'),
    path('attempt/<int:pk>/submit/', submit_exam_view, name='submit_exam'),
    path('attempt/<int:pk>/result/', attempt_result_view, name='attempt_result'),
    path('attempt/<int:pk>/grade/', grade_attempts_view, name='grade_attempt'),
    path('results/', exam_results_view, name='exam_results'),
]
