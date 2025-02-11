from django.urls import path

from .views import TeacherList, TeachersNoPGList, TeacherDetail, TeacherScheduleView, TeachersGroupsView, \
    TeacherStatistics, AsistantTeachersView

urlpatterns = [
    path('', TeacherList.as_view()),
    path('pg/', TeachersNoPGList.as_view()),
    path('<uuid:pk>/', TeacherDetail.as_view()),

    path('statistics/', TeacherStatistics.as_view()),

    path('schedule/',TeacherScheduleView.as_view()),
    path('groups/',TeachersGroupsView.as_view()),

    path('secondary/',AsistantTeachersView.as_view()),
]
