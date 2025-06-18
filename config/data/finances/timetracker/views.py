from datetime import datetime, date
from typing import List, Optional

from django.core.handlers.base import logger
from django.db import transaction
from django.db.models import Min
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from icecream import ic
from pyasn1_modules.rfc7906 import aa_manifest
from rest_framework import status, serializers
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
from .utils import get_monthly_per_minute_salary, calculate_penalty, update_calculate
from ..finance.models import Kind, Finance
from ...account.models import CustomUser


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
        try:
            ic(request.data)
            return self._process_attendance_with_error_handling(request.data)
        except AttendanceError as e:
            logger.error(f"Attendance error: {e.message}", extra=e.details)
            return Response({
                'error': e.message,
                'error_code': e.error_code,
                'details': e.details
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in attendance processing: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_attendance_with_error_handling(self, data: dict) -> Response:
        """Process attendance data with comprehensive error handling"""

        # Validate required fields
        self._validate_required_fields(data)

        # Extract and validate actions
        actions = self._validate_and_parse_actions(data.get('actions', []))


        with transaction.atomic():
            try:

                attendance_result = self._create_or_update_attendance(data)
                user = CustomUser.objects.filter(second_user=data.get("employee")).first()

                penalty_result = self._process_action_penalties(
                    user.id,
                    actions,
                    data.get('check_in'),
                    data.get('check_out')
                )

                return Response({
                    'success': True,
                    'attendance': attendance_result,
                    'penalty_calculation': penalty_result,
                    'message': 'Attendance processed successfully'
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Transaction failed: {str(e)}")
                raise AttendanceError(
                    "Failed to process attendance data",
                    "TRANSACTION_ERROR",
                    {'original_error': str(e)}
                )

    def _validate_required_fields(self, data: dict) -> None:
        """Validate required fields in attendance data"""
        required_fields = ['employee', 'date']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            raise AttendanceError(
                f"Missing required fields: {', '.join(missing_fields)}",
                "MISSING_FIELDS",
                {'missing_fields': missing_fields}
            )

        # Validate employee exists
        try:
            employee = CustomUser.objects.get(second_user=data['employee'])
        except CustomUser.DoesNotExist:
            raise AttendanceError(
                "Employee not found",
                "EMPLOYEE_NOT_FOUND",
                {'employee_id': data['employee']}
            )

    def _validate_and_parse_actions(self, actions: List[dict]) -> List[dict]:
        """Validate and parse actions data with error handling"""
        if not actions:
            return []

        validated_actions = []

        for i, action in enumerate(actions):
            try:
                # Validate required action fields
                required_action_fields = ['start', 'end', 'type', 'duration']
                missing_fields = [field for field in required_action_fields if field not in action]

                if missing_fields:
                    raise AttendanceError(
                        f"Action {i + 1} missing fields: {', '.join(missing_fields)}",
                        "INVALID_ACTION_DATA",
                        {'action_index': i, 'missing_fields': missing_fields}
                    )

                # Parse and validate datetime strings
                try:
                    start_time = self._parse_datetime_safe(action['start'])
                    end_time = self._parse_datetime_safe(action['end'])
                except ValueError as e:
                    raise AttendanceError(
                        f"Invalid datetime format in action {i + 1}",
                        "INVALID_DATETIME",
                        {'action_index': i, 'error': str(e)}
                    )

                # Validate duration consistency
                calculated_duration = (end_time - start_time).total_seconds()
                provided_duration = float(action['duration'])

                if abs(calculated_duration - provided_duration) > 60:  # Allow 1 minute tolerance
                    logger.warning(
                        f"Duration mismatch in action {i + 1}: calculated={calculated_duration}, provided={provided_duration}")

                # Validate action type
                valid_types = ['INSIDE', 'OUTSIDE']
                if action['type'] not in valid_types:
                    raise AttendanceError(
                        f"Invalid action type '{action['type']}' in action {i + 1}",
                        "INVALID_ACTION_TYPE",
                        {'action_index': i, 'valid_types': valid_types}
                    )

                validated_actions.append({
                    **action,
                    'start_datetime': start_time,
                    'end_datetime': end_time,
                    'duration_seconds': calculated_duration
                })

            except AttendanceError:
                raise
            except Exception as e:
                raise AttendanceError(
                    f"Error processing action {i + 1}: {str(e)}",
                    "ACTION_PROCESSING_ERROR",
                    {'action_index': i, 'error': str(e)}
                )

        # Sort actions by start time
        try:
            validated_actions.sort(key=lambda x: x['start_datetime'])
        except Exception as e:
            raise AttendanceError(
                "Failed to sort actions by time",
                "SORT_ERROR",
                {'error': str(e)}
            )

        return validated_actions

    def _parse_datetime_safe(self, datetime_str: str) -> datetime:
        """Safely parse datetime string with multiple format support"""
        datetime_formats = [
            "%Y_%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

        # Clean the string
        cleaned_str = datetime_str.replace('_', '-').strip()

        for fmt in datetime_formats:
            try:
                return datetime.strptime(cleaned_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse datetime: {datetime_str}")

    def _create_or_update_attendance(self, data: dict) -> dict:
        """Create or update attendance record with error handling"""
        try:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                attendance = serializer.save()
                return serializer.data
            else:
                raise AttendanceError(
                    "Invalid attendance data",
                    "SERIALIZER_ERROR",
                    {'validation_errors': serializer.errors}
                )
        except Exception as e:
            if isinstance(e, AttendanceError):
                raise
            raise AttendanceError(
                "Failed to create attendance record",
                "ATTENDANCE_CREATION_ERROR",
                {'error': str(e)}
            )

    def _process_action_penalties(self, employee_id: str, actions: List[dict],
                                  check_in: str, check_out: str) -> dict:
        """Process penalties/bonuses for individual actions"""
        try:
            if not actions:
                return {'total_penalty': 0, 'details': []}

            # Get user salary info
            penalty_info = self._get_penalty_calculation_info(employee_id)
            if not penalty_info:
                return {'total_penalty': 0, 'details': [], 'warning': 'No salary info found'}

            total_penalty = 0
            total_bonuses = 0
            penalty_details = []

            # Process each OUTSIDE action individually
            for i, action in enumerate(actions):
                if action['type'] == 'OUTSIDE' and action.get('usable', True):
                    try:
                        penalty_result = self._calculate_outside_penalty(
                            employee_id,
                            action,
                            penalty_info,
                            i + 1
                        )

                        total_penalty += penalty_result['penalty_amount']
                        penalty_details.append(penalty_result)

                    except Exception as e:
                        logger.error(f"Error calculating penalty for action {i + 1}: {str(e)}")
                        penalty_details.append({
                            'action_index': i + 1,
                            'error': f"Failed to calculate penalty: {str(e)}",
                            'penalty_amount': 0
                        })
                if action['type'] == 'INSIDE':
                    try:
                        if check_in and check_out:
                            today = now().date()

                            earliest_check_in = Stuff_Attendance.objects.filter(
                                employee__id=employee_id,
                                check_in__date=today
                            ).aggregate(Min('check_in'))['check_in__min']

                            attendance = Stuff_Attendance.objects.filter(
                                employee__id=employee_id,
                                check_in=earliest_check_in
                            ).first()

                            if attendance:
                                today = date.today()
                                day_name = today.strftime('%A')

                                timeline = UserTimeLine.objects.filter(
                                    user=attendance.employee,  # assuming attendance.employee is the user
                                    day=day_name
                                ).order_by('start_time').first()

                                if timeline:
                                    # Get actual check-in time (only time part)
                                    actual_check_in_time = attendance.check_in.time()
                                    scheduled_start_time = timeline.start_time

                                    # Calculate the difference
                                    from datetime import datetime, timedelta

                                    # Convert times to datetime objects for comparison
                                    today_datetime = datetime.combine(today, datetime.min.time())
                                    actual_datetime = datetime.combine(today, actual_check_in_time)
                                    scheduled_datetime = datetime.combine(today, scheduled_start_time)

                                    # Calculate time difference in minutes
                                    time_difference = (actual_datetime - scheduled_datetime).total_seconds() / 60

                                    if time_difference < 0:

                                        early_minutes = abs(time_difference)

                                        amount = early_minutes * penalty_info['penalty_amount']

                                        total_bonuses += amount
                                        employee = timeline.user
                                        comment = f"{employee.full_name} ning ishga {early_minutes} minut erta kelganligi uchun {amount} sum bonus"

                                        penalty_kind = Kind.objects.filter(
                                            action="EXPENSE",
                                            name__icontains="Bonus"
                                        ).first()

                                        Finance.objects.create(
                                            action="EXPENSE",
                                            kind=penalty_kind,
                                            amount=amount,
                                            stuff=employee,
                                            comment=comment
                                        )

                                        penalty_details.append(total_bonuses)
                                    elif time_difference > 0:
                                        # User was late
                                        late_minutes = time_difference

                                        amount = late_minutes * penalty_info['penalty_amount']

                                        total_penalty += amount
                                        employee = timeline.user
                                        comment = f"{employee.full_name} ning ishga {late_minutes} minut kech kelganligi uchun {amount} sum jarima"

                                        penalty_kind = Kind.objects.filter(
                                            action="EXPENSE",
                                            name__icontains="Money back"
                                        ).first()

                                        Finance.objects.create(
                                            action="INCOME",
                                            kind=penalty_kind,
                                            amount=amount,
                                            stuff=employee,
                                            comment=comment
                                        )

                                        penalty_details.append(total_penalty)
                                    else:
                                        # User was on time
                                        print("User was on time")
                                        status = "on_time"
                                        minutes_difference = 0


                        bonus_results = self._calculate_work_bonus(
                            employee_id,
                            action,
                            penalty_info,
                            i + 1
                        )
                        total_bonuses += bonus_results['bonus_amount']
                        penalty_details.append(bonus_results)
                    except Exception as e:
                        logger.error(f"Error calculating bonus for action {i + 1}: {str(e)}")
                        penalty_details.append({
                            'action_index': i + 1,
                            'error': f"Failed to calculate bonus: {str(e)}",
                            'bonus_amount': 0
                        })

            return {
                'total_penalty': round(total_penalty, 2),
                'details': penalty_details,
                'penalty_info': penalty_info
            }

        except Exception as e:
            logger.error(f"Error in penalty processing: {str(e)}")
            return {
                'total_penalty': 0,
                'details': [],
                'error': f"Penalty calculation failed: {str(e)}"
            }

    def _get_penalty_calculation_info(self, employee_id: str) -> Optional[dict]:
        """Get penalty calculation information for employee"""
        try:
            penalty_info = get_monthly_per_minute_salary(employee_id)
            return penalty_info if penalty_info.get('per_minute_salary', 0) > 0 else None
        except Exception as e:
            logger.error(f"Error getting penalty info for employee {employee_id}: {str(e)}")
            return None

    def _calculate_work_bonus(self,employee_id: str, action: dict,
                                   penalty_info: dict, action_index: int):
        try:
            duration_minutes = action['duration_seconds'] / 60
            per_minute_bonus = penalty_info.get('per_minute_salary', 0)
            bonus_amount = duration_minutes * per_minute_bonus

            try:
                self._create_bonus_finance_record(
                    employee_id,
                    bonus_amount,
                    action['start_datetime'],
                    action['end_datetime'],
                    duration_minutes
                )
                finance_created=True
            except Exception as e:
                logger.error(f"Error creating bonus record: {str(e)}")
                finance_created = False
            return {
                'action_index': action_index,
                'start_time': action['start'],
                'end_time': action['end'],
                'duration_minutes': round(duration_minutes, 2),
                'bonus_amount': round(bonus_amount, 2),
                'per_minute_bonus': per_minute_bonus,
                'finance_record_created': finance_created
            }
        except Exception as e:
            raise AttendanceError(
                f"Failed to calculate bonus for action {action_index}",
                "BONUS_CALCULATION_ERROR",
                {'action_index': action_index, 'error': str(e)}
            )

    def _calculate_outside_penalty(self, employee_id: str, action: dict,
                                   penalty_info: dict, action_index: int) -> dict:
        """Calculate penalty for individual OUTSIDE action"""
        try:
            duration_minutes = action['duration_seconds'] / 60
            per_minute_penalty = penalty_info.get('per_minute_salary', 0)

            # Calculate penalty amount
            penalty_amount = duration_minutes * per_minute_penalty

            # Create finance record for this specific outside period
            try:
                self._create_penalty_finance_record(
                    employee_id,
                    penalty_amount,
                    action['start_datetime'],
                    action['end_datetime'],
                    duration_minutes
                )
                finance_created = True
            except Exception as e:
                logger.error(f"Failed to create finance record: {str(e)}")
                finance_created = False

            return {
                'action_index': action_index,
                'start_time': action['start'],
                'end_time': action['end'],
                'duration_minutes': round(duration_minutes, 2),
                'penalty_amount': round(penalty_amount, 2),
                'per_minute_penalty': per_minute_penalty,
                'finance_record_created': finance_created
            }

        except Exception as e:
            raise AttendanceError(
                f"Failed to calculate penalty for action {action_index}",
                "PENALTY_CALCULATION_ERROR",
                {'action_index': action_index, 'error': str(e)}
            )

    def _create_penalty_finance_record(self, employee_id: str, amount: float,
                                       start_time: datetime, end_time: datetime,
                                       duration_minutes: float) -> None:
        """Create or update attendance and finance record for penalty."""
        try:
            user = CustomUser.objects.get(id=employee_id)

            # Ensure start and end times are timezone-aware
            if timezone.is_naive(start_time):
                start_time = timezone.make_aware(start_time)
            if timezone.is_naive(end_time):
                end_time = timezone.make_aware(end_time)

            # Check if identical attendance already exists
            att = Stuff_Attendance.objects.filter(
                employee=user,
                check_in=start_time,
                check_out=end_time,
                amount=amount
            ).first()

            if att:
                logger.info("Attendance record already exists — skipping creation.")
                return  # Skip if exact attendance already exists

            # Find or create penalty Kind
            penalty_kind = Kind.objects.filter(
                action="EXPENSE",
                name__icontains="Money back"
            ).first()

            if not penalty_kind:
                raise ValueError("Penalty Kind with action='EXPENSE' and name like 'Bonus' not found.")

            # Build comment for finance record
            comment = (
                f"Bugun {start_time.strftime('%H:%M')} dan {end_time.strftime('%H:%M')} "
                f"gacha {duration_minutes:.0f} minut tashqarida bo'lganingiz uchun "
                f"{amount:.2f} sum jarima yozildi!"
            )

            # Check if a matching Finance record already exists
            existing_finance = Finance.objects.filter(
                action="EXPENSE",
                kind=penalty_kind,
                amount=amount,
                stuff=user,
                comment=comment
            ).exists()

            if existing_finance:
                logger.info("Finance record already exists — skipping creation.")
                return  # Skip if the same finance record exists

            # Create new attendance
            att = Stuff_Attendance.objects.create(
                employee=user,
                check_in=start_time,
                check_out=end_time,
                amount=amount,
            )

            # Link to Employee_attendance
            attendance_date = start_time.date()
            employee_att, _ = Employee_attendance.objects.get_or_create(
                employee=user,
                date=attendance_date,
                defaults={'amount': 0}
            )

            # Add this Stuff_Attendance if not already linked
            if not employee_att.attendance.filter(id=att.id).exists():
                employee_att.attendance.add(att)
                employee_att.amount -= amount
                employee_att.save()

            # Create finance penalty record
            Finance.objects.create(
                action="INCOME",
                kind=penalty_kind,
                amount=amount,
                stuff=user,
                comment=comment
            )

        except Exception as e:
            logger.error(f"Failed to create penalty finance record: {str(e)}")
            raise

    def _create_bonus_finance_record(self, employee_id: str, amount: float,start_time: datetime, end_time: datetime,
                                       duration_minutes: float) -> None:
        try:
            user = CustomUser.objects.get(id=employee_id)

            # Ensure start and end times are timezone-aware
            if timezone.is_naive(start_time):
                start_time = timezone.make_aware(start_time)
            if timezone.is_naive(end_time):
                end_time = timezone.make_aware(end_time)

            # Check if identical attendance already exists
            att = Stuff_Attendance.objects.filter(
                employee=user,
                check_in=start_time,
                check_out=end_time,
                amount=amount
            ).first()

            if att:
                logger.info("Attendance record already exists — skipping creation.")
                return  # Skip if exact attendance already exists

            # Find or create penalty Kind
            penalty_kind = Kind.objects.filter(
                action="EXPENSE",
                name__icontains="Bonus"
            ).first()

            if not penalty_kind:
                raise ValueError("Penalty Kind with action='EXPENSE' and name like 'Bonus' not found.")

            # Build comment for finance record
            comment = (
                f"Bugun {start_time.strftime('%H:%M')} dan {end_time.strftime('%H:%M')} "
                f"gacha {duration_minutes:.0f} minut ishda bo'lganingiz uchun "
                f"{amount:.2f} sum bonus yozildi!"
            )

            # Check if a matching Finance record already exists
            existing_finance = Finance.objects.filter(
                action="EXPENSE",
                kind=penalty_kind,
                amount=amount,
                stuff=user,
                comment=comment
            ).exists()

            if existing_finance:
                logger.info("Finance record already exists — skipping creation.")
                return  # Skip if the same finance record exists

            # Create new attendance
            att = Stuff_Attendance.objects.create(
                employee=user,
                check_in=start_time,
                check_out=end_time,
                amount=amount,
            )

            # Link to Employee_attendance
            attendance_date = start_time.date()
            employee_att, _ = Employee_attendance.objects.get_or_create(
                employee=user,
                date=attendance_date,
                defaults={'amount': 0}
            )

            # Add this Stuff_Attendance if not already linked
            if not employee_att.attendance.filter(id=att.id).exists():
                employee_att.attendance.add(att)
                employee_att.amount += amount
                employee_att.save()

            # Create finance penalty record
            Finance.objects.create(
                action="EXPENSE",
                kind=penalty_kind,
                amount=amount,
                stuff=user,
                comment=comment
            )

        except Exception as e:
            logger.error(f"Failed to create penalty finance record: {str(e)}")
            raise


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
                # Get the attendance record
                attendance = self.get_object()
                previous_check_in = attendance.check_in
                previous_check_out = attendance.check_out
                previous_amount = attendance.amount or 0

                # Calculate previous per-minute amount if check-in/out existed
                previous_per_minute_amount = 0
                if previous_check_in and previous_check_out:

                    amount = calculate_penalty(
                        user_id=attendance.employee.id,
                        check_in=data.get("check_in"),
                        check_out=data.get("check_out"),
                    )

                    print(amount)

                    previous_per_minute_amount = update_calculate(
                        attendance.employee.id,
                        previous_check_in,
                        previous_check_out
                    ) / max(1, (previous_check_out - previous_check_in).total_seconds() / 60)

                # Update the attendance record
                serializer = self.get_serializer(attendance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                updated_attendance = serializer.save()

                # Calculate new penalty amount
                new_penalty = update_calculate(
                    updated_attendance.employee.id,
                    updated_attendance.check_in,
                    updated_attendance.check_out
                )

                # Calculate per-minute amount for new check-in/out
                new_per_minute_amount = 0
                if updated_attendance.check_in and updated_attendance.check_out:
                    new_per_minute_amount = new_penalty / max(1, (
                                updated_attendance.check_out - updated_attendance.check_in).total_seconds() / 60)

                # Calculate difference from previous amount
                amount_difference = new_penalty - previous_amount

                # Update the attendance amount
                updated_attendance.amount = new_penalty
                updated_attendance.save()

                # Update related finance records if needed
                if amount_difference != 0:
                    self._update_finance_records(
                        employee=updated_attendance.employee,
                        date=updated_attendance.check_in.date() if updated_attendance.check_in else None,
                        prev_amount=previous_amount,
                        new_amount=new_penalty,
                        check_in=updated_attendance.check_in,
                        check_out=updated_attendance.check_out
                    )

                # Update Employee_attendance
                if updated_attendance.check_in:
                    self._update_employee_attendance(
                        updated_attendance.employee,
                        updated_attendance.check_in.date(),
                        updated_attendance,
                        previous_amount,
                        new_penalty
                    )

                return Response({
                    'success': True,
                    'attendance': serializer.data,
                    'penalty_calculation': {
                        'previous_amount': previous_amount,
                        'new_amount': new_penalty,
                        'difference': amount_difference,
                        'previous_per_minute_amount': round(previous_per_minute_amount, 4),
                        'new_per_minute_amount': round(new_per_minute_amount, 4),
                        'per_minute_difference': round(new_per_minute_amount - previous_per_minute_amount, 4)
                    },
                    'message': 'Attendance updated successfully',
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e),
                'error_code': 'UPDATE_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)

    def _update_employee_attendance(self, employee, date, attendance, prev_amount, new_amount):
        """Update the employee's attendance record with the new amount"""
        employee_att, created = Employee_attendance.objects.get_or_create(
            employee=employee,
            date=date,
            defaults={'amount': new_amount}
        )

        if not created:
            employee_att.amount -= prev_amount
            employee_att.amount += new_amount
            employee_att.save()

        if not employee_att.attendance.filter(id=attendance.id).exists():
            employee_att.attendance.add(attendance)

    def _update_finance_records(self, employee, date, prev_amount, new_amount, check_in, check_out):
        """Update related finance records with the new amount"""
        if not date:
            return {'updated': 0}

        # More flexible matching - look for records close to the previous amount
        finance_records = Finance.objects.filter(
            stuff=employee,
            action="EXPENSE",
            kind__action="EXPENSE",
            kind__name__icontains="Bonus",
            created_at__date=date,
            amount=prev_amount,
        ).order_by('-created_at')

        updated_count = 0
        duration_minutes = (check_out - check_in).total_seconds() / 60 if check_in and check_out else 0


        if finance_records.exists():
            finance = finance_records.first()
            finance.amount = new_amount
            finance.comment = (
                f"Updated: {check_in.strftime('%H:%M')} to {check_out.strftime('%H:%M')} "
                f"({duration_minutes:.0f} minutes) penalty adjusted from "
                f"{prev_amount:.2f} to {new_amount:.2f}"
            )
            finance.save()
            updated_count = 1

        return {
            'previous_amount': prev_amount,
            'new_amount': new_amount,
            'updated': updated_count
        }


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
