from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.models import User
from .models import AuditLog


@login_required
def audit_log_list_view(request):
    if request.user.role != User.ROLE_ADMIN:
        return HttpResponseForbidden('Unauthorized')
    logs = AuditLog.objects.select_related('user').all().order_by('-created_at')
    return render(request, 'audit/list.html', {'logs': logs})
