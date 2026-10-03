from django.urls import path
from .views import notification_list_view

urlpatterns = [
    path('', notification_list_view, name='notification_list'),
]
