from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.utils.html import strip_tags

from accounts.models import User
from courses.models import Course
from questions.models import Question, QuestionChoice
from .models import Exam, ExamQuestion, Attempt, AttemptQuestion, Answer, AttemptEvent
from .forms import ExamForm


@login_required
def exam_list_view(request):
    if request.user.role == User.ROLE_STUDENT:
        exams = Exam.objects.filter(is_published=True).select_related('course', 'created_by')
    else:
        exams = Exam.objects.select_related('course', 'created_by').order_by('-created_at')
    q = request.GET.get('q')
    course_id = request.GET.get('course_id')
    if q:
        exams = exams.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if course_id:
        exams = exams.filter(course_id=course_id)
    paginator = Paginator(exams, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    courses = Course.objects.all()
    return render(request, 'exams/exam_list.html', {'page_obj': page_obj, 'q': q, 'course_id': course_id, 'courses': courses})


@login_required
def exam_create_view(request):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, 'Exam created.')
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form})


@login_required
def exam_detail_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.user.role == User.ROLE_STUDENT and not exam.is_published:
        return HttpResponseForbidden('This exam is not available yet.')
    return render(request, 'exams/exam_detail.html', {'exam': exam})


@login_required
def start_exam_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.user.role != User.ROLE_STUDENT:
        return HttpResponseForbidden('Only students can take exams.')
    if not exam.is_published:
        return HttpResponseForbidden('This exam is not published.')

    active_attempt = Attempt.objects.filter(user=request.user, exam=exam, status=Attempt.STATUS_IN_PROGRESS).first()
    if active_attempt:
        return redirect('take_exam', pk=active_attempt.id)

    existing_attempt = Attempt.objects.filter(user=request.user, exam=exam, status__in=[Attempt.STATUS_SUBMITTED, Attempt.STATUS_PASSED, Attempt.STATUS_FAILED]).first()
    if existing_attempt:
        messages.info(request, 'You already attempted this exam.')
        return redirect('attempt_result', pk=existing_attempt.id)

    questions = list(exam.questions.select_related('question').order_by('order').values_list('question_id', flat=True))
    if exam.question_selection == Exam.QUESTION_SELECTION_RANDOM:
        questions = list(questions)
        import random
        random.shuffle(questions)
    if exam.total_questions and exam.total_questions > 0:
        questions = questions[:exam.total_questions]

    with transaction.atomic():
        attempt = Attempt.objects.create(exam=exam, user=request.user, status=Attempt.STATUS_IN_PROGRESS)
        for index, qid in enumerate(questions, start=1):
            question = Question.objects.get(pk=qid)
            AttemptQuestion.objects.create(attempt=attempt, question=question, order=index)
            if not Answer.objects.filter(attempt=attempt, question=question).exists():
                Answer.objects.create(attempt=attempt, question=question)

    return redirect('take_exam', pk=attempt.id)


@login_required
def take_exam_view(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk)
    if attempt.user != request.user:
        return HttpResponseForbidden('Not allowed')
    if attempt.is_locked or attempt.status in [Attempt.STATUS_SUBMITTED, Attempt.STATUS_PASSED, Attempt.STATUS_FAILED]:
        return redirect('attempt_result', pk=attempt.id)

    exam = attempt.exam
    elapsed = timezone.now() - attempt.started_at
    duration_seconds = exam.duration_minutes * 60
    if elapsed.total_seconds() > duration_seconds:
        finalize_attempt(attempt)
        return redirect('attempt_result', pk=attempt.id)
    attempt_questions = list(attempt.attempt_questions.select_related('question').all())
    current_question = attempt_questions[0] if attempt_questions else None
    return render(request, 'exams/take_exam.html', {'attempt': attempt, 'exam': exam, 'attempt_questions': attempt_questions, 'current_question': current_question, 'remaining_seconds': max(0, duration_seconds - int(elapsed.total_seconds()))})


