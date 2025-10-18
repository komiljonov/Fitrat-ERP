from datetime import date as _date
from typing import Dict


from rest_framework import serializers

from data.student.attendance.choices import AttendanceStatusChoices
from data.student.attendance.models import Attendance
from data.student.groups.models import Group, GroupLesson
from data.student.studentgroup.models import StudentGroup
from data.student.subject.models import Theme

from data.firstlesson.serializers import FirstLessonSingleSerializer


class CreateAttendanceV2ItemSerializer(serializers.Serializer):

    student = serializers.PrimaryKeyRelatedField(queryset=StudentGroup.objects.all())

    status = serializers.ChoiceField(AttendanceStatusChoices.CHOICES)

    comment = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class CreateAttendanceV2Serializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    date = serializers.DateField(required=False, default=_date.today)

    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())

    items = CreateAttendanceV2ItemSerializer(many=True)

    repeated = serializers.BooleanField(default=False)

    def validate(self, attrs: Dict):
        group: Group = attrs["group"]
        d = attrs.get("date") or _date.today()
        theme: Theme = attrs["theme"]
        repeated: bool = attrs.get("repeated", False)

        qs = GroupLesson.objects.filter(group=group, theme=theme)

        if not repeated:
            # Only one non-repeat per (group, theme), except same date (treated as "update")
            if qs.filter(is_repeat=False).exclude(date=d).exists():
                raise serializers.ValidationError(
                    "Bu guruh va mavzu uchun (non-repeat) kun allaqachon mavjud."
                )
            # Any existing repeats must be strictly after this non-repeat date
            if qs.filter(is_repeat=True, date__lte=d).exists():
                raise serializers.ValidationError(
                    "Oldinroq yoki shu kunda repeated dars bor. Non-repeat kuni barcha repeatedlardan oldin bo‘lishi kerak."
                )

        else:
            # MUST have an existing base (non-repeat) for this (group, theme)
            base = qs.filter(is_repeat=False).first()
            # if base is None:
            #     raise serializers.ValidationError(
            #         "Repeated dars yaratib bo‘lmaydi: avval non-repeat (asosiy) dars bo‘lishi shart."
            #     )

            # if Base is exsits then repeats must be strictly after the base day
            if base and d <= base.date:
                raise serializers.ValidationError(
                    "Repeated dars sanasi non-repeat (asosiy) kundan keyin bo‘lishi kerak."
                )

        return attrs


class AttendanceGroupStateSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()

    frozen_date = serializers.SerializerMethodField()

    attendance = serializers.SerializerMethodField()

    first_lesson = FirstLessonSingleSerializer.only("id", "date", "status")()

    class Meta:
        model = StudentGroup
        fields = ["id", "name", "stage", "attendance", "frozen_date", "first_lesson"]

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

    def get_frozen_date(self, obj: StudentGroup):

        return (
            obj.student.frozen_till_date if obj.student and obj.student.is_frozen else None
        )

    def get_attendance(self, obj: StudentGroup):

        student_atts = self.context["student_attendances"]
        lead_atts = self.context["lead_attendances"]

        att: "Attendance | None" = student_atts.get(obj.student_id) or lead_atts.get(
            obj.lid_id
        )

        return (
            {"id": att.id, "comment": att.comment, "status": att.status}
            if att
            else None
        )


class AttendanceThemeRequestSerializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    date = serializers.DateField(required=False, allow_null=True)
