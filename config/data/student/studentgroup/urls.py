from django.urls import path

from .views import StudentGroupDetail, StudentGroupNopg, StudentsGroupList, GroupStudentList, GroupStudentDetail, \
    SecondaryStudentList, SecondaryGroupList, GroupStudentStatistics, GroupAttendedStudents, StudentGroupDelete, \
    SecondaryGroupStudentList, SecondaryStudentGroupDelete, StudentGroupStatistics, SecondaryStudentCreate
from ...teachers.teacher.views import Teacher_StudentsView

urlpatterns = [
    path('', StudentsGroupList.as_view()),
    path('<uuid:pk>/', StudentGroupDetail.as_view()),
    path('no-pg/', StudentGroupNopg.as_view()),

    path('group/<uuid:pk>/', GroupStudentList.as_view()),

    path('secondarygroup/<uuid:pk>/', SecondaryGroupStudentList.as_view()),
    path('second/delete/<uuid:pk>/', SecondaryStudentGroupDelete.as_view()),

    path('is_attendant/<uuid:pk>/', GroupAttendedStudents.as_view()),

    path('student/<uuid:pk>/', GroupStudentDetail.as_view()),
    path('students/',Teacher_StudentsView.as_view()),

    path('secondary/',SecondaryStudentList.as_view()),

    path('secondary/<uuid:pk>/', SecondaryGroupList.as_view()),

    path('statistics/<uuid:pk>', GroupStudentStatistics.as_view()),

    path("delete/<uuid:pk>", StudentGroupDelete.as_view()),

    path("stats/", StudentGroupStatistics.as_view()),

    path("secondary/web",SecondaryStudentCreate.as_view()),

]