from django.urls import path

from .views import StudentListView, StudentDetailView, StudentListNoPG, StudentScheduleView, \
    ExportLidToExcelAPIView, StudentStatistics, StudentAllStatistics, FistLesson_dataList, FirstLesson_dataListRetrive

urlpatterns = [
    path('', StudentListView.as_view(), name='student-list'),
    path('<uuid:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('no-pg/', StudentListNoPG.as_view(), name='student-no-pg'),

    path('schedule/<uuid:pk>/', StudentScheduleView.as_view(), name='student-schedule'),


    path('statistics/', StudentStatistics.as_view(), name='student-statistics'),

    path('excel/', ExportLidToExcelAPIView.as_view(), name='student-excel'),

    path('statistics/all', StudentAllStatistics.as_view(), name='student-statistics'),

    path("first/lesson/data",FistLesson_dataList.as_view(),name="first-lesson-data"),
    path("first/lesson/data/<uuid:pk>/",FirstLesson_dataListRetrive.as_view(),name="first-lesson-data"),
]