from django.db.models import Count, Q


from rest_framework import serializers

from data.employee.serializers import EmployeeSerializer
from data.student.course.serializers import CourseSerializer
from data.student.groups.models import Group
from data.student.groups.serializers import RoomsSerializer
from data.student.subject.models import Theme
from data.student.subject.serializers import SubjectSerializer


class GroupSerializer(serializers.ModelSerializer):

    teacher = EmployeeSerializer.minimal()

    course = CourseSerializer.minimal()

    subject = SubjectSerializer.minimal()

    student_count = serializers.SerializerMethodField()

    lessons = serializers.SerializerMethodField()

    room_number = RoomsSerializer()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "teacher",
            "status",
            "course",
            "subject",
            "student_count",
            "room_number",
            "lessons",
            "started_at",
            "ended_at",
        ]

    def get_student_count(self, obj: Group):

        return obj.students.filter(is_archive=False).count()

    def get_lessons(self, obj: Group):

        total_lessons = Theme.objects.filter(
            course=obj.course,
            level=obj.level,
            is_archived=False,
        ).count()

        attended_lessons = (
            obj.lessons.values("theme").annotate(attended_count=Count("id")).count()
        )

        return {
            "lessons": total_lessons,
            "attended": attended_lessons,
            "lessons": [
                {
                    "id": lesson.id,
                    "theme": {"id": lesson.theme.id, "name": lesson.theme.title},
                    "is_repeat": lesson.is_repeat,
                }
                for lesson in obj.lessons.select_related("theme").only(
                    "id", "theme", "is_repeat"
                )
            ],
        }
