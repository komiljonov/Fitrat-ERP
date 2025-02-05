from django.urls import path

from .views import *

urlpatterns = [
    path('', AttendanceList.as_view(), name='student-attendance'),
    path('<uuid:pk>/', AttendanceDetail.as_view(), name='attendance-detail'),
    path('student/<uuid:pk>/', AttendanceListView.as_view(), name='student-attendance-list'),
    path('lesson/<uuid:pk>/', LessonAttendanceList.as_view(), name='lesson-list'),

    # path('filter/',FilterAttendanceView.as_view(), name='filter-attendance'),
]