import icecream
from django.shortcuts import render
from rest_framework import status

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from .serializers import MasteringSerializer, StuffMasteringSerializer
from .models import Mastering, MasteringTeachers
from ..attendance.models import Attendance
from ..subject.models import Theme, Level, GroupThemeStart
from ...account.models import CustomUser
from ...finances.finance.models import KpiFinance
from ...finances.finance.serializers import KpiFinanceSerializer
from ...notifications.models import Notification
from ...payme.exceptions import InvalidParamsError


class MasteringList(ListCreateAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]


class MasteringDetail(RetrieveUpdateDestroyAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save(updater=request.user)

        return Response(serializer.data)


class MasteringNoPG(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class MasteringQuizFilter(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = Mastering.objects.filter(test__id=quiz_id)
        if quiz:
            return quiz
        return Mastering.objects.none()


class TeacherMasteringList(ListAPIView):
    queryset = MasteringTeachers.objects.all()
    serializer_class = StuffMasteringSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        if id:
            return MasteringTeachers.objects.filter(teacher__id=id)
        return MasteringTeachers.objects.none()


class StuffMasteringList(ListCreateAPIView):
    queryset = KpiFinance.objects.all()
    serializer_class = KpiFinanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get('id')
        if id:
            return KpiFinance.objects.filter(user__id=id)
        return KpiFinance.objects.all()


class MasteringTeachersList(RetrieveUpdateDestroyAPIView):
    queryset = KpiFinance.objects.all()
    serializer_class = KpiFinanceSerializer
    permission_classes = [IsAuthenticated]


class MasteringStudentFilter(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        quiz_id = self.request.query_qaram.get('quiz_id')
        student = self.request.query_param.get('student')
        user = self.queryset.query_param.get('user')
        queryset = Mastering.objects.all()
        if quiz_id:
            queryset = queryset.filter(test__id=quiz_id)

        if student:
            queryset = queryset.filter(student__id=student)

        if user:
            queryset = queryset.filter(student__user__id=user)
        return queryset

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class ChangeGroupTheme(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        data = request.data

        group_id = data.get('group')
        course_id = data.get('course')
        theme_number = data.get('theme_number')
        starter_theme_id = data.get('starter_theme')
        level_id = data.get('level')

        theme = Theme.objects.filter(id=starter_theme_id).first()
        theme_order = Theme.objects.filter(
            level__id=level_id,
            course__id=course_id
        ).order_by("-created_at")[:theme_number]

        group = Group.objects.filter(id=group_id).first()
        if not group or not theme:
            return Response({"detail": "Invalid group or theme."}, status=status.HTTP_400_BAD_REQUEST)

        if theme_order and theme.id == theme_order.first().id:
            att = Attendance.objects.filter(group__id=group_id).first()

            att_theme_obj = att.theme.first() if att else None
            att_theme_id = att_theme_obj.id if att_theme_obj else None

            if att_theme_id == theme.id:
                return Response(
                    {
                        "invalid_data": True,
                        "detail": "Theme has already been attended"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated_theme = GroupThemeStart.objects.create(
                theme=theme,
                group=group,
            )

            if updated_theme:
                directors = CustomUser.objects.filter(role="DIRECTOR")

                for item in directors:
                    Notification.objects.create(
                        user=item,
                        comment=f"{group.name} guruhi davomad mavzusi {theme_number} - {theme.title} mavzusiga o'zgartirildi!",
                        choice="Students",
                        come_from=group.id,
                    )

                return Response({"detail": "Theme successfully updated."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid theme order or theme mismatch."}, status=status.HTTP_400_BAD_REQUEST)


