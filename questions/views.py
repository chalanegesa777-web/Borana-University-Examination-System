from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from accounts.models import User
from .models import Question, QuestionChoice
from .forms import QuestionForm, QuestionChoiceForm


@login_required
def question_list_view(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    questions = Question.objects.select_related('created_by').all().order_by('-created_at')
    search = request.GET.get('q')
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    if search:
        questions = questions.filter(Q(text__icontains=search) | Q(category__icontains=search) | Q(topic__icontains=search))
    if category:
        questions = questions.filter(category__icontains=category)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    paginator = Paginator(questions, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'questions/question_list.html', {'page_obj': page_obj, 'q': search, 'category': category, 'difficulty': difficulty})


@login_required
def question_create_view(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            messages.success(request, 'Question created successfully.')
            return redirect('question_list')
    else:
        form = QuestionForm()
    return render(request, 'questions/question_form.html', {'form': form})


@login_required
def question_edit_view(request, pk):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated.')
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'questions/question_form.html', {'form': form, 'question': question})


@login_required
def question_delete_view(request, pk):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('question_list')


@login_required
def question_detail_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    choices = question.choices.all()
    return render(request, 'questions/question_detail.html', {'question': question, 'choices': choices})
