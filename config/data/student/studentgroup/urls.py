from django.urls import path

from .views import StudentGroupDetail, StudentGroupNopg, StudentsGroupList

urlpatterns = [
    path('', StudentsGroupList.as_view()),
    path('<uuid:pk>/', StudentGroupDetail.as_view()),
    path('no-pg/', StudentGroupNopg.as_view()),

]