from datetime import date, datetime

from django.db.models import Q
from rest_framework import serializers
from .models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..studentgroup.models import StudentGroup
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer

from datetime import date, datetime

from datetime import datetime, timedelta

class AttendanceSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), many=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    teacher = serializers.SerializerMethodField()
    is_attendance = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'theme',
            'repeated',
            'lid',
            'student',
            'teacher',
            'reason',
            'remarks',
            'is_attendance',
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        if obj.theme.exists():
            theme = obj.theme.first()
            teacher = (Attendance.objects
                       .filter(student=obj.student, theme=theme)
                       .values('theme__course__group__teacher__first_name',
                               'theme__course__group__teacher__last_name'))
            if teacher.exists():
                return teacher[0]
        return None

    def get_is_attendance(self, obj):
        # Determine whether obj_student is a Student or a Lid
        obj_student = obj.student if obj.student else obj.lid

        # Ensure obj_student is a Lid instance before querying with it
        if isinstance(obj_student, Lid):
            att = Attendance.objects.filter(Q(lid=obj_student), created_at__gte=date.today())
        else:
            att = Attendance.objects.filter(Q(student=obj_student), created_at__gte=date.today())

        return att

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['theme'] = ThemeSerializer(instance.theme, many=True).data
        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid).data
        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student).data
        else:
            rep.pop('student', None)

        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data

