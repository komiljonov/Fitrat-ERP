from django.urls import path

from data.student.groups.v2.views import GroupChangeLevelAPIView, GroupListAPIView


urlpatterns = [
    path("", GroupListAPIView.as_view()),
    path("<uuid:pk>/move-next-level/", GroupChangeLevelAPIView.as_view())
]
