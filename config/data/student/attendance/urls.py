from django.urls import path

from .views import *

urlpatterns = [
    path('', AttendanceList.as_view(), name='student-attendance'),
    path('<uuid:pk>/', AttendanceDetail.as_view(), name='attendance-detail'),
    path('student/<uuid:pk>/', AttendanceListView.as_view(), name='student-attendance-list'),
    path('lesson/<uuid:pk>/', LessonAttendanceList.as_view(), name='lesson-list'),
    path("lesson/secondary/<uuid:pk>/",LessonSecondaryAttendanceList.as_view(), name='lesson-secondary-list'),

    path("bulk/",AttendanceBulkList.as_view(), name='bulk-attendance-list'),

    path("bulk/update",AttendanceBulkUpdateAPIView.as_view(), name='bulk-update-attendance-list'),

    path("secondary/",SecondaryAttendanceList.as_view(), name='secondary-attendance-list'),
    path("secondary/<uuid:pk>",SecondaryAttendanceDetail.as_view(), name='secondary-attendance-detail'),

    # path('filter/',FilterAttendanceView.as_view(), name='filter-attendance'),
]