from django.urls import path, include
from rest_framework_nested import routers
from .views import QuizViewSet, QuestionViewSet, ChoiceViewSet, StudentAnswerViewSet, GradeViewSet

# Base router
router = routers.DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')

# Nested routes for quizzes within modules
modules_router = routers.NestedDefaultRouter(router, r'quizzes', lookup='quiz')
modules_router.register(r'questions', QuestionViewSet, basename='quiz-questions')

# Nested routes for choices within questions
questions_router = routers.NestedDefaultRouter(modules_router, r'questions', lookup='question')
questions_router.register(r'choices', ChoiceViewSet, basename='question-choices')

# Student answers should not be nested, as they relate to both quizzes and questions
router.register(r'student-answers', StudentAnswerViewSet, basename='student-answer')
router.register(r'grades', GradeViewSet, basename='grade')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(modules_router.urls)),
    path('', include(questions_router.urls)),
]
