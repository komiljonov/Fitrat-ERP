from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_datetime, parse_date
from icecream import ic
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee_attendance
from .models import UserTimeLine, Stuff_Attendance
from .serializers import Stuff_AttendanceSerializer, UserTimeLineUpsertSerializer
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer
from .utils import calculate_amount, delete_user_actions, get_updated_datas
from ...account.models import CustomUser


class TimeTrackerList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer

    def get_queryset(self):
        queryset = Employee_attendance.objects.filter(attendance__action="In_side", employee__is_archived=False)

        employee = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        date = self.request.GET.get('date')
        is_weekend = self.request.GET.get('is_weekend')
        from_date = self.request.GET.get('start_date')
        to_date = self.request.GET.get('end_date')
        action = self.request.GET.get('action')
        is_archived = self.request.GET.get('is_archived')

        if is_archived:
            queryset = queryset.filter(employee__is_archived=is_archived.capitalize())
        if action:
            queryset = queryset.filter(attendance__action=action)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if from_date and to_date:
            queryset = queryset.filter(date__gte=from_date, date__lte=to_date)

        if is_weekend:
            queryset = queryset.filter(is_weekend=is_weekend.capitalize())
        if employee:
            queryset = queryset.filter(employee__id=employee)
        if status:
            queryset = queryset.filter(status=status)
        if date:
            queryset = queryset.filter(date=parse_datetime(date))
        return queryset.order_by('-date')


