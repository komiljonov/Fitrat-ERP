from django.urls import path

from .views import *
from ..groups.views import LessonScheduleWebListApi

urlpatterns = [
    # path('', LessonList.as_view(), name='student-list'),
    # path('<uuid:pk>/', LessonDetail.as_view(), name='student-detail'),
    # path('no-pg/',LessonNoPG.as_view(), name='no-pg'),
    path('schedule/',AllLessonsView.as_view(), name='schedule'),

    path('first-lesson/' , FistLessonView.as_view(), name='first-lesson'),

    path('first-lesson/<uuid:pk>/',FirstLessonView.as_view(), name='student-fist'),

    path('extra/',ExtraLessonView.as_view(), name='extra'),
    path('extra/<uuid:pk>/',ExtraLessonView.as_view(), name='extra'),

    path('group-extra/',ExtraLessonGroupView.as_view(), name='extra-group'),
    path('group-extra/<uuid:pk>/',ExtraLessonGroupView.as_view(), name='extra-group-uuid'),
]