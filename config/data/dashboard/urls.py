from django.urls import include, path

from data.dashboard.views import DashboardView, MarketingChannels, Room_place, DashboardLineGraphAPIView

urlpatterns = [
    path('admin/',DashboardView.as_view(), name='dashboard'),
    path("channels/",MarketingChannels.as_view(), name='marketing-channels'),
    path("rooms/",Room_place.as_view(), name='rooms'),
    path("finance/",DashboardLineGraphAPIView.as_view(), name='dashboard-line-graph'),
]