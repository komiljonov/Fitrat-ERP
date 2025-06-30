from datetime import datetime

from django.utils.dateparse import parse_datetime
from icecream import ic
from rest_framework import status
from rest_framework.exceptions import NotFound
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
from .utils import calculate_amount, delete_user_actions, get_updated_datas
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

            total_amount = att_amount.get("total_eff_amount")

            emp_att = Employee_attendance.objects.filter(
                employee=user,
                date=date,
            ).first()

            delete_actions = delete_user_actions(user, actions)
            print(delete_actions)

            if not emp_att:
                emp_att = Employee_attendance.objects.create(
                    employee=user,
                    date=date,
                    amount=0
                )

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
                    actions=actions,
                )

                if attendance:
                    emp_att.attendance.add(attendance)
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


class TimeLineBulkCreate(CreateAPIView):
    serializer_class = UserTimeLineSerializer

    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
