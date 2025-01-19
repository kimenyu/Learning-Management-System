from djoser.serializers import UserCreateSerializer
from .models import User
from rest_framework import serializers
import uuid

class CustomUserCreateSerializer(UserCreateSerializer):
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)  # Ensure UUID is handled

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'role')

    def create(self, validated_data):
        # Ensure that role and username are passed correctly if not handled by Djoser
        username = validated_data.get('username')
        role = validated_data.get('role', 'customer')  # default role if not provided
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        return user