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
    Mixed bulk upsert:
      - no 'id' / empty 'id' -> create
      - with 'id'            -> update only provided fields
    Creates happen first (bulk_create), updates second (bulk_update).
    Response mirrors input order.
    """

    # --- helpers -------------------------------------------------------------
    def _pairs_from_initial(self, validated_data):
        raw_items = list(self.initial_data)
        pairs = []
        for i, attrs in enumerate(validated_data):
            raw = raw_items[i] if i < len(raw_items) and isinstance(raw_items[i], dict) else {}
            pk = raw.get("id", None)
            if pk in ("", None) or (isinstance(pk, str) and pk.lower() == "null"):
                pk = None
            pairs.append((pk, attrs))
        return pairs

    def _upsert(self, validated_data):
        Model = self.child.Meta.model
        updatable = set(self.child.get_updatable_fields())

        pairs = self._pairs_from_initial(validated_data)
        to_create_attrs = [attrs for (pk, attrs) in pairs if pk is None]
        to_update_pairs = [(pk, attrs) for (pk, attrs) in pairs if pk is not None]

        ids = [pk for pk, _ in to_update_pairs]
        existing_map = {obj.id: obj for obj in Model.objects.filter(id__in=ids)}

        missing_ids = [pk for pk in ids if pk not in existing_map]
        if missing_ids:
            raise ValidationError({"id": [f"Unknown id(s): {missing_ids}"]})

        to_update_instances = []
        for pk, attrs in to_update_pairs:
            inst = existing_map[pk]
            for field, value in attrs.items():
                if field in updatable:
                    setattr(inst, field, value)
            to_update_instances.append(inst)

        with transaction.atomic():
            created_instances = Model.objects.bulk_create(
                [Model(**attrs) for attrs in to_create_attrs]
            ) if to_create_attrs else []

            if to_update_instances:
                Model.objects.bulk_update(to_update_instances, fields=list(updatable))

        # Return results in original order
        created_iter = iter(created_instances)
        result = []
        for pk, _ in pairs:
            result.append(next(created_iter) if pk is None else existing_map[pk])
        return result

    # --- DRF entry points ----------------------------------------------------
    def create(self, validated_data):
        return self._upsert(validated_data)

    def update(self, instance, validated_data):
        # This is called if you pass instance=... or use PUT/UpdateAPIView
        return self._upsert(validated_data)


class UserTimeLine1Serializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    start_time = serializers.TimeField(allow_null=True, required=False)
    end_time   = serializers.TimeField(allow_null=True, required=False)

    class Meta:
        model = UserTimeLine
        fields = [
            "id", "user", "day", "start_time", "end_time",
            "is_weekend", "penalty", "bonus", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        list_serializer_class = UserTimeLine1BulkSerializer

    def to_internal_value(self, data):
        # Accept "" for time fields -> treat as NULL
        data = data.copy()
        for f in ("start_time", "end_time"):
            if data.get(f) == "":
                data[f] = None
        return super().to_internal_value(data)

    def get_updatable_fields(self):
        return ["user", "day", "start_time", "end_time", "is_weekend", "penalty", "bonus"]