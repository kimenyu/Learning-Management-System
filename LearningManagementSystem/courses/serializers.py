from rest_framework import serializers
from .models import Course, Module, Content, Enrollment


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'id', 'module', 'content_type', 'content_file', 
            'title', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'module', 'created_at', 'updated_at']


class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'description',
            'contents', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'course', 'created_at', 'updated_at']



class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor_email = serializers.EmailField(source='instructor.email', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'instructor_email',
            'modules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'instructor', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_email = serializers.EmailField(source='student.email', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_email', 'course', 'course_title',
            'enrolled_at', 'last_accessed', 'is_active'
        ]
        read_only_fields = [
            'id', 'student', 'enrolled_at', 'last_accessed'
        ]

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, data):
        # Check if enrollment already exists
        if self.context['request'].method == 'POST':
            if Enrollment.objects.filter(
                student=self.context['request'].user,
                course=data['course']
            ).exists():
                raise serializers.ValidationError(
                    "You are already enrolled in this course."
                )
        return data