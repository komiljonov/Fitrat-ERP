from django.urls import path

from .views import StoresListView,StoreDetailView

urlpatterns = [
    path('store/',StoresListView.as_view()),
    path('store/<uuid:pk>',StoreDetailView.as_view()),
]