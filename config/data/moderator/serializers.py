from rest_framework import serializers
from ..account.models import CustomUser
from ..lid.new_lid.models import Lid
from ..lid.new_lid.serializers import LidSerializer
from ..student.student.models import Student
from ..student.student.serializers import StudentSerializer


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'full_name',
            'phone',
            'photo',
            'role',
            'created_at',
            'updated_at',
            # 'balance',

        ]


class ModeratorStudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Moderator that includes their related students and lids.
    """
    students = serializers.SerializerMethodField()
    lids = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',          # Moderator's ID
            'full_name',   # Full name of the moderator
            'phone',       # Phone number
            'photo',       # Photo of the moderator
            'role',        # Role (should be MODERATOR)
            'created_at',  # Date of creation
            'updated_at',  # Last update date
            'students',    # Related students
            'lids',        # Related lids
        ]

    def get_students(self, obj):
        """
        Fetch students related to this moderator.
        """
        students = Student.objects.filter(moderator=obj)  # No need to order by
        return StudentSerializer(students, many=True).data

    def get_lids(self, obj):
        """
        Fetch lids related to this moderator.
        """
        lids = Lid.objects.filter(moderator=obj)  # No need to order by
        return LidSerializer(lids, many=True).data

    def to_representation(self, instance):
        """
        Optionally combine students and lids into a single list.
        """
        representation = super().to_representation(instance)
        representation['combined'] = representation['students'] + representation['lids']
        return representation


