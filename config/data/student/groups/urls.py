from django.urls import path

from .views import StudentGroupsView, GroupRetrieveUpdateDestroyAPIView, GroupListAPIView, TeachersGroupsView, \
    RoomListAPIView, RoomRetrieveUpdateDestroyAPIView, RoomNoPG, SecondaryGroupsView, \
    SecondaryGroupRetrieveUpdateDestroyAPIView, SecondaryNoPG, DaysNoPG, DaysAPIView, LessonScheduleListApi, \
    GroupLessonScheduleView, LessonScheduleWebListApi, RoomFilterView, CheckRoomLessonScheduleView, \
    GroupIsActiveNowAPIView, SecondaryGroupIsActiveNowAPIView, StudentGroupIsActiveNowAPIView, \
    StudentSaleGroupListCreateAPIView, StudentSaleGroupDetailAPIView
from ..lesson.views import ExtraLessonScheduleView

urlpatterns = [
    path('', StudentGroupsView.as_view(), name='group-list'),
    path('<uuid:pk>/', GroupRetrieveUpdateDestroyAPIView.as_view(), name='group-detail'),
    path('no-pg/',GroupListAPIView.as_view(), name='no-pg-list'),

    path('teacher/<uuid:pk>/', TeachersGroupsView.as_view(), name='student-detail'),


    path('schedule/',LessonScheduleListApi.as_view(), name='group-schedule'),
    path('schedule-all/', LessonScheduleWebListApi.as_view(), name='schedule-all'),
    path('schedule-extra/',ExtraLessonScheduleView.as_view(), name='extra-lesson-schedule'),
    path('<uuid:pk>/schedule/',GroupLessonScheduleView.as_view(), name='group-schedule'),

    path("room-check/",CheckRoomLessonScheduleView.as_view(), name='check-room-lesson-schedule'),

    path("check/<uuid:pk>",GroupIsActiveNowAPIView.as_view(), name='check-group-is-active'),
    path("check/secondary/<uuid:pk>",SecondaryGroupIsActiveNowAPIView.as_view(), name='check-secondary-group-is-active'),
    path("check/student/<uuid:pk>",StudentGroupIsActiveNowAPIView.as_view(), name='student-groups'),

    path('room',RoomListAPIView.as_view(), name='room-list'),
    path('room/<uuid:pk>/', RoomRetrieveUpdateDestroyAPIView.as_view(), name='room-detail'),
    path('room/no-pg/',RoomNoPG.as_view(), name='room-no-pg-list'),
    path("room-filing/",RoomFilterView.as_view(), name='days-nopg-list'),

    path('secondary/',SecondaryGroupsView.as_view(), name='secondary-list'),
    path('secondary/<uuid:pk>/', SecondaryGroupRetrieveUpdateDestroyAPIView.as_view(),
         name='secondary-detail'),
    path('secondary/no-pg/',SecondaryNoPG.as_view(), name='secondary-no-pg-list'),


    path('days',DaysAPIView.as_view(), name='days-list'),
    path('days/no-pg',DaysNoPG.as_view(), name='days-no-pg-list'),

    path("group-sale/",StudentSaleGroupListCreateAPIView.as_view(), name='group-sale-list'),
    path("group-sale/<uuid:pk>",StudentSaleGroupDetailAPIView.as_view(), name='group-sale-detail'),
]