from django.urls import path

from .views import GroupStatisticsAPIView, StudentGroupPriceCreateAPIView


urlpatterns = [
    path("stats", GroupStatisticsAPIView.as_view()),
    path("price", StudentGroupPriceCreateAPIView.as_view()),
]
