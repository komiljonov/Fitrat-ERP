from django.urls import path

from .views import StudentListView, StudentDetailView, StudentListNoPG, StudentScheduleView, StudentLoginAPIView, \
    ExportLidToExcelAPIView, StudentStatistics

urlpatterns = [
    path('', StudentListView.as_view(), name='student-list'),
    path('<uuid:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('no-pg/', StudentListNoPG.as_view(), name='student-no-pg'),

    path('schedule/<uuid:pk>/', StudentScheduleView.as_view(), name='student-schedule'),

    path('auth/',StudentLoginAPIView.as_view(), name='student-login'),

    path('statistics/', StudentStatistics.as_view(), name='student-statistics'),

    path('excel/', ExportLidToExcelAPIView.as_view(), name='student-excel'),

]