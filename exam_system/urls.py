from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('questions/', include('questions.urls')),
    path('exams/', include('exams.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('audit/', include('audit.urls')),
    path('dashboard/', include('accounts.urls')),
]
