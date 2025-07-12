import random
import string

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from data.account.models import CustomUser
from data.parents.models import Relatives
from data.student.student.sms import SayqalSms

sms = SayqalSms()


class RelativesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatives
        fields = [
          'id',
          'lid',
          'student',
          'name',
          'phone',
          'who',
        ]


    def create(self, validated_data):
        phone = validated_data.get("phone")
        student = validated_data.get("student")
        name = validated_data.get("name")

        if phone and student:
            # ✅ Generate strong 8-character password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # ✅ Create CustomUser
            parent = CustomUser.objects.create(
                full_name=name,
                phone=phone,
                password=make_password(password),  # hash the password
                role="Parents",  # or whatever your parent role is called
            )

            # ✅ Optionally send or log password
            print(f"Parent account created with phone {phone} and password: {password}")
            sms.send_sms(
                number=phone,
                message=f"""
                Fitrat Ota - Onalar uchun ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!

                Login: {phone}
                Parol: {password}

                Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                """
            )

            # ✅ Create Relative linking user to student
            relative = Relatives.objects.create(
                student=student,
                name=name,
                phone=phone,
                who=validated_data.get("who"),
                lid=None
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
        parent_user = CustomUser.objects.filter(phone=phone, role="Parents").first()

        if not parent_user:
            # If not found, create one
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
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
                """
            )
            print(f"New parent user created for phone {phone} with password: {password}")

        # Update Relative instance
        instance.name = name
        instance.phone = phone
        instance.who = who
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
