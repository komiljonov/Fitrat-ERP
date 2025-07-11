from django.urls import path

from .views import NotificationListAPIView, NotificationListNoPG, NotificationRetrieveUpdateDestroyAPIView, \
    MarkAllNotificationsReadAPIView

urlpatterns = [
    path('',NotificationListAPIView.as_view()),
    path('<uuid:pk>',NotificationRetrieveUpdateDestroyAPIView.as_view()),
    path('no-pg/',NotificationListNoPG.as_view()),

    path("notifications/mark-all-read/",MarkAllNotificationsReadAPIView.as_view()),
]