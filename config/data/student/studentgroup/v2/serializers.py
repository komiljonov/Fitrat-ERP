from rest_framework import serializers

from data.account.models import CustomUser
from data.student.course.models import Course
from data.department.filial.models import Filial
from data.student.studentgroup.models import StudentGroupPrice


class GroupStatisticsFilterSerializer(serializers.Serializer):

    filial = serializers.PrimaryKeyRelatedField(
        queryset=Filial.objects.all(),
        allow_null=True,
        required=False,
    )

    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        allow_null=True,
        required=False,
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="TEACHER"),
        allow_null=True,
        required=False,
    )

    start_date = serializers.DateField(allow_null=True, required=False)

    end_date = serializers.DateField(allow_null=True, required=False)


class StudentGroupPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentGroupPrice
        fields = ["id", "student_group", "amount", "comment"]
