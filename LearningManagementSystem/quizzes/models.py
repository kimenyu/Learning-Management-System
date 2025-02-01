from django.db import models
from accounts.models import User
from courses.models import Module
import uuid

# Quiz Model
class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE, 
        related_name='quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Question Model (Supports MCQ & Text Input)
class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('text', 'Text Input')  # Supports Open-Ended Answers
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    question = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quiz.title} - {self.question[:20]}"


# Choice Model (For Multiple Choice Questions)
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.question[:20]} - {self.text}"


# Student Answer Model (Handles MCQ & Text Answers)
class StudentAnswer(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_choice = models.ForeignKey(
        Choice, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='selected_by'
    )  # Used for MCQs

    text_answer = models.TextField(blank=True, null=True)  # Used for Open-Ended Questions
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.student.username} for {self.question.question[:20]}"


# Grade Model
class Grade(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='grades')
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')
