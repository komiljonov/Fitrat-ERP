from django.urls import path
from .views import StudentGroupsView, StudentRetrieveUpdateDestroyAPIView, StudentListAPIView, GroupLessonScheduleView

urlpatterns = [
    path('', StudentGroupsView.as_view(), name='group-list'),
    path('<int:pk>/', StudentRetrieveUpdateDestroyAPIView.as_view(), name='group-detail'),
    path('no-pg/',StudentListAPIView.as_view(), name='no-pg-list'),

    path('<uuid:pk>/schedule/',GroupLessonScheduleView.as_view(), name='group-schedule'),
]