from django.urls import path

from .views import NotificationListAPIView, NotificationListNoPG, NotificationRetrieveUpdateDestroyAPIView, \
    MarkAllNotificationsReadAPIView, UserRFTokenListCreateAPIView

urlpatterns = [
    path('',NotificationListAPIView.as_view()),
    path('<uuid:pk>',NotificationRetrieveUpdateDestroyAPIView.as_view()),
    path('no-pg/',NotificationListNoPG.as_view()),

    path("mark-all-read/",MarkAllNotificationsReadAPIView.as_view()),

    path("rftoken/", UserRFTokenListCreateAPIView.as_view()),
    path("rftoken/<uuid:pk>", UserRFTokenRetrieveUpdateDestroyAPIView.as_view()),

]