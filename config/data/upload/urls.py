from django.urls import path
from .views import *

urlpatterns = [
    path('upload/',UploadFileAPIView.as_view()),
]