from django.db.models import Sum
from icecream import ic
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import CustomUser
from ..account.permission import PhoneAuthBackend
from ..department.filial.models import Filial
from ..finances.compensation.models import Compensation, Bonus, Page
from ..finances.finance.models import Casher
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "id", "full_name", "first_name", "last_name", "phone", "role", "password", "salary",
            "photo", "filial", "balance", "ball", "files","extra_number","is_call_center",
            "enter", "leave", "date_of_birth",
        )
        # We don't need to add extra_kwargs for password

    def create(self, validated_data):
        # Ensure password is provided in the request
        password = validated_data.pop('password', None)
        print(password)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        files = validated_data.pop('files', [])
        filial = validated_data.pop('filial', None)

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.full_name = f"{user.first_name} {user.last_name}"
        user.save()
        user.filial.set(filial)
        user.files.set(files)
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

        user = CustomUser.objects.get(phone=phone)

        if phone:
            user = CustomUser.objects.get(phone=phone)
            if user.is_archived ==True:
                raise serializers.ValidationError({"permission denied": "Sizning faoliyatingiz cheklangan!"},
                                                  code='permission_denied')
        if phone and user.role not in ["TEACHER","ASSISTANT"]:

            user = CustomUser.objects.filter(phone=phone).first()

            pages = Page.objects.filter(user=user, is_readable=True)
            if not pages.exists() and (user.role not in ["Student", "Parents"]):
                raise serializers.ValidationError({"permission denied": "Siz uchun ruxsat etilgan saxivalar yo'q !"},
                                                  code='permission_denied')

        if phone and password:
            backend = PhoneAuthBackend()
            user = backend.authenticate(
                request=self.context.get('request'),
                phone=phone,
                password=password,
            )
            ic(user)

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
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True, required=False)
    password = serializers.CharField(max_length=128, write_only=True, required=False)
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, required=False)
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(),many=True, required=False)

    class Meta:
        model = CustomUser
        fields = ["id", "phone", "full_name", "first_name", "last_name", "password","is_archived",
                  "role", "photo", "salary", "enter", "leave", "files","filial","extra_number","is_call_center",
                  "date_of_birth"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        phone = validated_data.get("phone")
        if phone and phone != instance.phone:
            if CustomUser.objects.exclude(id=instance.id).filter(phone=phone).exists():
                raise serializers.ValidationError({"phone": "already_used_number"})
            instance.phone = phone

        # Update `photo` field manually
        if "photo" in validated_data:
            instance.photo = validated_data["photo"]

        # Update other fields except many-to-many
        for attr, value in validated_data.items():
            if attr not in [ "files","filial"]:
                setattr(instance, attr, value)

        if "first_name" or "last_name" in validated_data:
            instance.full_name = f"{instance.first_name} {instance.last_name}"


        if "files" in validated_data:
            print("Updating files:", validated_data["files"])  # Debugging
            instance.files.set(validated_data["files"] or [])

        if "filial" in validated_data:
            instance.filial.set(validated_data["filial"] or [])

        instance.save()
        return instance

    def to_representation(self, instance):
        # Get the base URL for media
        representation = super().to_representation(instance)
        if instance.photo:
            representation['photo'] = FileUploadSerializer(instance.photo, context=self.context).data
        return representation


class UserListSerializer(ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
    bonus = serializers.SerializerMethodField()
    compensation = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', "full_name", "first_name", "last_name", 'role',"balance",
                  "salary", "pages", "files","is_archived","extra_number","is_call_center",
                  "photo", "filial", "bonus", "compensation","created_at" ]

    def get_bonus(self, obj):
        bonus = Bonus.objects.filter(user=obj).values("id", "name", "amount")
        return list(bonus)

    def get_compensation(self, obj):
        compensation = Compensation.objects.filter(user=obj).values("id", "name", "amount")
        return list(compensation)

    def get_pages(self, obj):
        pages = Page.objects.filter(user=obj).values("id", "name", "user", "is_editable", "is_readable", "is_parent")
        return list(pages)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo, context=self.context).data
        rep['files'] = FileUploadSerializer(instance.files.all(), many=True, context=self.context).data
        return rep


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    pages = serializers.SerializerMethodField()
    bonus = serializers.SerializerMethodField()
    compensation = serializers.SerializerMethodField()
    penalty = serializers.SerializerMethodField()
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)
    is_linked = serializers.SerializerMethodField()


    # def __init__(self, *args, **kwargs):
    #     fields_to_remove: list | None = kwargs.pop("remove_fields", None)
    #     super(UserSerializer, self).__init__(*args, **kwargs)
    #
    #     if fields_to_remove:
    #         for field in fields_to_remove:
    #             self.fields.pop(field, None)

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError("You cannot use 'remove_fields' and 'include_only' at the same time.")

        super(UserSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    class Meta:
        model = CustomUser
        fields = (
            "id", "full_name", "first_name", "last_name", "is_linked","phone", "role", "penalty" ,"pages", "files",
            "photo", "filial", "balance", "ball", "salary","extra_number","is_call_center",
            "enter", "leave", "date_of_birth", "created_at", "bonus", "compensation",
            "updated_at","is_archived"
        )

    def get_penalty(self, obj):
        # Use .aggregate() to get the sum of the 'amount' field
        compensation = Compensation.objects.filter(user=obj).aggregate(total_penalty=Sum('amount'))

        # Extract the sum value
        total_penalty = compensation.get('total_penalty', 0)  # Defaults to 0 if there's no match

        return total_penalty

    def get_is_linked(self, obj):
        return [True if Casher.objects.filter(user=obj).exists() else False]

    def get_bonus(self, obj):
        bonus = Bonus.objects.filter(user=obj).values("id", "name", "amount")
        return list(bonus)

    def get_compensation(self, obj):
        compensation = Compensation.objects.filter(user=obj).values("id", "name", "amount")
        return list(compensation)

    def get_pages(self, obj):
        pages = Page.objects.filter(user=obj).values("id", "name", "user", "is_editable",
                                                     "is_readable", "is_parent")
        return list(pages)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['photo'] = FileUploadSerializer(instance.photo, context=self.context).data
        rep['files'] = FileUploadSerializer(instance.files.all(), many=True, context=self.context).data
        return rep

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        return user

class CheckNumberSerializer(serializers.Serializer):
    phone = serializers.CharField()

