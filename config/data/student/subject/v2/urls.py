from django.urls import path
from .views import ThemeNoPgListAPIView, ThemeReorderAPIView, LevelReOrderAPIView


urlpatterns = [
    path("themes/no-pg", ThemeNoPgListAPIView.as_view()),
    path("themes/reorder", ThemeReorderAPIView.as_view()),
    path("levels/reorder", LevelReOrderAPIView.as_view()),
]
