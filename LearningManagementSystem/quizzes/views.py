from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Quiz, Question, Choice, StudentAnswer, Grade
from .serializers import QuizSerializer, QuestionSerializer, ChoiceSerializer, StudentAnswerSerializer, GradeSerializer
from courses.permissions import IsInstructor, IsEnrolledStudent

# Quiz ViewSet (Only instructors can create quizzes, students can only view their enrolled course quizzes)
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'instructor':
            return Quiz.objects.filter(module__course__instructor=user)
        elif user.role == 'student':
            return Quiz.objects.filter(module__course__enrollments__student=user)
        return Quiz.objects.none()

# Question ViewSet (Only instructors can create/edit questions, students can only view them)
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'instructor':
            return Question.objects.filter(quiz__module__course__instructor=user)
        elif user.role == 'student':
            return Question.objects.filter(quiz__module__course__enrollments__student=user)
        return Question.objects.none()

# Choice ViewSet (Only instructors can add choices, students can only view them)
class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        question_pk = self.kwargs.get('question_pk')
        
        # Debug logging
        print(f"ChoiceViewSet - Getting choices for question_pk: {question_pk}")
        
        # First, filter by question_pk to ensure we only get choices for the current question
        base_queryset = Choice.objects.filter(question_id=question_pk)
        
        # Then apply role-based filtering
        if user.role == 'instructor':
            queryset = base_queryset.filter(question__quiz__module__course__instructor=user)
        elif user.role == 'student':
            queryset = base_queryset.filter(question__quiz__module__course__enrollments__student=user)
        else:
            queryset = Choice.objects.none()
        
        # Debug logging
        print(f"ChoiceViewSet - Found {queryset.count()} choices for question {question_pk}")
        
        return queryset

    def perform_create(self, serializer):
        question_pk = self.kwargs.get('question_pk')
        question = Question.objects.get(pk=question_pk)
        # Debug logging
        print(f"ChoiceViewSet - Creating choice for question: {question_pk}")
        serializer.save(question=question)



# Student Answer ViewSet (Students can submit answers, instructors can view them)
class StudentAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return StudentAnswer.objects.filter(student=user)
        elif user.role == 'instructor':
            return StudentAnswer.objects.filter(question__quiz__module__course__instructor=user)
        return StudentAnswer.objects.none()

# Grade ViewSet (Students can view their grades, instructors can assign grades)
class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Grade.objects.filter(student=user)
        elif user.role == 'instructor':
            return Grade.objects.filter(quiz__module__course__instructor=user)
        return Grade.objects.none()