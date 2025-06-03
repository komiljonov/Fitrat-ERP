from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from icecream import ic
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Employee_attendance
from .models import UserTimeLine, Stuff_Attendance
from .serializers import Stuff_AttendanceSerializer
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer
from .utils import calculate_penalty

class TimeTrackerList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer

    def get_queryset(self):
        queryset = Employee_attendance.objects.all()

        employee = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        date = self.request.GET.get('date')
        is_weekend = self.request.GET.get('is_weekend')
        from_date = self.request.GET.get('start_date')
        to_date = self.request.GET.get('end_date')

        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if from_date and to_date:
            queryset = queryset.filter(date__gte=from_date,date__lte=to_date)

        if is_weekend:
            queryset = queryset.filter(is_weekend=is_weekend.capitalize())
        if employee:
            queryset = queryset.filter(employee__id=employee)
        if status:
            queryset = queryset.filter(status=status)
        if date:
            queryset = queryset.filter(date=parse_datetime(date))
        return queryset.order_by('date')


class AttendanceList(ListCreateAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ic(data)

        employee = data.get('employee')
        if not employee:
            return Response({"detail": "Employee is required."}, status=status.HTTP_400_BAD_REQUEST)

        check_in = data.get("check_in")
        check_out = data.get("check_out")
        date = data.get("date")
        not_marked = data.get("not_marked", False)
        att_status = data.get("status", None)

        if check_in and check_out is None:
            att = Stuff_Attendance.objects.filter(check_in=check_in,employee=employee,date=date).exists()
            if att:
                return Response({
                    "detail": "Attendance is already created."
                })

        elif check_in and check_out:
            att = Stuff_Attendance.objects.filter(
                check_in=check_in,
                employee=employee,
                date=date,
                check_out=check_out,
            ).exists()
            if att:
                return Response({
                    "detail": "Attendance is already created."
                })

        attendance = Stuff_Attendance.objects.create(
            employee=employee,
            check_in=check_in,
            check_out=check_out,
            date=date,
            not_marked=not_marked,
            status=att_status
        )

        amount = calculate_penalty(
            user_id=attendance.employee.id,
            check_in=check_in ,
            check_out=check_out

        )
        ic(amount)
        attendance.amount = amount
        attendance.save()
        ic(attendance.amount)
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        ic("------------------")
        emp_attendance, created = Employee_attendance.objects.get_or_create(
            employee=employee,
            date=date,
            defaults={"status": "In_office"},
        )
        emp_attendance.amount += attendance.amount
        emp_attendance.save()
        emp_attendance.attendance.add(attendance)

        return Response(
            {
                "created": created,
                "attendance": self.get_serializer(attendance).data,
                "amount": attendance.amount
            },
            status=status.HTTP_201_CREATED
        )


    def get_queryset(self):
        filial = self.request.GET.get('filial')
        user_id = self.request.GET.get('id')
        action = self.request.GET.get('action')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        queryset = Employee_attendance.objects.all()

        if start_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date))
        if start_date and end_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date),
                                       date__lte=parse_datetime(end_date))

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
            queryset = queryset.filter(user__id=user)

        if day:
            queryset = queryset.filter(day=day)
        return queryset


class UserTimeLineDetail(RetrieveUpdateDestroyAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer
    permission_classes = [IsAuthenticated]