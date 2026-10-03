from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Avg, Sum
from django.utils import timezone
from django.http import HttpResponseForbidden

from .forms import UserRegistrationForm
from .models import User
from courses.models import Course
from exams.models import Exam, Attempt
from questions.models import Question


@login_required
def dashboard_view(request):
    user = request.user
    statistics = {}

    if user.role == User.ROLE_ADMIN:
        statistics['students'] = User.objects.filter(role=User.ROLE_STUDENT).count()
        statistics['instructors'] = User.objects.filter(role=User.ROLE_INSTRUCTOR).count()
        statistics['users'] = User.objects.count()
        statistics['courses'] = Course.objects.count()
        statistics['exams'] = Exam.objects.count()
        statistics['published_exams'] = Exam.objects.filter(is_published=True).count()
        statistics['upcoming_exams'] = Exam.objects.filter(start_at__gt=timezone.now()).count()
        statistics['completed_exams'] = Exam.objects.filter(end_at__lt=timezone.now()).count()
        statistics['recent_activities'] = Attempt.objects.select_related('exam', 'user').order_by('-submitted_at')[:8]
        statistics['exam_stats'] = Exam.objects.annotate(questions_count=Count('questions')).order_by('-created_at')[:5]
        statistics['user_stats'] = User.objects.values('role').annotate(count=Count('id'))
        statistics['activity_counts'] = Attempt.objects.filter(submitted_at__isnull=False).count()
    elif user.role == User.ROLE_INSTRUCTOR:
        my_courses = Course.objects.filter(created_by=user)
        my_exams = Exam.objects.filter(created_by=user)
        statistics['my_courses'] = my_courses.count()
        statistics['my_exams'] = my_exams.count()
        statistics['upcoming_exams'] = my_exams.filter(start_at__gt=timezone.now()).count()
        statistics['active_exams'] = my_exams.filter(start_at__lte=timezone.now(), end_at__gte=timezone.now()).count()
        statistics['completed_exams'] = my_exams.filter(end_at__lt=timezone.now()).count()
        statistics['enrolled_students'] = sum(course.students.count() for course in my_courses)
        statistics['pending_grading'] = Attempt.objects.filter(exam__created_by=user, status='submitted').count()
        attempts = Attempt.objects.filter(exam__created_by=user)
        statistics['average_exam_performance'] = attempts.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        statistics['pass_fail'] = {'passed': attempts.filter(status='passed').count(), 'failed': attempts.filter(status='failed').count()}
        statistics['recent_activities'] = attempts.order_by('-submitted_at')[:6]
    else:
        attempts = Attempt.objects.filter(user=user)
        statistics['available_exams'] = Exam.objects.filter(is_published=True, start_at__lte=timezone.now(), end_at__gte=timezone.now()).exclude(id__in=Attempt.objects.filter(user=user, status__in=['in_progress','submitted']).values_list('exam_id', flat=True)).count()
        statistics['upcoming_exams'] = Exam.objects.filter(is_published=True, start_at__gt=timezone.now()).count()
        statistics['active_exams'] = Exam.objects.filter(is_published=True, start_at__lte=timezone.now(), end_at__gte=timezone.now()).count()
        statistics['completed_exams'] = attempts.filter(status='submitted').count()
        statistics['recent_results'] = attempts.filter(submitted_at__isnull=False).order_by('-submitted_at')[:5]
        statistics['average_score'] = attempts.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        statistics['exam_history'] = attempts.select_related('exam').order_by('-started_at')[:10]
        statistics['notifications'] = []

    return render(request, 'dashboard.html', {'user': user, 'stats': statistics})


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def user_list_view(request):
    if request.user.role != User.ROLE_ADMIN:
        return HttpResponseForbidden('You do not have access to this page.')
    users = User.objects.all().order_by('username')
    search = request.GET.get('q')
    role = request.GET.get('role')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search))
    if role:
        users = users.filter(role=role)
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/user_list.html', {'page_obj': page_obj, 'search': search, 'role': role})
