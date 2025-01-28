from rest_framework.urls import path

from .views import *

urlpatterns = [
    path('', ArchivedListAPIView.as_view(), name='archived'),
    path('<uuid:pk>/', ArchivedDetailAPIView.as_view(), name='archived-detail'),
    path('no-pg/',ListArchivedListNOPgAPIView.as_view(), name='archived-no-pg'),

    path('students/<uuid:pk>/', StudentArchivedListAPIView.as_view(), name='students'),
]