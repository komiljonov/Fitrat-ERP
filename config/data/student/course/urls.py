from django.urls import path, include

from .views import *

urlpatterns = [
    path('',CourseList.as_view()),
    path('<uuid:pk>/',CourseDetail.as_view()),
    path('no-pg/',CourseNoPG.as_view()),

]