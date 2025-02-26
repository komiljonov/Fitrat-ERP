from django.urls import include, path

from data.dashboard.views import DashboardView, MarketingChannels, Room_place, DashboardLineGraphAPIView, \
    MonitoringView, DashboardWeeklyFinanceAPIView, ArchivedView

urlpatterns = [
    path('admin/',DashboardView.as_view(), name='dashboard'),
    path("channels/",MarketingChannels.as_view(), name='marketing-channels'),
    path("rooms/",Room_place.as_view(), name='rooms'),
    path("finance/",DashboardLineGraphAPIView.as_view(), name='dashboard-line-graph'),

    path('monitoring/',MonitoringView.as_view(), name='monitoring'),

    path("archive/",ArchivedView.as_view(), name='archived'),

    path('paychart/',DashboardWeeklyFinanceAPIView.as_view(), name='paychart'),

]