from rest_framework import serializers

from data.firstlesson.models import FirstLesson
from data.lid.new_lid.models import Lid
from data.student.groups.models import Group


class FirstLessonSerializer(serializers.ModelSerializer):

    lead = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.filter(status="ACTIVE")
    )

    class Meta:
        model = FirstLesson
        fields = ["id", "lead", "group", "date", "status", "comment", "creator"]
