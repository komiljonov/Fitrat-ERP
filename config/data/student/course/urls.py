from django.urls import path, include

from .views import *
from ..subject.views import ThemeList
from ...teachers.teacher.views import TeacherList

urlpatterns = [
    path('',CourseList.as_view()),
    path('<uuid:pk>/',CourseDetail.as_view()),
    path('no-pg/',CourseNoPG.as_view()),

    path('students/<uuid:pk>/',StudentCourse.as_view()),

    path('theme/<uuid:pk>/',CourseTheme.as_view()),

    path('teachers/<uuid:pk>/',CourseTeacher.as_view()),

]