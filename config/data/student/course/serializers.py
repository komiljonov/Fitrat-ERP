from rest_framework import serializers

from data.student.course.models import Course
from data.student.subject.serializers import SubjectSerializer, ThemeSerializer


class CourseSerializer(serializers.ModelSerializer):
    theme = ThemeSerializer(many=True)
    class Meta:
        model = Course
        fields = ["id",
                  'name',
                  'lessons_number',
                  'theme',
                  "subject",
                  "status"
                  ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject).data
        return rep
