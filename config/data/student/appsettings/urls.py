from django.urls import path

from .views import StoresListView,StoreDetailView, StudentHomeView

urlpatterns = [
    path('store/',StoresListView.as_view()),
    path('store/<uuid:pk>',StoreDetailView.as_view()),

    path('home/',StudentHomeView.as_view())
]