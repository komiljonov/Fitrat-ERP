from rest_framework import serializers

from data.archive.models import Archive
from data.comments.serializers import CommentSerializer
from data.employee.serializers import EmployeeSerializer
from data.lid.new_lid.serializers import LeadSerializer
from data.student.student.serializers import StudentSerializer


class ArchiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Archive

        fields = [
            "id",
            "created_at",
            "obj_status",
            "reason",
            "creator",
            "lead",
            "student",
            "comment",
            "unarchived_by",
        ]

    def to_representation(self, instance: Archive):
        # Get the default representation
        representation = super().to_representation(instance)

        # Add detailed serialization for related fields
        if instance.creator:
            representation["creator"] = EmployeeSerializer(
                instance.creator,
                include_only=["id", "first_name", "last_name", "middle_name"],
            ).data

        if instance.lead:
            representation["lead"] = LeadSerializer(
                instance.lead,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone_number",
                    "sales_manager",
                    "service_manager",
                    "lid_stage_type",
                    "lid_stages",
                    "ordered_stages",
                    "call_operator",
                    "balance",
                ],
            ).data

        if instance.student:
            representation["student"] = StudentSerializer(
                instance.student,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone",
                    "balance",
                    "sales_manager",
                    "service_manager",
                    "student_stage_type",
                    "new_student_stages",
                    "balance",
                ],
            ).data

        if instance.comment:
            representation["comment"] = CommentSerializer(instance.comment).data

        return representation
