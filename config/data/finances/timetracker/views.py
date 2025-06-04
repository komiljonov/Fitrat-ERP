from django.utils.dateparse import parse_datetime
from icecream import ic  # For debug logging
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Employee_attendance
from .models import UserTimeLine, Stuff_Attendance
from .serializers import Stuff_AttendanceSerializer
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer
from .utils import calculate_penalty, parse_datetime_string


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


from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from django.utils import timezone
from datetime import timedelta
from icecream import ic


class AttendanceList(ListCreateAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer

    def create(self, request, *args, **kwargs):
        ic(request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee = data.get('employee')
        if not employee:
            return Response({"detail": "Employee is required."}, status=status.HTTP_400_BAD_REQUEST)

        check_in = data.get("check_in")
        check_out = data.get("check_out")
        date = data.get("date")
        not_marked = data.get("not_marked", False)
        att_status = data.get("status", None)
        actions = data.get("actions", [])

        ic(actions)

        updated = False
        attendance = None

        # Case 1: All empty – create check-in now
        if not check_in and not check_out and not actions:
            now = timezone.now()
            attendance = Stuff_Attendance.objects.create(
                employee=employee,
                check_in=now,
                date=date or now.date(),
                not_marked=not_marked,
                status=att_status
            )

        # Case 2: Actions present
        elif actions:
            actions = actions.sort(key=lambda x: x['start'], reverse=True)

            ic("sorted",actions)

            first_action = actions[0]
            start = first_action.get("start")
            end = first_action.get("end")

            if start and end:
                start = parse_datetime_string(start)
                end = parse_datetime_string(end)

            if not start:
                return Response({"detail": "'start' required in first action."}, status=status.HTTP_400_BAD_REQUEST)

            # Try to update existing attendance
            att_qs = Stuff_Attendance.objects.filter(
                check_in=start,
                employee=employee,
                date=date
            )

            if att_qs.exists():
                attendance = att_qs.first()
                if end:
                    attendance.check_out = end
                attendance.actions = actions
                attendance.save()
                updated = True
            else:
                # Create new attendance
                attendance = Stuff_Attendance.objects.create(
                    employee=employee,
                    check_in=start,
                    check_out=end,
                    date=date,
                    not_marked=not_marked,
                    status=att_status,
                    actions=actions
                )

        # Case 3: Direct check_in + check_out
        elif check_in and check_out:
            exists = Stuff_Attendance.objects.filter(
                check_in=check_in,
                check_out=check_out,
                employee=employee,
                date=date
            ).exists()
            if exists:
                return Response({"detail": "Attendance already exists."}, status=status.HTTP_400_BAD_REQUEST)

            attendance = Stuff_Attendance.objects.create(
                employee=employee,
                check_in=check_in,
                check_out=check_out,
                date=date,
                not_marked=not_marked,
                status=att_status
            )

        else:
            return Response({"detail": "Invalid or incomplete data."}, status=status.HTTP_400_BAD_REQUEST)

        # Compute and assign penalty
        amount = calculate_penalty(
            user_id=attendance.employee.id,
            check_in=attendance.check_in,
            check_out=attendance.check_out
        )
        ic(amount)
        attendance.amount = amount
        attendance.save()

        # Update or create employee attendance summary
        emp_attendance, created = Employee_attendance.objects.get_or_create(
            employee=employee,
            date=attendance.date,
            defaults={"status": "In_office"},
        )
        emp_attendance.amount += attendance.amount
        emp_attendance.save()
        emp_attendance.attendance.add(attendance)

        return Response(
            {
                "updated": updated,
                "created": not updated,
                "attendance": self.get_serializer(attendance).data,
                "amount": attendance.amount
            },
            status=status.HTTP_201_CREATED
        )


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


class TimeLineBulkCreate(CreateAPIView):
    serializer_class = UserTimeLineSerializer

    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
