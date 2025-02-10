from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import CustomUser
from ..account.permission import PhoneAuthBackend
from ..finances.compensation.models import Compensation, Bonus, Page
from ..finances.compensation.serializers import CompensationSerializer, BonusSerializer, PagesSerializer
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = (
            "full_name", "first_name", "last_name", "phone", "role","password","salary",
            "photo", "filial", "balance", "ball","pages",
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
        page_data = validated_data.pop('pages', [])

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        user.compensation.set(compensation_data)  # Set the compensation
        user.bonus.set(bonus_data)  # Set the bonus
        user.pages.set(page_data)
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
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    password = serializers.CharField(max_length=128, write_only=True, required=False)
    compensation = serializers.PrimaryKeyRelatedField(queryset=Compensation.objects.all(), many=True, required=False)
    bonus = serializers.PrimaryKeyRelatedField(queryset=Bonus.objects.all(), many=True, required=False)
    pages = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all(), many=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['phone', 'full_name', 'first_name', 'last_name', 'password', 'role', 'photo', "salary","enter", "leave","pages",
                  'date_of_birth', 'compensation', 'bonus']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Handle phone field properly
        phone = validated_data.get('phone')  # Use `.get()` instead of `.pop()`
        if phone and phone != instance.phone:
            if CustomUser.objects.exclude(id=instance.id).filter(phone=phone).exists():
                raise serializers.ValidationError({"phone": "This phone number is already in use."})
            instance.phone = phone  # Only update if changed

        # Update other fields (except compensation and bonus)
        for attr, value in validated_data.items():
            if attr not in ['compensation', 'bonus','pages', 'phone']:  # Skip phone here
                setattr(instance, attr, value)

        # Handle many-to-many relationships correctly
        if "compensation" in validated_data:
            instance.compensation.set(validated_data["compensation"])
        if "bonus" in validated_data:
            instance.bonus.set(validated_data["bonus"])
        if "pages" in validated_data:
            instance.pages.set(validated_data["pages"])

        instance.save()
        return instance
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['photo'] = FileUploadSerializer(instance.photo).data
        return ret


class UserListSerializer(ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', "full_name","first_name","last_name",'role',"salary","pages",
                  "photo", "filial", ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo).data
        return rep


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    compensation = serializers.PrimaryKeyRelatedField(queryset=Compensation.objects.all(), many=True, allow_null=True)
    bonus = serializers.PrimaryKeyRelatedField(queryset=Bonus.objects.all(), many=True, allow_null=True)
    pages = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all(), many=True, allow_null=True)

    class Meta:
        model = CustomUser
        fields = (
            "id", "full_name", "first_name", "last_name", "phone", "role","pages",
            "photo", "filial", "balance", "ball","salary",
            "enter", "leave", "date_of_birth", "created_at",
            "updated_at", "compensation", "bonus"
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["photo"] = FileUploadSerializer(instance.photo).data if instance.photo else None
        rep["compensation"] = CompensationSerializer(instance.compensation.all(), many=True).data
        rep["bonus"] = BonusSerializer(instance.bonus.all(), many=True).data
        rep["pages"] = PagesSerializer(instance.pages.all(), many=True).data
        return rep

    def create(self, validated_data):
        compensation_data = validated_data.pop("compensation", [])
        bonus_data = validated_data.pop("bonus", [])
        page_data = validated_data.pop("pages", [])

        user = CustomUser.objects.create(**validated_data)

        user.compensation.set(compensation_data)
        user.bonus.set(bonus_data)
        user.pages.set(page_data)

        return user