from django.db.models import Q
from rest_framework import serializers

from data.account.models import CustomUser
from .models import Employee_attendance, UserTimeLine, Stuff_Attendance
from ...student.groups.models import Group


class Stuff_AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stuff_Attendance
        fields = [
            "id",
            "employee",
            "check_in",
            "check_out",
            "not_marked",
            "date",
            "amount",
            "action",
            "actions",
            "created_at",
        ]


class TimeTrackerSerializer(serializers.ModelSerializer):
    attendance = serializers.PrimaryKeyRelatedField(
        queryset=Employee_attendance.objects.all(), many=True, allow_null=True
    )
    employee = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), allow_null=True
    )

    groups = serializers.SerializerMethodField()  # <-- Bu yangi qo‘shildi

    class Meta:
        model = Employee_attendance
        fields = [
            "id",
            "employee",
            "attendance",
            "date",
            "amount",
            "group",
            "status",
            "created_at",
            "groups",  # <-- Bu yerga ham qo‘shildi
        ]

    def get_groups(self, obj):
        DAY_TRANSLATIONS = {
            'MONDAY': 'Dushanba',
            'TUESDAY': 'Seshanba',
            'WEDNESDAY': 'Chorshanba',
            'THURSDAY': 'Payshanba',
            'FRIDAY': 'Juma',
            'SATURDAY': 'Shanba',
            'SUNDAY': 'Yakshanba',
        }

        user = CustomUser.objects.filter(id=obj.employee.id).first()
        result = []

        if user and user.role in ["TEACHER", "ASSISTANT"]:
            groups = Group.objects.filter(Q(teacher=user) | Q(secondary_teacher=user)).distinct()
            for group in groups:
                days_qs = group.scheduled_day_type.all()
                days_uz = [DAY_TRANSLATIONS.get(day.name.upper(), day.name) for day in days_qs]

                result.append({
                    "group_name": group.name,
                    "started_at": group.started_at.strftime('%H:%M'),
                    "ended_at": group.ended_at.strftime('%H:%M'),
                    "days": days_uz
                })
        else:
            timeline = UserTimeLine.objects.filter(user=obj.employee).all()
            for i in timeline:
                result.append({
                    "started_at": i.start_time.strftime('%H:%M'),
                    "ended_at": i.end_time.strftime('%H:%M'),
                    "days": i.day
                })

        return result

    def create(self, validated_data):
        if validated_data["attendance"] is None:
            validated_data["attendance"] = []

        return super(TimeTrackerSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data["attendance"] is None:
            validated_data["attendance"] = []
        return super(TimeTrackerSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["employee"] = {
            "id": instance.employee.id,
            "full_name": instance.employee.full_name,
        }
        rep["attendance"] = Stuff_AttendanceSerializer(instance.attendance, many=True).data
        return rep


class UserTimeLineBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        return UserTimeLine.objects.bulk_create([
            UserTimeLine(**item) for item in validated_data
        ])

    def update(self, instances, validated_data):
        # map instance id -> instance
        instance_mapping = {instance.id: instance for instance in instances}
        updated_objs = []

        for item in validated_data:
            instance = instance_mapping.get(item.get("id"))
            if instance:
                for attr, value in item.items():
                    setattr(instance, attr, value)
                updated_objs.append(instance)

        return UserTimeLine.objects.bulk_update(
            updated_objs,
            fields=["day", "start_time", "end_time", "is_weekend", "penalty", "bonus"]
        )


class UserTimeLineSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )

    class Meta:
        model = UserTimeLine
        fields = [
            "id",
            "user",
            "day",
            "start_time",
            "end_time",
            "is_weekend",
            "penalty",
            "bonus",
            "created_at",
        ]
        list_serializer_class = UserTimeLineBulkSerializer

#
# class UserTimeLine1BulkSerializer(serializers.ListSerializer):
#     """
#     Upsert in bulk:
#       - item with 'id' -> UPDATE (404 if id doesn't exist)
#       - item without 'id' -> CREATE
#     """
#
#     def _updatable_fields(self):
#         # Compute concrete, editable fields (exclude PK & created_at)
#         model = self.child.Meta.model
#         names = []
#         for f in model._meta.concrete_fields:
#             if f.primary_key or not f.editable:
#                 continue
#             if f.name == "created_at":
#                 continue
#             names.append(f.name)
#         return names
#
#     def create(self, validated_data):
#         Model = self.child.Meta.model
#         raw_items = list(self.initial_data)  # to read 'id' presence
#
#         # Pair each validated dict with its raw id (DRF strips 'id' from validated_data)
#         pairs = []
#         for i, clean in enumerate(validated_data):
#             raw_id = None
#             if i < len(raw_items) and isinstance(raw_items[i], dict):
#                 raw_id = raw_items[i].get("id")
#             pairs.append((raw_id, clean))
#
#         # Fetch existing instances in one query
#         ids = [pk for pk, _ in pairs if pk]
#         existing = Model.objects.in_bulk(ids)  # {id: instance}
#
#         to_update, to_create = [], []
#
#         for pk, attrs in pairs:
#             if pk:
#                 obj = existing.get(pk)
#                 if not obj:
#                     # Client sent id but row not found -> fail loudly
#                     raise serializers.ValidationError({"id": f"{pk} not found"})
#                 # Assign only provided attrs
#                 for attr, value in attrs.items():
#                     setattr(obj, attr, value)
#                 to_update.append(obj)
#             else:
#                 to_create.append(Model(**attrs))
#
#         update_fields = self._updatable_fields()
#
#         with transaction.atomic():
#             created = Model.objects.bulk_create(to_create)
#             if to_update:
#                 Model.objects.bulk_update(to_update, update_fields)
#
#         # Return updated + created so serializer.data renders everything
#         return to_update + created
#
#
# class UserTimeLine1Serializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         queryset=CustomUser.objects.all(), allow_null=True
#     )
#
#     class Meta:
#         model = UserTimeLine
#         fields = [
#             "id",
#             "user",
#             "day",
#             "start_time",
#             "end_time",
#             "is_weekend",
#             "penalty",
#             "bonus",
#             "created_at",
#         ]
#         read_only_fields = ["created_at"]
#         list_serializer_class = UserTimeLineBulkSerializer
