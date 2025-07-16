from django.urls import path

from .views import ParentListView, ParentDetailView, RelativesListNoPGView, StudentsRelativesListView, \
    ParentsStudentsAPIView, ParentsNotificationsRetrieveAPIView, ParentRetrieveAPIView, ParentStudentAvgAPIView

urlpatterns = [
    path('', ParentListView.as_view()),
    path('<uuid:pk>', ParentDetailView.as_view()),
    path('no-pg/', RelativesListNoPGView.as_view()),
    path('student/<uuid:pk>', StudentsRelativesListView.as_view()),

    path("students/", ParentsStudentsAPIView.as_view()),

    path("parent-notifications/<uuid:user__id>", ParentsNotificationsRetrieveAPIView.as_view()),

    path("retrive/<uuid:user__id>",ParentRetrieveAPIView.as_view()),

    path("childrens/",ParentStudentAvgAPIView.as_view()),
]
