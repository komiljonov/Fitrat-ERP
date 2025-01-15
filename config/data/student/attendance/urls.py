from django.urls import path

from .views import *

urlpatterns = [
    path('', AttendanceList.as_view(), name='student-attendance'),
    path('<uuid:pk>/', AttendanceDetail.as_view(), name='attendance-detail'),
    path('student/<uuid:pk>/', StudentAttendanceList.as_view(), name='student-attendance-list'),
    path('lid/<uuid:pk>/', LidAttendanceList.as_view(), name='lid-attendance-list'),
]