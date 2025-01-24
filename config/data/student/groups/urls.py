from django.urls import path
from .views import StudentGroupsView, StudentRetrieveUpdateDestroyAPIView, StudentListAPIView, GroupLessonScheduleView, \
    TeachersGroupsView

urlpatterns = [
    path('', StudentGroupsView.as_view(), name='group-list'),
    path('<uuid:pk>/', StudentRetrieveUpdateDestroyAPIView.as_view(), name='group-detail'),
    path('no-pg/',StudentListAPIView.as_view(), name='no-pg-list'),

    path('teacher/<uuid:pk>/', TeachersGroupsView.as_view(), name='student-detail'),


    path('<uuid:pk>/schedule/',GroupLessonScheduleView.as_view(), name='group-schedule'),
]