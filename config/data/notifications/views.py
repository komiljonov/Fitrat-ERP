from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, UserRFToken
from .serializers import NotificationSerializer, UserRFTokenSerializer
from data.account.models import CustomUser


class NotificationListAPIView(ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = CustomUser.objects.filter(id=self.request.user.id).first()
        qs = Notification.objects.filter(user=user)

        is_read = self.request.GET.get("is_read")
        has_read = self.request.GET.get("has_read")
        if is_read:
            qs = qs.filter(is_read=is_read.capitalize())
        if has_read:
            qs = qs.filter(has_read=has_read.capitalize())
        return qs


class NotificationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]


class NotificationListNoPG(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)

        is_read = self.request.GET.get("is_read")
        has_read = self.request.GET.get("has_read")
        if is_read:
            qs = qs.filter(is_read=is_read.capitalize())
        if has_read:
            qs = qs.filter(has_read=has_read.capitalize())
        return qs

    def get_paginated_response(self, data):
        return Response(data)


class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = notifications.update(is_read=True)

        return Response(
            {"message": f"{updated_count} notifications marked as read."},
            status=status.HTTP_200_OK,
        )


class UserRFTokenListCreateAPIView(ListCreateAPIView):
    serializer_class = UserRFTokenSerializer
    queryset = UserRFToken.objects.all()

    def get_queryset(self):
        return UserRFToken.objects.filter(user=self.request.user)


class UserRFTokenRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserRFTokenSerializer
    queryset = UserRFToken.objects.all()
    permission_classes = [IsAuthenticated]
