from rest_framework import serializers

from data.student.course.models import Course
from data.student.subject.models import Level
from data.student.subject.serializers import SubjectSerializer, ThemeSerializer, LevelSerializer


class CourseSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    theme = ThemeSerializer(many=True)

    class Meta:
        model = Course
        fields = ["id",
                  'name',
                  'level',
                  'lessons_number',
                  'theme',
                  "subject",
                  "status"
                  ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['level'] = LevelSerializer(instance.level).data
        rep["subject"] = SubjectSerializer(instance.subject).data
        return rep
