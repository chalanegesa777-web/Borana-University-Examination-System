from django.urls import path
from .views import reports_index_view

urlpatterns = [
    path('', reports_index_view, name='reports_index'),
]
