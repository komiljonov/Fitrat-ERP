from django.urls import path
from .views import ThemeNoPgListAPIView


urlpatterns = [path("no-pg", ThemeNoPgListAPIView.as_view())]
