from django.urls import include, path

from data.dashboard.views import DashboardView, MarketingChannels

urlpatterns = [
    path('admin',DashboardView.as_view(), name='dashboard'),
    path("channels",MarketingChannels.as_view(), name='marketing-channels'),
]