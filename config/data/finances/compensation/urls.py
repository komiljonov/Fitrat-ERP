from django.urls import path

from .views import (
    BonusList, BonusDetail, BonusNoPG, CompensationList, CompensationDetail, CompensationNoPG,
    PageCreateView, PageBulkUpdateView, AsosListCreateView, StudentCountRetrieveView, ResultsNameListCreateView,
    AsosListRetrieveView, AsosNoPGListView, MonitoringBulkCreateView, MonitoringRetrieveView,
    PointListCreateView, PointRetrieveView, PointNoPGListView, MonitoringListCreateView,
    Asos4ListCreateView, ResultSubjectRetrieveView, StudentCountMonitoringListCreateView, MonitoringAsosListCreateView,
    CommentsListCreateView, Monitoring5List, MonitoringAsos_1_2List,
)

urlpatterns = [
    path('bonus/', BonusList.as_view()),
    path('bonus/<uuid:pk>/', BonusDetail.as_view()),
    path('bonus/no-pg/', BonusNoPG.as_view()),

    path('compensation/', CompensationList.as_view()),
    path('compensation/<uuid:pk>/', CompensationDetail.as_view()),
    path('compensation-no-pg/', CompensationNoPG.as_view()),

    path('pages/', PageCreateView.as_view()),
    path("pages/update/",PageBulkUpdateView.as_view()),

    path("asos/",AsosListCreateView.as_view()),
    path("asos/<uuid:pk>/",AsosListRetrieveView.as_view()),
    path("asos/no-pg/",AsosNoPGListView.as_view()),

    path("monitoring/", MonitoringBulkCreateView.as_view()),
    path("monitoring/list/",MonitoringListCreateView.as_view()),
    path("monitoring/<uuid:pk>/",MonitoringRetrieveView.as_view()),

    path("points-name/",ResultsNameListCreateView.as_view()),
    path("points/", PointListCreateView.as_view()),
    path("points/<uuid:pk>/",PointRetrieveView.as_view()),
    path("points/no-pg/", PointNoPGListView.as_view()),

    path("asos4/",Asos4ListCreateView.as_view()),
    path("asos4/<uuid:pk>/",ResultSubjectRetrieveView.as_view()),
    path("monitoring/asos4/", MonitoringAsosListCreateView.as_view()),

    path("asos5/",StudentCountMonitoringListCreateView.as_view()),
    path("asos5/<uuid:pk>/",StudentCountRetrieveView.as_view()),
    path("asos5/monitoring/", Monitoring5List.as_view()),

    path("comments/",CommentsListCreateView.as_view()),

    path("asos1/",MonitoringAsos_1_2List.as_view()),
    path("asos1/<uuid:pk>/",MonitoringRetrieveView.as_view()),

]