@login_required
def exam_auto_save_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    attempt = get_object_or_404(Attempt, pk=pk)
    if attempt.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    question_id = request.POST.get('question_id')
    choice_id = request.POST.get('choice_id')
    text_answer = request.POST.get('text_answer', '')
    marked_review = request.POST.get('marked_review') == 'true'

    if not question_id:
        return JsonResponse({'status': 'error', 'message': 'Missing question_id'}, status=400)

    attempt_question = attempt.attempt_questions.filter(question_id=question_id).first()
    if not attempt_question:
        return JsonResponse({'status': 'error', 'message': 'Question not found in attempt'}, status=404)

    attempt_question.is_marked_review = marked_review
    attempt_question.save(update_fields=['is_marked_review'])

    answer, _ = Answer.objects.get_or_create(attempt=attempt, question_id=question_id)
    if choice_id:
        try:
            answer.selected_choice_id = int(choice_id)
        except ValueError:
            answer.selected_choice_id = None
    else:
        answer.selected_choice_id = None
    answer.text_answer = text_answer
    answer.save()

    return JsonResponse({'status': 'saved', 'message': 'Answer saved successfully'})


@login_required
def submit_exam_view(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk)
    if attempt.user != request.user:
        return HttpResponseForbidden('Not allowed')
    if attempt.status in [Attempt.STATUS_SUBMITTED, Attempt.STATUS_PASSED, Attempt.STATUS_FAILED]:
        return redirect('attempt_result', pk=attempt.id)
    finalize_attempt(attempt)
    messages.success(request, 'Exam submitted successfully.')
    return redirect('attempt_result', pk=attempt.id)


@login_required
def attempt_result_view(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk)
    if attempt.user != request.user:
        return HttpResponseForbidden('Not allowed')
    return render(request, 'exams/result.html', {'attempt': attempt})


@login_required
def grade_attempts_view(request, pk):
    if request.user.role not in [User.ROLE_ADMIN, User.ROLE_INSTRUCTOR]:
        return HttpResponseForbidden('Unauthorized')
    attempt = get_object_or_404(Attempt, pk=pk)
    if request.user.role == User.ROLE_INSTRUCTOR and attempt.exam.created_by != request.user:
        return HttpResponseForbidden('Unauthorized')

    if request.method == 'POST':
        score = float(request.POST.get('score', 0))
        grade = request.POST.get('grade', 'N/A')
        attempt.score = score
        attempt.grade = grade
        attempt.status = Attempt.STATUS_PASSED if score >= attempt.exam.passing_mark else Attempt.STATUS_FAILED
        attempt.percentage = (score / attempt.exam.max_marks) * 100 if attempt.exam.max_marks else 0
        attempt.submitted_at = attempt.submitted_at or timezone.now()
        attempt.is_locked = True
        attempt.save()
        messages.success(request, 'Attempt graded successfully.')
        return redirect('exam_list')

    return render(request, 'exams/grade_form.html', {'attempt': attempt})


def finalize_attempt(attempt):
    if attempt.status in [Attempt.STATUS_SUBMITTED, Attempt.STATUS_PASSED, Attempt.STATUS_FAILED]:
        return

    score = 0
    for answer in attempt.answers.all():
        if answer.selected_choice and answer.selected_choice.is_correct:
            score += 1
        elif answer.text_answer:
            score += 1
    max_marks = attempt.exam.max_marks or 1
    attempt.score = score
    attempt.percentage = (score / max_marks) * 100 if max_marks else 0
    attempt.status = Attempt.STATUS_PASSED if score >= attempt.exam.passing_mark else Attempt.STATUS_FAILED
    attempt.grade = 'A' if attempt.percentage >= 80 else 'B' if attempt.percentage >= 60 else 'C' if attempt.percentage >= 50 else 'F'
    attempt.submitted_at = timezone.now()
    attempt.is_locked = True
    attempt.save()

    AttemptEvent.objects.create(attempt=attempt, event_type=AttemptEvent.EVENT_SUBMISSION, details='Submitted exam')
    return attempt


@login_required
def exam_results_view(request):
    if request.user.role == User.ROLE_STUDENT:
        attempts = Attempt.objects.filter(user=request.user).select_related('exam')
    else:
        attempts = Attempt.objects.select_related('exam', 'user').all()
    return render(request, 'exams/results.html', {'attempts': attempts})
