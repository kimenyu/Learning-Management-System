from rest_framework import viewsets, status, filters
from rest_framework.parsers import MultiPartParser, FileUploadParser  # Add this import
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
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().select_related('instructor')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'instructor__email']
    ordering_fields = ['created_at', 'title']

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
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

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
    parser_classes = viewsets.ModelViewSet.parser_classes + [
        MultiPartParser, FileUploadParser
    ]

    def get_queryset(self):
        return Content.objects.filter(
            module_id=self.kwargs['module_pk'],
            module__course_id=self.kwargs['course_pk']
        )

    def perform_create(self, serializer):
        module = get_object_or_404(
            Module,
            pk=self.kwargs['module_pk'],
            course_id=self.kwargs['course_pk']
        )
        if module.course.instructor != self.request.user:
            raise PermissionError("Only the course instructor can add content.")
        serializer.save(module=module)

    def perform_destroy(self, instance):
        # Delete the associated file before deleting the Content object
        if instance.content_file:
            instance.content_file.delete(save=False)
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