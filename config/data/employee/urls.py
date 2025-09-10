from django.urls import path
from .views import EmployeeListAPIView

urlpatterns = [path("", EmployeeListAPIView.as_view())]
