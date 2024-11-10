from django.contrib.auth import authenticate
from requests import Response
from rest_framework.exceptions import ValidationError

from avtorizate.models import User, VerificationCode
from rest_framework import serializers
from django.utils import timezone
import random
from avtorizate.utils import send_verification_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4, required=False)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()

        if not user:
            raise serializers.ValidationError("Пользователь не найден.")

        if 'code' in data and data['code']:
            code = data['code']
            verification = VerificationCode.objects.filter(user=user, code=code, is_used=False).first()

            if not verification or (timezone.now() - verification.created_at).seconds > 300:
                raise serializers.ValidationError("Неверный или просроченный код.")

            verification.is_used = True
            verification.save()
            user.is_active = True
            user.is_email_verified = True
            user.save()
        else:
            user.delete()
            raise serializers.ValidationError("Код подтверждения не введен. Аккаунт был удален.")

        return data

    def create(self, validated_data):
        return validated_data


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)
    new_password = serializers.CharField(min_length=1)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError("Пользователь с таким email не найден.")

        code = data['code']
        verification = VerificationCode.objects.filter(user=user, code=code, is_used=False).first()

        if not verification or (timezone.now() - verification.created_at).seconds > 300:
            raise serializers.ValidationError("Неверный или просроченный код.")

        verification.is_used = True
        verification.save()

        user.set_password(data['new_password'])
        user.save()

        return data

    def create(self, validated_data):

        return validated_data


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        code = str(random.randint(1000, 9999))
        VerificationCode.objects.create(user=user, code=code)
        send_verification_email(user.email, code)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
