from django.urls import path

from .views import *

urlpatterns = [
    path('', LessonList.as_view(), name='student-list'),
    path('<int:pk>/', LessonDetail.as_view(), name='student-detail'),
    path('no-pg/',LessonNoPG.as_view(), name='no-pg'),
]