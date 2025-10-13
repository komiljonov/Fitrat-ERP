from django.urls import path
from .views import ThemeNoPgListAPIView


urlpatterns = [path("themes/no-pg", ThemeNoPgListAPIView.as_view())]
