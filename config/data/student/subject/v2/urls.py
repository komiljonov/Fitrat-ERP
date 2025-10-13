from django.urls import path
from .views import ThemeNoPgListAPIView, ThemeReorderAPIView


urlpatterns = [
    path("themes/no-pg", ThemeNoPgListAPIView.as_view()),
    path("themes/reorder", ThemeReorderAPIView.as_view()),
]
