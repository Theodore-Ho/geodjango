from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'last_login', 'is_superuser', 'is_staff', 'date_joined']


class Login(serializers.Serializer):
    username = serializers.CharField(
        required=True
    )
    password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

    def validate(self, data):
        return data


class Logout(serializers.Serializer):
    class Meta:
        model = User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        write_only=True,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate(self, data):
        # validate password and confirm password are equal
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Password is not same")

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    new_password_confirmation = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate(self, data):
        # validate new password and new confirm password are equal
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError("Password not match!")

        return data


class UpdateProfileSerializer(serializers.Serializer):
    firstname = serializers.CharField(
        required=False
    )

    lastname = serializers.CharField(
        required=False
    )

    email = serializers.CharField(
        required=False
    )

    def to_internal_value(self, data):
        return data