class AttendanceList(ListCreateAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer

    def create(self, request, *args, **kwargs):
        ic(request.data)

        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        date = request.data.get('date')
        employee = request.data.get('employee')
        actions = request.data.get('actions')

        # Validate user exists
        user = CustomUser.objects.filter(second_user=employee).first()
        if not user:
            return Response(
                "User not found",
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if attendance already exists for this date
        existing_attendance = Stuff_Attendance.objects.filter(
            employee__id=employee,
            date=date
        ).exists()

        if existing_attendance:
            return Response(
                "Attendance for this date already exists",
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.create_attendance(request.data)

    def create_attendance(self, data):
        actions = data.get('actions')
        employee = data.get('employee')
        date = data.get('date')

        if not actions:
            return Response(
                "No actions provided",
                status=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.filter(second_user=employee).first()

        # Delete existing actions for this date to avoid duplicates
        delete_actions = delete_user_actions(user, actions, date)

        # Sort actions by start time
        sorted_actions = sorted(actions, key=lambda x: x['start'])

        # Calculate amount for ALL actions at once
        att_amount = calculate_amount(
            user=user,
            actions=sorted_actions,
        )

        total_amount = att_amount.get("total_eff_amount", 0)

        # Get or create employee attendance record
        emp_att, created = Employee_attendance.objects.get_or_create(
            employee=user,
            date=date,
            defaults={'amount': 0}
        )

        # Create individual attendance records for each action
        for action in sorted_actions:
            check_in = action.get('start')
            check_out = action.get('end')

            if isinstance(check_in, str):
                check_in = datetime.fromisoformat(check_in)
            if isinstance(check_out, str) and check_out is not None:
                check_out = datetime.fromisoformat(check_out)

            attendance = Stuff_Attendance.objects.create(
                employee=user,
                check_in=check_in,
                check_out=check_out,
                date=date,
                action="In_side" if action.get("type") == "INSIDE" else "Outside",
                actions=[action],  # Store individual action, not all actions
            )

            emp_att.attendance.add(attendance)

        # Update total amount once for all actions
        emp_att.amount = total_amount
        emp_att.save()

        return Response("Attendance created", status=status.HTTP_201_CREATED)


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        data = request.data

        ic(data)

        employee = CustomUser.objects.filter(second_user=data.get("employee")).first()
        if not employee:
            raise NotFound("Employee not found")

        instance.employee = employee
        instance.check_in = data.get("check_in")
        instance.check_out = data.get("check_out")
        instance.date = data.get("date")
        instance.actions = data.get("actions")
        instance.not_marked = data.get("not_marked", instance.not_marked)

        updated_json = get_updated_datas(employee, instance.date)

        calculated_amount = calculate_amount(
            user=instance.employee,
            actions=updated_json,
        )
        ic(calculated_amount)

        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTimeLineList(ListCreateAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer

    def get_queryset(self):
        queryset = UserTimeLine.objects.all()

        user = self.request.GET.get('user')
        day = self.request.GET.get('day')
        if user:
            queryset = queryset.filter(user__id=user)

        if day:
            queryset = queryset.filter(day=day)

        return queryset.order_by("start_time")


class UserTimeLineDetail(RetrieveUpdateDestroyAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        ids = [item["id"] for item in request.data if "id" in item]
        instances = list(UserTimeLine.objects.filter(id__in=ids))

        serializer = self.get_serializer(instances, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return Response({"detail": "Expected a list of ids."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = UserTimeLine.objects.filter(id__in=ids).delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)


def _norm_pk(v):
    # Normalize id values from JSON ("", None, "null", "123") -> (None or int)
    if v is None or v == "" or v == "null":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return v  # if it's not int-like, let Django coerce/fail later


class UserTimeLineBulkUpsert(APIView):
    """
    POST a list of items:
      - item without 'id' -> create
      - item with 'id'    -> update that row with the given fields (partial)
    Returns saved rows in the same order as input.
    """

    UPDATABLE_FIELDS = ["user", "day", "start_time", "end_time", "is_weekend", "penalty", "bonus"]

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        items = request.data

        # Split into create vs update
        create_payloads = []
        update_payloads = []  # list of (pk, payload)
        for obj in items:

            print(obj,type(obj))
            if not isinstance(obj, dict):
                return Response({"detail": "Each item must be an object."}, status=400)
            pk = _norm_pk(obj.get("id"))
            if pk is None:
                create_payloads.append(obj)
            else:
                update_payloads.append((pk, obj))

        # Validate creates
        create_sers = [UserTimeLineUpsertSerializer(data=payload) for payload in create_payloads]
        for ser in create_sers:
            ser.is_valid(raise_exception=True)
        create_instances = [UserTimeLine(**ser.validated_data) for ser in create_sers]

        # Validate updates
        update_ids = [pk for pk, _ in update_payloads]
        existing = UserTimeLine.objects.filter(id__in=update_ids)
        existing_map = {obj.id: obj for obj in existing}
        missing = [pk for pk in update_ids if pk not in existing_map]
        if missing:
            return Response({"id": [f"Unknown id(s): {missing}"]}, status=status.HTTP_400_BAD_REQUEST)

        update_serializers = []
        for pk, payload in update_payloads:
            inst = existing_map[pk]
            payload = {k: v for k, v in payload.items() if k != "id"}  # never change id
            ser = UserTimeLineUpsertSerializer(instance=inst, data=payload, partial=True)
            ser.is_valid(raise_exception=True)
            update_serializers.append((inst, ser))

        # Apply + commit atomically
        with transaction.atomic():
            # 1) Creates
            created = UserTimeLine.objects.bulk_create(create_instances) if create_instances else []

            # 2) Updates
            if update_serializers:
                # Apply validated data to model instances
                for inst, ser in update_serializers:
                    for f, v in ser.validated_data.items():
                        setattr(inst, f, v)
                UserTimeLine.objects.bulk_update(
                    [inst for inst, _ in update_serializers], fields=self.UPDATABLE_FIELDS
                )

        # Build response in the same order as input
        created_iter = iter(created)
        result_instances = []
        for obj in items:
            pk = _norm_pk(obj.get("id")) if isinstance(obj, dict) else None
            if pk is None:
                result_instances.append(next(created_iter))
            else:
                result_instances.append(existing_map[pk])

        out_ser = UserTimeLineUpsertSerializer(result_instances, many=True)
        return Response(out_ser.data, status=status.HTTP_200_OK)


class UserTimeLineBulkUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        # Collect ids from payload (keep as strings for UUID safety)
        ids = [str(item.get("id")) for item in request.data if item.get("id") is not None]
        if not ids:
            return Response({"detail": "Each item must include id for update."}, status=status.HTTP_400_BAD_REQUEST)

        qs = UserTimeLine.objects.filter(id__in=ids)
        if qs.count() != len(ids):
            return Response({"detail": "Some IDs not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Reorder instances to match payload order
        by_id = {str(obj.id): obj for obj in qs}
        instances_ordered = [by_id[str(item["id"])] for item in request.data]

        # partial=True so we can send only the fields we want to change
        serializer = UserTimeLineSerializer(instances_ordered, data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        # Re-serialize updated instances
        return Response(UserTimeLineSerializer(instances, many=True).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return Response({"detail": "Expected a list of ids."}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = UserTimeLine.objects.filter(id__in=ids).delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)


class CustomUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserAttendanceListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination

    def get_queryset(self):
        qs = CustomUser.objects.filter(is_archived=False).exclude(role__in=["Parents", "Student"])
        employee = self.request.GET.get('employee')
        filial = self.request.GET.get("filial")

        if employee:
            qs = qs.filter(id=employee)
        if filial:
            qs = qs.filter(filial__id__in=filial)

        return qs.distinct()

    def list(self, request, *args, **kwargs):
        paginated_users = self.paginate_queryset(self.get_queryset())

        status = request.GET.get('status')
        is_weekend = request.GET.get('is_weekend')
        date = request.GET.get('date')
        from_date = request.GET.get('start_date')
        to_date = request.GET.get('end_date')
        is_archived = request.GET.get('is_archived')

        results = []

        for user in paginated_users:

            print(user.full_name)

            attendance_filter = Q(employee=user)

            if is_archived:
                attendance_filter &= Q(employee__is_archived=is_archived.capitalize())
            if status:
                attendance_filter &= Q(status=status)
            if is_weekend:
                attendance_filter &= Q(is_weekend=is_weekend.capitalize())
            if date:
                attendance_filter &= Q(date=parse_date(date))
            if from_date:
                attendance_filter &= Q(date__gte=from_date)
            if from_date and to_date:
                attendance_filter &= Q(date__lte=to_date)

            # Step 1: Get all Employee_attendance for the user
            emp_attendance_qs = Employee_attendance.objects.filter(attendance_filter)

            stuff_attendance_set = []
            for emp_att in emp_attendance_qs:
                for att in emp_att.attendance.filter(action="In_side"):
                    stuff_attendance_set.append(att)

            serialized_tt_data = Stuff_AttendanceSerializer(stuff_attendance_set, many=True).data
            timeline = TimeTrackerSerializer(emp_attendance_qs, many=True).data
            groups_only = [item.get("groups") for item in timeline]

            results.append({
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                },
                "tt_data": serialized_tt_data,
                "groups": groups_only,
            })

        return self.get_paginated_response(results)


class TimeTrackerStatisticsListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date = request.GET.get("date")

        if date:
            date = parse_date(date)
            filters = {"date": date}
        else:
            filters = {}

        in_office_count = Employee_attendance.objects.filter(status="In_office", **filters).count()
        gone_count = Employee_attendance.objects.filter(status="Gone", **filters).count()
        absent_count = Employee_attendance.objects.filter(status="Absent", **filters).count()

        return Response({
            "in_office": in_office_count,
            "gone": gone_count,
            "absent": absent_count,
        }, status=200)
