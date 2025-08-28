from django.urls import path
from .views import *

urlpatterns = [
    path('',ModeratorListAPIView.as_view(), name='moderator-list'),
    path('<uuid:pk>',ModeratorDetailAPIView.as_view(), name='moderator-detail'),
    path('no-pg/',ModeratorListNoPGView.as_view(), name='moderator-list-no-pg'),
    path('<uuid:pk>/students/',ModeratorStudentsListAPIView.as_view(), name='moderator-student-list'),
]