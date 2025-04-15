from django.urls import path

from .views import StoresListView, StoreDetailView, StudentHomeView, StudentDetailView, FinanceListView

urlpatterns = [
    path('store/',StoresListView.as_view()),
    path('store/<uuid:pk>',StoreDetailView.as_view()),
    path('home/',StudentHomeView.as_view()),

    path("student/<uuid:id>/",StudentDetailView.as_view()),
    path("finance/<uuid:id>/",FinanceListView.as_view()),
]