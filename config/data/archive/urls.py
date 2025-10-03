from django.urls import path

from .views import (
    ArchiveListAPIView,
    ArchiveRetrieveDestroyAPIView,
    ArchiveStatsAPIView,
)


urlpatterns = [
    path("", ArchiveListAPIView.as_view()),
    path("stats", ArchiveStatsAPIView.as_view()),
    path("<uuid:pk>", ArchiveRetrieveDestroyAPIView.as_view()),
]
