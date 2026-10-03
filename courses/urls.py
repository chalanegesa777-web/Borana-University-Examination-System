from django.urls import path
from .views import course_list_view, course_create_view, course_detail_view, enroll_course_view

urlpatterns = [
    path('', course_list_view, name='course_list'),
    path('new/', course_create_view, name='course_create'),
    path('<int:pk>/', course_detail_view, name='course_detail'),
    path('<int:pk>/enroll/', enroll_course_view, name='enroll_course'),
]
