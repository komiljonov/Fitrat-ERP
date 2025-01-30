from .views import *
from django.urls import path, include

urlpatterns = [
    path('university/',UniversityResultsViewSet.as_view()),
    path('university/<uuid:pk>/',UniversityResultsRetrieveAPIView.as_view()),
    path('university/no-pg/',UniversityResultsNoPg.as_view()),

    path('certificate/', CertificationResultsViewSet.as_view()),
    path('certificate/<uuid:pk>/',CertificationResultsRetrieveAPIView.as_view()),
    path('certificate/no-pg/', CertificationResultsNoPg.as_view()),

    path('all/',ResultsViewSet.as_view()),
]