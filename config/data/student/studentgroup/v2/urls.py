from django.urls import path

from .views import GroupStatisticsAPIView


urlpatterns = [path("stats", GroupStatisticsAPIView.as_view())]
