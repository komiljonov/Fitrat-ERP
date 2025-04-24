from django.urls import path

from .views import PaymeWebHookAPIView


urlpatterns = [
    path("update/", PaymeWebHookAPIView.as_view())
]
