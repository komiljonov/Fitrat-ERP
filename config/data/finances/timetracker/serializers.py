from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        Model = self.child.Meta.model
        objs = [Model(**item) for item in validated_data]
        with transaction.atomic():
            created = Model.objects.bulk_create(objs)
        return created

    def update(self, instances, validated_data):
        Model = self.child.Meta.model
        # Map {str(id): instance} to handle UUIDs or ints uniformly
        instance_map = {str(inst.id): inst for inst in instances}

        raw_items = list(self.initial_data)  # has 'id'
        updated_objs = []

        # Pair each raw (has id) with its cleaned attrs
        for raw, attrs in zip(raw_items, validated_data):
            pk = str(raw.get("id")) if raw.get("id") is not None else None
            if not pk or pk not in instance_map:
                # You can raise if you want strictness:
                # raise ValidationError({"id": [f"Unknown id: {raw.get('id')}"]})
                continue
            inst = instance_map[pk]
            for field, val in attrs.items():
                setattr(inst, field, val)
            updated_objs.append(inst)

        update_fields = getattr(self.child, "get_updatable_fields")()
        if updated_objs:
            with transaction.atomic():
                Model.objects.bulk_update(updated_objs, fields=update_fields)

        # IMPORTANT: return the instances (not the integer from bulk_update)
        return updated_objs


class UserTimeLineSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)

    class Meta:
        model = UserTimeLine
        fields = [
            "id", "user", "day", "start_time", "end_time",
            "is_weekend", "penalty", "bonus", "created_at",
        ]
        list_serializer_class = UserTimeLineBulkSerializer

    def get_updatable_fields(self):
        return ["user", "day", "start_time", "end_time", "is_weekend", "penalty", "bonus"]



class UserTimeLine1BulkSerializer(serializers.ListSerializer):
    """
    Upsert list:
      - Items WITHOUT 'id' -> created first (bulk_create)
      - Items WITH 'id'    -> updated next (bulk_update with partial data)
    Response preserves the original input order.
    """

    def create(self, validated_data):
        Model = self.child.Meta.model

        # Pair up original raw items (to read 'id') with cleaned items (validated_data)
        raw_items = list(self.initial_data)
        pairs = []
        for i, clean in enumerate(validated_data):
            raw = raw_items[i] if i < len(raw_items) and isinstance(raw_items[i], dict) else {}
            raw_id = raw.get("id")
            pairs.append((raw_id, clean))

        # Split into creates and updates
        to_create_attrs = [attrs for (pk, attrs) in pairs if pk is None]
        to_update_pairs = [(pk, attrs) for (pk, attrs) in pairs if pk is not None]

        # Pre-fetch instances that will be updated
        ids = [pk for pk, _ in to_update_pairs]
        existing_map = {obj.id: obj for obj in Model.objects.filter(id__in=ids)}

        # If any provided id doesn't exist -> fail clearly
        missing_ids = [pk for pk in ids if pk not in existing_map]
        if missing_ids:
            raise ValidationError({"id": [f"Unknown id(s): {missing_ids}"]})

        # Build instances to update (apply only provided fields)
        to_update_instances = []
        for pk, attrs in to_update_pairs:
            inst = existing_map[pk]
            for attr, val in attrs.items():
                setattr(inst, attr, val)
            to_update_instances.append(inst)

        # Determine which fields are allowed to be updated in bulk
        update_fields = self.child.get_updatable_fields()

        with transaction.atomic():
            # 1) Create FIRST
            created_instances = Model.objects.bulk_create(
                [Model(**attrs) for attrs in to_create_attrs]
            ) if to_create_attrs else []

            # 2) Then UPDATE
            if to_update_instances:
                Model.objects.bulk_update(to_update_instances, fields=update_fields)

        # Rebuild the result list in the same order as input
        created_iter = iter(created_instances)
        result = []
        for pk, _attrs in pairs:
            if pk is None:
                result.append(next(created_iter, None))
            else:
                result.append(existing_map[pk])

        # Filter out any Nones (defensive; should not happen)
        return [obj for obj in result if obj is not None]


class UserTimeLine1Serializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)

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
        read_only_fields = ["id", "created_at"]
        list_serializer_class = UserTimeLine1BulkSerializer

    def get_updatable_fields(self):
        # All fields we allow to be set during updates (partial updates OK)
        return ["user", "day", "start_time", "end_time", "is_weekend", "penalty", "bonus"]