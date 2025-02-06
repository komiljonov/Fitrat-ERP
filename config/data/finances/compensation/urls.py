from django.urls import path

from .views import (BonusList, BonusDetail, BonusNoPG
, CompensationList, CompensationDetail, CompensationNoPG, PagesList)

urlpatterns = [
    path('bonus/', BonusList.as_view()),
    path('bonus/<uuid:pk>/', BonusDetail.as_view()),
    path('bonus/no-pg/', BonusNoPG.as_view()),

    path('compensation/', CompensationList.as_view()),
    path('compensation/<uuid:pk>/', CompensationDetail.as_view()),
    path('compensation-no-pg/', CompensationNoPG.as_view()),

    path('pages/', PagesList.as_view()),
]