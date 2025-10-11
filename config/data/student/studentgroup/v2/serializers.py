from rest_framework import serializers

from data.account.models import CustomUser
from data.student.course.models import Course
from data.department.filial.models import Filial
from data.student.studentgroup.models import StudentGroupPrice
from data.student.studentgroup.serializers import StudentsGroupSerializer


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

    student_group = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroupPrice
        fields = ["id", "student_group", "amount", "comment"]

    def get_student_group(self, obj: StudentGroupPrice):

        return {
            "id": obj.student_group.id,
            "group": {
                "id": obj.student_group.group.id,
                "name": obj.student_group.group.name,
            },
            "student": (
                {
                    "id": obj.student_group.student_id,
                    "first_name": obj.student_group.student.first_name,
                    "last_name": obj.student_group.student.last_name,
                    "middle_name": obj.student_group.student.middle_name,
                }
                if obj.student_group.student
                else None
            ),
            "lead": (
                {
                    "id": obj.student_group.lid_id,
                    "first_name": obj.student_group.lid.first_name,
                    "last_name": obj.student_group.lid.last_name,
                    "middle_name": obj.student_group.lid.middle_name,
                }
                if obj.student_group.lid
                else None
            ),
        }
