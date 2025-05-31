from django.utils.dateparse import parse_datetime
from icecream import ic
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Employee_attendance, UserTimeLine
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer
from ...account.models import CustomUser


from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from .models import Employee_attendance, CustomUser
from .serializers import TimeTrackerSerializer

class AttendanceList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee_id = data.get('employee')
        if not employee_id:
            return Response({"detail": "Employee is required."}, status=status.HTTP_400_BAD_REQUEST)

        ic(data)
        user = CustomUser.objects.filter(second_user=employee_id).first()
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        date = data.get("date")
        not_marked = data.get("not_marked", False)  # Default to False if not provided

        filters = {
            "employee": user,
            "check_in": check_in,
            "date": date,
        }

        if check_out is not None:
            filters["check_out"] = check_out
        else:
            filters["check_out__isnull"] = True

        existing_attendance = Employee_attendance.objects.filter(**filters).first()
        if existing_attendance:
            return Response({
                "detail": "Attendance already exists.",
                "attendance_id": existing_attendance.id
            }, status=status.HTTP_200_OK)

        new_attendance = Employee_attendance.objects.create(
            employee=user,
            check_in=check_in,
            check_out=check_out,
            date=date,
            not_marked=not_marked
        )

        return Response({
            "detail": "Attendance created.",
            "attendance_id": new_attendance.id
        }, status=status.HTTP_201_CREATED)


    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        user_id = self.request.query_params.get('id')
        action = self.request.query_params.get('action')
        type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = Employee_attendance.objects.all()

        if start_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date))
        if start_date and end_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date),
                                       date__lte=parse_datetime(end_date))

        if type:
            queryset = queryset.filter(type=type)
        if action:
            queryset = queryset.filter(action=action)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if user_id:
            queryset = queryset.filter(employee_id=user_id)

        return queryset


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]


class UserTimeLineList(ListCreateAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer

    def get_queryset(self):
        queryset = UserTimeLine.objects.all()

        user = self.request.GET.get('user')
        day = self.request.GET.get('day')
        if user:
            queryset = queryset.filter(user_id=user)

        if day:
            queryset = queryset.filter(day=day)
        return queryset


class UserTimeLineDetail(RetrieveUpdateDestroyAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer
    permission_classes = [IsAuthenticated]