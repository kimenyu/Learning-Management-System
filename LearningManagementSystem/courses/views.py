from rest_framework import viewsets, status, filters
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from .models import Course, Module, Content, Enrollment
from .serializers import (
    CourseSerializer, ModuleSerializer,
    ContentSerializer, EnrollmentSerializer
)
from .permissions import (
    IsInstructorOrReadOnly, 
    IsEnrolledOrInstructor,
    IsInstructor
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .permissions import IsInstructor, IsInstructorOrReadOnly

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().select_related('instructor')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]  # Default for other actions

    def get_permissions(self):
        if self.action == 'enroll':
            return [IsAuthenticated()]  # ✅ Students need to be authenticated
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructor()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == 'instructor':
            return queryset.filter(instructor=self.request.user)
        return queryset

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        serializer = EnrollmentSerializer(
            data={'course': course.id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Module.objects.filter(
            course_id=self.kwargs['course_pk']
        ).prefetch_related('contents')

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        if course.instructor != self.request.user:
            raise PermissionError("Only the course instructor can add modules.")
        serializer.save(course=course)


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Content.objects.filter(
            module_id=self.kwargs['module_pk'],
            module__course_id=self.kwargs['course_pk']
        ).prefetch_related('files')

    def perform_create(self, serializer):
        module = get_object_or_404(
        Module,
        pk=self.kwargs['module_pk'],
        course_id=self.kwargs['course_pk']
        )

        # ✅ Correct check: access course through the actual module instance
        if module.course.instructor != self.request.user:
            raise PermissionError("Only the course instructor can add contents.")

        serializer.save(module=module)



    def perform_destroy(self, instance):
        # Delete all related files first (optional)
        for file in instance.files.all():
            file.delete()
        instance.delete()



class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['enrolled_at', 'last_accessed']

    def get_queryset(self):
        if self.request.user.role == 'instructor':
            return Enrollment.objects.filter(
                course__instructor=self.request.user
            ).select_related('student', 'course')
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)