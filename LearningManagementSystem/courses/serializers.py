from rest_framework import serializers
from .models import Course, Module, Content, Enrollment,ContentFile


# serializers.py
class ContentFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentFile
        fields = ['id', 'file', 'file_url', 'file_type', 'created_at']

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None


class ContentSerializer(serializers.ModelSerializer):
    files = ContentFileSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
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
            'files', 'uploaded_files', 'file_types',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'module', 'created_at', 'updated_at']

    def validate(self, data):
        files = data.get('uploaded_files', [])
        file_types = data.get('file_types', [])

        if files and not file_types:
            raise serializers.ValidationError("Must provide file_types when uploading files")
        if file_types and not files:
            raise serializers.ValidationError("Must provide files when specifying file_types")
        if len(files) != len(file_types):
            raise serializers.ValidationError("Number of files must match number of file types")

        return data

    def create(self, validated_data):
        files = validated_data.pop('uploaded_files', [])
        file_types = validated_data.pop('file_types', [])

        content = Content.objects.create(**validated_data)

        for file, file_type in zip(files, file_types):
            ContentFile.objects.create(
                content=content,
                file=file,
                file_type=file_type
            )

        return content


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
