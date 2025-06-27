from datetime import datetime, date
from typing import List, Optional

from django.core.handlers.base import logger
from django.db import transaction
from django.db.models import Min
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from icecream import ic
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
from .utils import get_monthly_per_minute_salary, calculate_amount
from ..finance.models import Kind, Finance
from ...account.models import CustomUser
from ...student import attendance


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


class AttendanceError(Exception):
    """Custom exception for attendance-related errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "ATTENDANCE_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AttendanceList(ListCreateAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)

        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        date = request.data.get('date')
        employee = request.data.get('employee')
        actions = request.data.get('actions')

        filters = {}
        if check_out:
            filters['check_out'] = check_out

        user = CustomUser.objects.filter(second_user=employee).first()
        if not user:
            return Response(
                "User not found",
                status=status.HTTP_404_NOT_FOUND
            )

        if actions is None:
            att = Stuff_Attendance.objects.filter(
                employee__id=employee,
                date=date,
                first_check_in=check_in,
                **filters
            )
            if att:
                return Response(
                    "attendance exists",
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif check_in and actions and check_out is None:

            sorted_actions = sorted(actions, key=lambda x: x['start'])

            sorted_actions = sorted_actions[0]

            att = Stuff_Attendance.objects.filter(
                employee__id=employee,
                date=date,
                first_check_in=sorted_actions.get('start'),
                first_check_out=sorted_actions.get('end'),
            ).first()
            if att:
                return Response(
                    "attendance exists",
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif check_in and actions and check_out:

            sorted_actions = sorted(actions, key=lambda x: x['start'])

            sorted_actions = sorted_actions[0]

            att = Stuff_Attendance.objects.filter(
                employee__id=employee,
                date=date,
                first_check_in=sorted_actions.get('start'),
                first_check_out=sorted_actions.get('end'),
            ).first()
            if att:
                return Response(
                    "attendance exists",
                    status=status.HTTP_400_BAD_REQUEST
                )

        return self.create_attendance(request.data)

    def create_attendance(self, data):
        actions = data.get('actions')
        employee = data.get('employee')
        date = data.get('date')

        if actions:
            sorted_actions = sorted(actions, key=lambda x: x['start'])

            print(employee)

            user = CustomUser.objects.filter(second_user=employee).first()

            att_amount = calculate_amount(
                user=user,
                actions=sorted_actions,
            )

            total_amount = att_amount.get("total_amount")

            emp_att = Employee_attendance.objects.filter(
                employee=user,
                date=date,
            ).first()
            if not emp_att:
                emp_att = Employee_attendance.objects.create(
                    employee=user,
                    date=date,
                    attendance=[],
                    amount=0
                )

            for action in sorted_actions:

                attendance = Stuff_Attendance.objects.create(
                    employee=user,
                    check_in=action.get('start'),
                    check_out=action.get('end'),
                    date=date,
                    action="In_side" if action.get("type") == "INSIDE" else "Outside",
                    actions=actions,
                )

                if attendance:
                    emp_att.attendance.add(attendance)
                    emp_att.amount += att_amount

            emp_att.amount=total_amount
            emp_att.save()
        return Response("Attendance created", status=status.HTTP_201_CREATED)


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Stuff_Attendance.objects.all()
    serializer_class = Stuff_AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            attendance_id = data.get('id') or kwargs.get('pk')

            if not attendance_id:
                return Response({
                    'error': 'Attendance id is required for update',
                    'error_code': 'MISSING_ID'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                attendance = self.get_object()

                previous_amount = attendance.amount or 0


                self._remove_existing_financial_impact(attendance, previous_amount)

                serializer = self.get_serializer(attendance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                updated_attendance = serializer.save()
                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAisdfhugoidsfhugodisfhugsdfg")

                new_penalty = calculate_amount(
                    updated_attendance.employee.id,
                    updated_attendance.check_in,
                    updated_attendance.check_out
                ) if updated_attendance.check_in and updated_attendance.check_out else 0

                ic(new_penalty)

                updated_attendance.amount = new_penalty
                updated_attendance.save()

                em_att, created = Employee_attendance.objects.get_or_create(
                    employee=updated_attendance.employee,
                    date=updated_attendance.date,
                    defaults={'amount': 0}
                )

                if not em_att.attendance.filter(id=updated_attendance.id).exists():
                    em_att.attendance.add(updated_attendance)

                # Update the amount by first subtracting the previous amount and adding the new penalty
                em_att.amount = (em_att.amount or 0) - (previous_amount or 0) + (new_penalty or 0)
                em_att.save()

                return Response({
                    'success': True,
                    'attendance': serializer.data,
                    'penalty_calculation': {
                        'previous_amount': previous_amount,
                        'new_amount': new_penalty,
                        'difference': new_penalty - previous_amount,
                    },
                    'message': 'Attendance updated successfully',
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error updating attendance: {str(e)}", exc_info=True)
            return Response({
                'error': str(e),
                'error_code': 'UPDATE_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)

    def _remove_existing_financial_impact(self, attendance,previs_amount):
        """Remove all financial impact of the existing attendance record"""
        if not attendance.check_in:
            return

        date = attendance.check_in.date()
        employee = attendance.employee

        # 1. Remove from Employee_attendance
        try:
            employee_att = Employee_attendance.objects.get(
                employee=employee,
                date=date
            )
            employee_att.amount -= attendance.amount or 0
            employee_att.save()

            # Remove the attendance record from the relationship
            employee_att.attendance.remove(attendance)

            # Delete if no more attendance records and amount is zero
            if employee_att.amount == 0 and not employee_att.attendance.exists():
                employee_att.delete()
        except Employee_attendance.DoesNotExist:
            pass

        # 2. Delete related finance records

        print("finance logs",Finance.objects.filter(
            stuff=employee,
            amount=previs_amount,
        ).first())

        print(employee)
        print(previs_amount)

        Finance.objects.filter(
            stuff=employee,
            created_at__date=date,
            amount=previs_amount,
            comment__contains=f"{attendance.check_in.strftime('%H:%M')} dan {attendance.check_out.strftime('%H:%M')}"
        ).delete()

    def _parse_datetime_safe(self, datetime_str):
        """Parse datetime string with timezone support"""
        if isinstance(datetime_str, datetime):
            return datetime_str

        try:
            # Handle ISO format with timezone
            if '+' in datetime_str or '-' in datetime_str.split('T')[-1]:
                return datetime.fromisoformat(datetime_str)
            # Handle simple format
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {datetime_str}") from e


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
