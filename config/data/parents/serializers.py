import random
import string

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from data.parents.tasks import send_creds_to_relatives
from data.account.models import CustomUser
from data.lid.new_lid.models import Lid
from data.parents.models import Relatives
from data.student.student.models import Student
from data.student.student.sms import SayqalSms

sms = SayqalSms()


class RelativesSerializer(serializers.ModelSerializer):

    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
        required=False,
    )

    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
        required=False,
    )

    def validate(self, attrs):
        student = attrs.get("student")
        lid = attrs.get("lid")

        if not student and not lid:
            raise serializers.ValidationError("Either 'student' or 'lid' is required.")
        if student and lid:
            raise serializers.ValidationError(
                "You cannot provide both 'student' and 'lid'."
            )

        return attrs

    class Meta:
        model = Relatives
        fields = [
            "id",
            "lid",
            "student",
            "name",
            "phone",
            "who",
            "user",
        ]

    def create(self, validated_data):
        phone = validated_data.get("phone")
        student = validated_data.get("student")
        name = validated_data.get("name")
        lid = validated_data.get("lid")

        if phone:
            parent = CustomUser.objects.filter(phone=phone).first()
            if not parent:
                password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=8)
                )

                parent = CustomUser.objects.create(
                    full_name=name,
                    phone=phone,
                    password=make_password(password),
                    role="Parents",
                )

                # ✅ Optionally send or log password
                print(
                    f"Parent account created with phone {phone} and password: {password}"
                )
                # sms.send_sms(
                #     number=phone,
                #     message=f"""
                #     Fitrat Ota - Onalar uchun ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!

                #     Login: {phone}
                #     Parol: {password}

                #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                #     """,
                # )

                send_creds_to_relatives.delay(parent.id, password)

            # ✅ Create Relative linking user to student
            relative = Relatives.objects.create(
                student=student,
                name=name,
                phone=phone,
                who=validated_data.get("who"),
                user=parent,
                lid=lid,
            )
            return relative

        raise serializers.ValidationError("Phone and student must be provided.")

    def update(self, instance, validated_data):
        phone = validated_data.get("phone", instance.phone)
        name = validated_data.get("name", instance.name)
        who = validated_data.get("who", instance.who)
        student = validated_data.get("student", instance.student)
        lid = validated_data.get("lid", instance.lid)

        # Check for existing parent user with this phone
        parent_user = CustomUser.objects.filter(
            phone=phone,
            role="Parents",
        ).first()

        if not parent_user:
            # If not found, create one
            password = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )
            parent_user = CustomUser.objects.create(
                full_name=name,
                phone=phone,
                password=make_password(password),
                role="Parents",
            )

            sms.send_sms(
                number=phone,
                message=f"""
                Fitrat Ota - Onalar uchun ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!

                Login: {phone}
                Parol: {password}

                Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                """,
            )
            print(
                f"New parent user created for phone {phone} with password: {password}"
            )

        # Update Relative instance
        instance.name = name
        instance.phone = phone
        instance.who = who
        instance.parent = parent_user

        if student and lid is None:
            instance.student = student
            instance.lid = None
        else:
            instance.student = None
            instance.lid = lid

        instance.save()

        # Optionally update user name and phone again
        parent_user.full_name = name
        parent_user.phone = phone
        parent_user.save()

        return instance
