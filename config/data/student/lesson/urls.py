from django.urls import path

from .views import *
from ..student.views import StudentListView, StudentDetailView

urlpatterns = [
    path('', StudentListView.as_view(), name='student-list'),
    path('<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('no-pg/',LessonNoPG.as_view(), name='no-pg'),
]