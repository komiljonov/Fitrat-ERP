from django.urls import path

from .views import TeacherList,TeachersNoPGList,TeacherDetail

urlpatterns = [
    path('', TeacherList.as_view()),
    path('pg/', TeachersNoPGList.as_view()),
    path('<uuid:pk>/', TeacherDetail.as_view()),
]
