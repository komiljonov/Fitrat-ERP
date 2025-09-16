from datetime import date


from rest_framework import serializers

from data.student.attendance.choices import AttendanceStatusChoices
from data.student.attendance.models import Attendance
from data.student.groups.models import Group
from data.student.studentgroup.models import StudentGroup
from data.student.subject.models import Theme


class CreateAttendanceV2ItemSerializer(serializers.Serializer):

    student = serializers.PrimaryKeyRelatedField(queryset=StudentGroup.objects.all())

    status = serializers.ChoiceField(AttendanceStatusChoices.CHOICES)

    comment = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class CreateAttendanceV2Serializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    date = serializers.DateField(required=False, default=date.today)

    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())

    items = CreateAttendanceV2ItemSerializer(many=True)

    repeated = serializers.BooleanField(default=False)


class AttendanceGroupStateSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = ["id", "name", "stage", "status"]

    def get_name(self, obj: StudentGroup):

        # student_atts = self.context["student_attendances"]
        # lead_atts = self.context["lead_attendances"]

        # att = student_atts.get(obj.student_id) or lead_atts.get(obj.lid_id)

        return (
            f"{obj.student.first_name} {obj.student.last_name} {obj.student.middle_name}"
            if obj.student is not None
            else f"{obj.lid.first_name} {obj.lid.last_name} { obj.lid.middle_name}"
        )

    def get_stage(self, obj: StudentGroup):

        return "STUDENT" if obj.student is not None else "ORDER"

    def get_status(self, obj: StudentGroup):

        student_atts = self.context["student_attendances"]
        lead_atts = self.context["lead_attendances"]

        att: "Attendance | None" = student_atts.get(obj.student_id) or lead_atts.get(
            obj.lid_id
        )

        return att.status if att else None
