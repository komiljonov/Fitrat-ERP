from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import CustomUser
from ..account.permission import PhoneAuthBackend
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('phone', 'password', 'role', 'full_name', 'balance', 'photo')
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'ADMINISTRATOR'},
        }

    def create(self, validated_data):
        # Extract and hash the password
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user


# class ConfirmationCodeSerializer(serializers.Serializer):
#     phone = serializers.EmailField()
#     confirmation_code = serializers.IntegerField()
#
#
# class PasswordResetRequestSerializer(serializers.Serializer):
#     phone = serializers.EmailField()
#
#
# class PasswordResetLoginSerializer(serializers.Serializer):
#     new_password = serializers.CharField()

class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            backend = PhoneAuthBackend()
            user = backend.authenticate(
                request=self.context.get('request'),
                phone=phone,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.",
                    code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "Must include 'phone' and 'password'.",
                code="authorization"
            )

        attrs['user'] = user
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15, required=False)
    password = serializers.CharField(max_length=128, write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['phone', 'full_name',"first_name","last_name", 'password', 'role', "photo", "date_of_birth", ]

    def validate(self, attrs):
        user = self.instance  # Get the user instance
        if 'password' in attrs:
            user.set_password(attrs['password'])
            user.save()
        return attrs


class UserListSerializer(ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', "full_name","fist_name","last_name",'role', "photo", "filial", ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo).data
        return rep


class UserSerializer(ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = CustomUser
        fields = (
            "id", "full_name","fist_name","last_name", 'phone', "role", "photo", "filial", "balance", "ball",
            "enter", 'leave','date_of_birth', 'created_at',
            'updated_at')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo).data
        return rep
