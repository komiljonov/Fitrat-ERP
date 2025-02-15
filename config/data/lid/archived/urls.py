from rest_framework.urls import path

from .views import *

urlpatterns = [
    path('', ArchivedListAPIView.as_view(), name='archived'),
    path('<uuid:pk>/', ArchivedDetailAPIView.as_view(), name='archived-detail'),
    path('no-pg/',ListArchivedListNOPgAPIView.as_view(), name='archived-no-pg'),

    path('students/', StudentArchivedListAPIView.as_view(), name='students'),

    path('stuff/', StuffArchive.as_view(), name='stuff'),
]