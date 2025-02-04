
from rest_framework import serializers

from .models import Attendance
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(),many=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(),allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),allow_null=True)
    teacher = serializers.SerializerMethodField()
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
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        if obj.theme.exists():  # Check if there's at least one theme
            # Assuming `obj.theme` is a ManyToManyField, and we want the first theme for now
            theme = obj.theme.first()  # Get the first theme (or choose another way to determine which theme to use)

            teacher = (Attendance.objects
                       .filter(student=obj.student, theme=theme)
                       .values('theme__course__group__teacher__first_name',
                               'theme__course__group__teacher__last_name'))

            # Ensure that we get the teacher's information in the desired format
            if teacher.exists():
                return teacher[0]  # Returning the first teacher found (or adjust depending on your needs)
        return None  # Return None if no teacher is found or no theme is available

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['theme'] = ThemeSerializer(instance.theme,many=True).data

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
