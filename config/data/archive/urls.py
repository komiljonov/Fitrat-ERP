from django.urls import path

from .views import ArchiveListAPIView, ArchiveRetrieveDestroyAPIView


urlpatterns = [
    path("", ArchiveListAPIView.as_view()),
    path("<uuid:pk>", ArchiveRetrieveDestroyAPIView.as_view()),
]
