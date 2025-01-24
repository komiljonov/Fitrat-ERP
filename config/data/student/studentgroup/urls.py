from django.urls import path

from .views import StudentGroupDetail, StudentGroupNopg, StudentsGroupList, GroupStudentList

urlpatterns = [
    path('', StudentsGroupList.as_view()),
    path('<uuid:pk>/', StudentGroupDetail.as_view()),
    path('no-pg/', StudentGroupNopg.as_view()),

    path('group/<uuid:pk>/', GroupStudentList.as_view()),
]