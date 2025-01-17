from django.urls import path

from .views import NotificationListAPIView,NotificationListNoPG,NotificationRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('',NotificationListAPIView.as_view()),
    path('<uuid:pk>',NotificationRetrieveUpdateDestroyAPIView.as_view()),
    path('no-pg/',NotificationListNoPG.as_view()),
]