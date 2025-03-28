from .views import *
from django.urls import path, include

urlpatterns = [\

    path('university/',UniversityResultsViewSet.as_view()),
    path('university/<uuid:pk>/',UniversityResultsRetrieveAPIView.as_view()),
    path('university/no-pg/',UniversityResultsNoPg.as_view()),

    path('certificate/', CertificationResultsViewSet.as_view()),
    path('certificate/<uuid:pk>/',CertificationResultsRetrieveAPIView.as_view()),
    path('certificate/no-pg/', CertificationResultsNoPg.as_view()),

    path('all/',ResultsViewSet.as_view()),

    path('other/',OtherResultsViewSet.as_view()),
    path('other/<uuid:pk>/',OtherResultsRetrieveAPIView.as_view()),

    path('national/',NationalSertificateApi.as_view()),

    path('',ResultsView.as_view()),
    path('<uuid:pk>/',ResultsRetrieveAPIView.as_view()),

    path("student/",ResultStudentListAPIView.as_view()),
]