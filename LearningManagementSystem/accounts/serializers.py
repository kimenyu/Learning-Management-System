# from djoser.serializers import UserCreateSerializer
# from .models import User
# from rest_framework import serializers
# import uuid

# class CustomUserCreateSerializer(UserCreateSerializer):
#     id = serializers.UUIDField(default=uuid.uuid4, read_only=True)  # Ensure UUID is handled

#     class Meta(UserCreateSerializer.Meta):
#         model = User
#         fields = ('id', 'email', 'username', 'password', 'role')

#     def create(self, validated_data):
#         # Ensure that role and username are passed correctly if not handled by Djoser
#         username = validated_data.get('username')
#         role = validated_data.get('role', 'student')  # default role if not provided
#         user = User.objects.create_user(
#             username=username,
#             email=validated_data['email'],
#             password=validated_data['password'],
#             role=role
#         )
#         return user

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is not active")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'created_at']


# ✅ New: JWT payload customization
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add extra fields to JWT payload
        token['email'] = user.email
        token['role'] = user.role

        return token
