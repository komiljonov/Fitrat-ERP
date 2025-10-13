from django.urls import path
from .views import ThemeNoPgListAPIView


urlpatterns = [path("theme/no-pg", ThemeNoPgListAPIView.as_view())]
