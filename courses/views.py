from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Course
from accounts.models import User


@login_required
def course_list_view(request):
    courses = Course.objects.select_related('created_by').all().order_by('-created_at')
    q = request.GET.get('q')
    if q:
        courses = courses.filter(Q(title__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q))
    paginator = Paginator(courses, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'courses/list.html', {'page_obj': page_obj, 'q': q})


@login_required
def course_create_view(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        if not title or not code:
            messages.error(request, 'Please provide title and code.')
            return render(request, 'courses/form.html', {'title': title, 'code': code, 'description': description})
        course = Course.objects.create(title=title, code=code, description=description, created_by=request.user)
        messages.success(request, 'Course created successfully.')
        return redirect('course_list')
    return render(request, 'courses/form.html')


@login_required
def course_detail_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user.role == User.ROLE_STUDENT and request.user not in course.students.all():
        return HttpResponseForbidden('You are not enrolled in this course.')
    return render(request, 'courses/detail.html', {'course': course})


@login_required
def enroll_course_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user.role != User.ROLE_STUDENT:
        messages.info(request, 'Only students can enroll in a course.')
        return redirect('course_list')
    course.students.add(request.user)
    messages.success(request, 'You enrolled successfully.')
    return redirect('course_list')
