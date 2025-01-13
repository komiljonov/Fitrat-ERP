from django.urls import path

from .views import DublListNoPGView,DublListAPIView,DublRetrieveAPIView


urlpatterns = [
    path('no-pg/', DublListNoPGView.as_view(), name='dubl-list'),
    path('<uuid:pk>/', DublRetrieveAPIView.as_view(), name='dubl-retrieve'),
    path('', DublListAPIView.as_view(), name='dubl-list'),
]
