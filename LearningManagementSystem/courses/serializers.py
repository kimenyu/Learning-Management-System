from rest_framework import serializers
from .models import Course, Module, Content, Enrollment,ContentFile
from quizzes.serializers import QuizSerializer

# serializers.py
class ContentFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentFile
        fields = ['id', 'file', 'file_url', 'external_link', 'file_type', 'created_at']

    def get_file_url(self, obj):
        if obj.external_link:
            return obj.external_link
        if not obj.file:
            return None
        return obj.file.url

class ContentSerializer(serializers.ModelSerializer):
    files = ContentFileSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True, required=False),
        write_only=True,
        required=False
    )
    external_links = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )
    file_types = serializers.ListField(
        child=serializers.ChoiceField(choices=Content.MODULE_CONTENT_TYPE_CHOICES),
        write_only=True,
        required=False
    )

    class Meta:
        model = Content
        fields = [
            'id', 'module', 'title', 'description',
            'files', 'uploaded_files', 'external_links', 'file_types',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'module', 'created_at', 'updated_at']
        
    def validate(self, data):
        files = data.get('uploaded_files', [])
        links = data.get('external_links', [])
        file_types = data.get('file_types', [])
        
        total_items = len(files) + len(links)
        
        if total_items == 0 and file_types:
            raise serializers.ValidationError("Must provide files or links when specifying file_types")
        if file_types and total_items != len(file_types):
            raise serializers.ValidationError("Number of files and links combined must match number of file types")
        
        return data

    def create(self, validated_data):
        files = validated_data.pop('uploaded_files', [])
        links = validated_data.pop('external_links', [])
        file_types = validated_data.pop('file_types', [])

        content = Content.objects.create(**validated_data)
        
        # Process uploads
        for file, file_type in zip(files, file_types[:len(files)]):
            if file:
                ContentFile.objects.create(
                    content=content,
                    file=file,
                    file_type=file_type
                )
        
        # Process links
        link_types = file_types[len(files):] if file_types else []
        for link, file_type in zip(links, link_types):
            ContentFile.objects.create(
                content=content,
                external_link=link,
                file_type=file_type
            )

        return content


class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)


    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'description', 
            'contents', 'created_at', 'updated_at', 'quizzes'
        ]
        read_only_fields = ['id', 'course', 'created_at', 'updated_at', 'quizzes']



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
