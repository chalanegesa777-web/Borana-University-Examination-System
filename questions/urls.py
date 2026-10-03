from django.urls import path
from .views import question_list_view, question_create_view, question_edit_view, question_delete_view, question_detail_view

urlpatterns = [
    path('', question_list_view, name='question_list'),
    path('new/', question_create_view, name='question_create'),
    path('<int:pk>/', question_detail_view, name='question_detail'),
    path('<int:pk>/edit/', question_edit_view, name='question_edit'),
    path('<int:pk>/delete/', question_delete_view, name='question_delete'),
]
