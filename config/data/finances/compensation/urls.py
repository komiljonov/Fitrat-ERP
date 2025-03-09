from django.urls import path

from .views import (BonusList, BonusDetail, BonusNoPG
, CompensationList, CompensationDetail, CompensationNoPG, PageCreateView, PageBulkUpdateView, AsosListCreateView,
                    AsosListRetrieveView, AsosNoPGListView, MonitoringBulkCreateView, MonitoringRetrieveView)

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
    path("monitoring/<uuid:pk>/",MonitoringRetrieveView.as_view()),

]