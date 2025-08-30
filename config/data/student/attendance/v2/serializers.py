from datetime import date


from rest_framework import serializers

from data.lid.new_lid.models import Lid
from data.student.attendance.choices import AttendanceReasonChoices
from data.student.groups.models import Group
from data.student.student.models import Student
from data.student.subject.models import Theme


class CreateAttendanceV2ItemSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
    )
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
    )

    status = serializers.ChoiceField(AttendanceReasonChoices.CHOICES)

    comment = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def validate(self, attrs):
        student = attrs.get("student")
        lead = attrs.get("lead")

        if bool(student) == bool(lead):  # both True or both False
            raise serializers.ValidationError(
                "Exactly one of student or lead must be provided."
            )

        return attrs


class CreateAttendanceV2Serializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    date = serializers.DateField(required=False, default=date.today)

    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())

    items = CreateAttendanceV2ItemSerializer(many=True)

    repeated = serializers.BooleanField(default=False)
