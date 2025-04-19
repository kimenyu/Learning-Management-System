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
class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'student', 'question', 'selected_choice', 'text_answer', 'submitted_at']
        extra_kwargs = {
            'student': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


# Grade Serializer
class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'quiz', 'score', 'submitted_at']