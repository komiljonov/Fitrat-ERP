from rest_framework.urls import path

from .views import *

urlpatterns = [
    path("", ArchivedListAPIView.as_view(), name="archived"),
    path("<uuid:pk>/", ArchivedDetailAPIView.as_view(), name="archived-detail"),
    path("no-pg/", ListArchivedListNOPgAPIView.as_view(), name="archived-no-pg"),
    path("students/", StudentArchivedListAPIView.as_view(), name="students"),
    path("stuff/", StuffArchive.as_view(), name="stuff"),
    path("frozen/", FrozenListCreateList.as_view(), name="frozen"),
    path("frozen/<uuid:pk>", FrozenDetailAPIView.as_view(), name="frozen-detail"),
    path("excel/", ExportLidsExcelView.as_view(), name="archived"),
    path("static/", LidStudentArchivedStatistics.as_view(), name="static"),
]
