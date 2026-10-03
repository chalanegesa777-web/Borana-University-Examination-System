from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.models import User


@login_required
def reports_index_view(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    return render(request, 'reports/index.html', {'user': request.user})
