from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    if request.method == 'POST':
        for notification in notifications:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
    return render(request, 'notifications/list.html', {'notifications': notifications})
