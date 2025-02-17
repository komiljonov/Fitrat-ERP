from django.urls import include, path

from data.dashboard.views import DashboardView

urlpatterns = [
    path('admin',DashboardView.as_view(), name='dashboard'),
]