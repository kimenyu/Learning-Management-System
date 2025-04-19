from rest_framework import serializers
from .models import Quiz, Question, Choice, StudentAnswer, Grade
from accounts.models import User

# Choice Serializer (For Multiple Choice Questions)
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

# Question Serializer (Handles MCQ & Text Questions)
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question', 'question_type', 'order', 'choices']

# Quiz Serializer (Includes Nested Questions & Choices)
class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'module', 'created_at', 'questions']

# Student Answer Serializer
from rest_framework import serializers
from .models import StudentAnswer, Question, Choice
from accounts.models import User

class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.SerializerMethodField()
    selected_choice_text = serializers.SerializerMethodField()
    student_email = serializers.SerializerMethodField()

    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'student', 'question', 'selected_choice', 'text_answer',
            'question_text', 'selected_choice_text', 'student_email'
        ]
        read_only_fields = ['student']  # ✅ tell DRF not to require this field in POST

    def get_question_text(self, obj):
        return obj.question.question if obj.question else None

    def get_selected_choice_text(self, obj):
        return obj.selected_choice.text if obj.selected_choice else None

    def get_student_email(self, obj):
        return obj.student.email if obj.student else None




# Grade Serializer
class GradeSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'quiz', 'quiz_title', 'score']
