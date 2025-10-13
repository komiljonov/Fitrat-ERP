from django.urls import path

from .views import GroupListAPIView


urlpatterns = [
    path("", GroupListAPIView.as_view())
]
