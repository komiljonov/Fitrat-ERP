from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from ..account.models import CustomUser


class NotificationListAPIView(ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = CustomUser.objects.filter(id=self.request.user.id).first()
        return Notification.objects.filter(user=user)

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

        is_read = self.request.GET.get('is_read')
        has_read = self.request.GET.get('has_read')
        if is_read:
            qs = qs.filter(is_read=is_read.capitalize())
        if has_read:
            qs = qs.filter(has_read=has_read.capitalize())
        return

    def get_paginated_response(self, data):
        return Response(data)
