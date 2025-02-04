from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import CustomUser
from ..account.permission import PhoneAuthBackend
from ..finances.compensation.models import Compensation, Bonus
from ..finances.compensation.serializers import CompensationSerializer, BonusSerializer
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = (
            "full_name", "first_name", "last_name", "phone", "role","password","salary",
            "photo", "filial", "balance", "ball",
            "enter", "leave", "date_of_birth", "compensation", "bonus"
        )
        # We don't need to add extra_kwargs for password

    def create(self, validated_data):
        # Ensure password is provided in the request
        password = validated_data.pop('password', None)
        print(password)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        compensation_data = validated_data.pop('compensation', [])
        bonus_data = validated_data.pop('bonus', [])

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        user.compensation.set(compensation_data)  # Set the compensation
        user.bonus.set(bonus_data)  # Set the bonus
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
    compensation = serializers.PrimaryKeyRelatedField(queryset=Compensation.objects.all(), many=True, required=False)
    bonus = serializers.PrimaryKeyRelatedField(queryset=Bonus.objects.all(), many=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['phone', 'full_name', 'first_name', 'last_name', 'password', 'role', 'photo', "salary",
                  'date_of_birth', 'compensation', 'bonus']

    def update(self, instance, validated_data):
        # Extract and update the password if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)  # Hash the password
            instance.save()  # Save after setting the password

        # Update other fields (except compensation and bonus)
        for attr, value in validated_data.items():
            if attr not in ['compensation', 'bonus']:  # Avoid setting many-to-many fields directly
                setattr(instance, attr, value)

        # Handle many-to-many relationships correctly
        compensation_data = validated_data.pop('compensation', None)
        bonus_data = validated_data.pop('bonus', None)

        if compensation_data is not None:
            instance.compensation.set(compensation_data)  # Correctly update compensation
        if bonus_data is not None:
            instance.bonus.set(bonus_data)  # Correctly update bonus

        instance.save()  # Save the instance after all updates
        return instance



class UserListSerializer(ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', "full_name","first_name","last_name",'role',"salary",
                  "photo", "filial", ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo).data
        return rep


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    compensation = serializers.PrimaryKeyRelatedField(queryset=Compensation.objects.all(), many=True, allow_null=True)
    bonus = serializers.PrimaryKeyRelatedField(queryset=Bonus.objects.all(), many=True, allow_null=True)

    class Meta:
        model = CustomUser
        fields = (
            "id", "full_name", "first_name", "last_name", "phone", "role",
            "photo", "filial", "balance", "ball","salary",
            "enter", "leave", "date_of_birth", "created_at",
            "updated_at", "compensation", "bonus"
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["photo"] = FileUploadSerializer(instance.photo).data if instance.photo else None
        rep["compensation"] = CompensationSerializer(instance.compensation.all(), many=True).data
        rep["bonus"] = BonusSerializer(instance.bonus.all(), many=True).data
        return rep

    def create(self, validated_data):
        compensation_data = validated_data.pop("compensation", [])
        bonus_data = validated_data.pop("bonus", [])

        user = CustomUser.objects.create(**validated_data)

        user.compensation.set(compensation_data)
        user.bonus.set(bonus_data)

        return user