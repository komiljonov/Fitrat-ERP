from django.urls import path

from .views import StudentGroupDetail, StudentGroupNopg, StudentsGroupList, GroupStudentList, GroupStudentDetail

urlpatterns = [
    path('', StudentsGroupList.as_view()),
    path('<uuid:pk>/', StudentGroupDetail.as_view()),
    path('no-pg/', StudentGroupNopg.as_view()),

    path('group/<uuid:pk>/', GroupStudentList.as_view()),

    path('student/<uuid:pk>/', GroupStudentDetail.as_view()),
]