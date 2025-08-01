from rest_framework import permissions
from .models import Enrollment
from quizzes.models import Quiz

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'role', None) == 'instructor'


class IsEnrolledOrInstructor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'instructor':
            return obj.instructor == request.user
        return Enrollment.objects.filter(
            student=request.user,
            course=obj,
            is_active=True
        ).exists()

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'instructor'

class IsEnrolledStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student' and Quiz.objects.filter(module__course__enrollments__student=request.user).exists()
