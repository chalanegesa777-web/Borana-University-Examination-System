from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from questions.models import Question


class Exam(models.Model):
    QUESTION_SELECTION_RANDOM = 'random'
    QUESTION_SELECTION_MANUAL = 'manual'
    SELECTION_OPTIONS = [
        (QUESTION_SELECTION_RANDOM, 'Random'),
        (QUESTION_SELECTION_MANUAL, 'Manual'),
    ]

    RESULT_VISIBLE_ALWAYS = 'always'
    RESULT_VISIBLE_AFTER_SUBMISSION = 'after_submission'
    RESULT_VISIBILITY_CHOICES = [
        (RESULT_VISIBLE_ALWAYS, 'Always'),
        (RESULT_VISIBLE_AFTER_SUBMISSION, 'After submission'),
    ]

    title = models.CharField(max_length=200)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='exams')
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    total_questions = models.PositiveIntegerField(default=1)
    max_marks = models.PositiveIntegerField(default=100)
    passing_mark = models.PositiveIntegerField(default=50)
    question_selection = models.CharField(max_length=20, choices=SELECTION_OPTIONS, default=QUESTION_SELECTION_RANDOM)
    randomize_questions = models.BooleanField(default=True)
    randomize_choices = models.BooleanField(default=True)
    result_visibility = models.CharField(max_length=30, choices=RESULT_VISIBILITY_CHOICES, default=RESULT_VISIBLE_AFTER_SUBMISSION)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_at']

    def __str__(self):
        return self.title

    @property
    def status_label(self):
        from django.utils import timezone
        now = timezone.now()
        if self.is_published and self.start_at <= now <= self.end_at:
            return 'Active'
        if self.is_published and now < self.start_at:
            return 'Upcoming'
        if self.is_published and now > self.end_at:
            return 'Completed'
        return 'Draft'


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE, related_name='exam_questions')
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.exam.title} - {self.question_id}'


class Attempt(models.Model):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_SUBMITTED = 'submitted'
    STATUS_PASSED = 'passed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_PASSED, 'Passed'),
        (STATUS_FAILED, 'Failed'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    grade = models.CharField(max_length=10, default='N/A')
    is_locked = models.BooleanField(default=False)
    session_key = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} - {self.exam}'


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='attempt_questions')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    is_marked_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.attempt_id} - {self.question_id}'


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    selected_choice = models.ForeignKey('questions.QuestionChoice', on_delete=models.SET_NULL, blank=True, null=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'{self.attempt.user} - {self.question_id}'


class AttemptEvent(models.Model):
    EVENT_TAB_SWITCH = 'tab_switch'
    EVENT_FULLSCREEN = 'fullscreen'
    EVENT_SUBMISSION = 'submission'
    EVENT_ACTIVITY = 'activity'
    EVENT_CHOICES = [
        (EVENT_TAB_SWITCH, 'Tab switch'),
        (EVENT_FULLSCREEN, 'Fullscreen'),
        (EVENT_SUBMISSION, 'Submission'),
        (EVENT_ACTIVITY, 'Activity'),
    ]

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.event_type} - {self.attempt_id}'
