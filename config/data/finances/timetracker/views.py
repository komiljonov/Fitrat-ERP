from django.db.models import Q
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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from django.utils import timezone
from datetime import timedelta
from icecream import ic


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


class AttendanceList(ListCreateAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer

    # def get_queryset(self):
    #     """
    #     Filter queryset based on query parameters for created/updated status
    #     """
    #     queryset = super().get_queryset()

        # Get query parameters
        # created_filter = self.request.query_params.get('created', None)
        # updated_filter = self.request.query_params.get('updated', None)
        # operation_type = self.request.query_params.get('operation_type', None)
        #
        # # Filter by creation status (you'll need to add this field to your model)
        # if created_filter is not None:
        #     if created_filter.lower() == 'true':
        #         # Filter for newly created records (assuming you have a 'was_created' field)
        #         queryset = queryset.filter(was_created=True)
        #     elif created_filter.lower() == 'false':
        #         queryset = queryset.filter(was_created=False)
        #
        # # Filter by update status
        # if updated_filter is not None:
        #     if updated_filter.lower() == 'true':
        #         # Records that have been updated (check_out is not null or actions exist)
        #         queryset = queryset.filter(
        #             Q(check_out__isnull=False) | Q(actions__isnull=False)
        #         )
        #     elif updated_filter.lower() == 'false':
        #         # Records that haven't been updated
        #         queryset = queryset.filter(check_out__isnull=True, actions__isnull=True)
        #
        # # Filter by operation type (create/update)
        # if operation_type:
        #     if operation_type.lower() == 'create':
        #         # Recently created records (last 24 hours as example)
        #         yesterday = timezone.now() - timezone.timedelta(days=1)
        #         queryset = queryset.filter(
        #             created_at__gte=yesterday,
        #             check_out__isnull=True
        #         )
        #     elif operation_type.lower() == 'update':
        #         # Records with check_out or actions (indicating updates)
        #         queryset = queryset.filter(
        #             Q(check_out__isnull=False) | Q(actions__isnull=False)
        #         )
        #
        # return queryset

    def create(self, request, *args, **kwargs):
        try:
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
            created = False
            attendance = None
            operation_type = "none"

            # SCENARIO 1: Check-in only (CREATE)
            if check_in and not check_out and not actions:
                now = timezone.now()

                att = Stuff_Attendance.objects.filter(
                    check_in=check_in,
                    check_out=None,
                    actions=None,
                    date=date,
                    employee=employee,
                ).first()

                if att:
                    return Response(
                        {"detail": "Attendance is already created."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                attendance = Stuff_Attendance.objects.create(
                    employee=employee,
                    check_in=check_in,
                    date=date,
                    check_out=check_out,
                    not_marked=not_marked,
                    status=att_status,
                    was_created=True  # Mark as newly created
                )
                created = True
                operation_type = "create"
                ic("Created new attendance:", attendance)

            # SCENARIO 2: Actions provided (UPDATE or CREATE)
            elif actions:
                actions = sorted(actions, key=lambda x: x['start'], reverse=True)
                ic("sorted", actions)

                first_action = actions[0]
                start = first_action.get("start")
                end = first_action.get("end")

                if start and end:
                    start = parse_datetime_string(start)
                    end = parse_datetime_string(end)

                if not start:
                    return Response(
                        {"detail": "'start' required in first action."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Try to update existing attendance
                att_qs = Stuff_Attendance.objects.filter(
                    check_in=start,
                    employee=employee,
                    date=date
                )

                if att_qs.exists():
                    # UPDATE existing record
                    attendance = att_qs.first()
                    if end:
                        attendance.check_out = end
                    attendance.actions = actions
                    attendance.was_created = False  # Mark as updated
                    attendance.save()
                    updated = True
                    operation_type = "update"
                    ic("Updated existing attendance:", attendance)
                else:
                    # CREATE new record
                    attendance = Stuff_Attendance.objects.create(
                        employee=employee,
                        check_in=start,
                        check_out=end,
                        date=date,
                        not_marked=not_marked,
                        status=att_status,
                        actions=actions,
                        was_created=True  # Mark as newly created
                    )
                    created = True
                    operation_type = "create"
                    ic("Created new attendance with actions:", attendance)

            # SCENARIO 3: Both check-in and check-out (CREATE)
            elif check_in and check_out:
                exists = Stuff_Attendance.objects.filter(
                    check_in=check_in,
                    check_out=check_out,
                    employee=employee,
                    date=date
                ).exists()

                if exists:
                    return Response(
                        {"detail": "Attendance already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                attendance = Stuff_Attendance.objects.create(
                    employee=employee,
                    check_in=check_in,
                    check_out=check_out,
                    date=date,
                    not_marked=not_marked,
                    status=att_status,
                    was_created=True  # Mark as newly created
                )
                created = True
                operation_type = "create"
                ic("Created complete attendance:", attendance)

            ic("Operation completed:", operation_type)

            # Calculate penalty amount
            amount = calculate_penalty(
                user_id=attendance.employee.id,
                check_in=attendance.check_in,
                check_out=attendance.check_out
            )
            ic("Calculated amount:", amount)
            attendance.amount = amount
            attendance.save()

            # Update or create employee attendance summary
            emp_attendance, emp_created = Employee_attendance.objects.get_or_create(
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
                    "created": created,
                    "operation_type": operation_type,
                    "attendance": self.get_serializer(attendance).data,
                    "amount": attendance.amount,
                    "employee_attendance_created": emp_created
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        except Exception as e:
            ic("Error occurred:", str(e))
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer
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

        return queryset.order_by("start_time")


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
