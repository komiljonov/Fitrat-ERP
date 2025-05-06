from django.urls import path

from .views import TeacherList, TeachersNoPGList, TeacherDetail, TeacherScheduleView, TeachersGroupsView, \
    TeacherStatistics, AsistantTeachersView, AssistantStatisticsView, TeacherMasteringStatisticsView, \
    SecondaryGroupStatic

urlpatterns = [
    path('', TeacherList.as_view()),
    path('pg/', TeachersNoPGList.as_view()),
    path('<uuid:pk>/', TeacherDetail.as_view()),

    path('statistics/', TeacherStatistics.as_view()),

    path('schedule/',TeacherScheduleView.as_view()),
    path('groups/',TeachersGroupsView.as_view()),

    path('secondary/',AsistantTeachersView.as_view()),
    path('secondary/statistics/',AssistantStatisticsView.as_view()),

    path('mastering/',TeacherMasteringStatisticsView.as_view()),

    path("statis/",SecondaryGroupStatic.as_view()),

]
