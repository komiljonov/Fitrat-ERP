from datetime import datetime

from django.db.models import Prefetch, Q
from django.utils.dateparse import parse_datetime, parse_date
from icecream import ic
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee_attendance
from .models import UserTimeLine, Stuff_Attendance
from .serializers import Stuff_AttendanceSerializer
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


class TimeLineBulkCreate(CreateAPIView):
    serializer_class = UserTimeLineSerializer

    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserTimeLineBulkUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        ids = [item.get("id") for item in request.data if "id" in item]
        instances = list(UserTimeLine.objects.filter(id__in=ids))

        if len(instances) != len(ids):
            return Response({"detail": "Some IDs not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserTimeLineSerializer(instances, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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

        filial = self.request.GET.get("filial")
        if filial:
            qs = qs.filter(filial__id__in=filial)

        return qs

    def list(self, request, *args, **kwargs):
        paginated_users = self.paginate_queryset(self.get_queryset())

        # 🔍 Get filters from request
        employee = request.GET.get('employee')
        status = request.GET.get('status')
        date = request.GET.get('date')
        is_weekend = request.GET.get('is_weekend')
        from_date = request.GET.get('start_date')
        to_date = request.GET.get('end_date')
        is_archived = request.GET.get('is_archived')

        results = []

        for user in paginated_users:
            # 🔍 Filter Employee_attendance per user
            attendance_filter = Q(employee=user)

            if is_archived:
                attendance_filter &= Q(employee__is_archived=is_archived.capitalize())
            if employee:
                attendance_filter &= Q(employee__id=employee)
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

            attendance_qs = Stuff_Attendance.objects.filter(action="In_side").distinct()

            employee_attendance_qs = (
                Employee_attendance.objects
                .filter(attendance_filter)
                .prefetch_related(Prefetch("attendance", queryset=attendance_qs))
            ).distinct()

            user_data = {
                "id": user.id,
                "full_name": user.full_name,
            }
            attendance_data = TimeTrackerSerializer(employee_attendance_qs, many=True).data

            results.append({
                "user": user_data,
                "tt_data": attendance_data
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