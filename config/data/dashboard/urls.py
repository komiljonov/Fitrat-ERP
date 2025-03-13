from django.urls import include, path

from data.dashboard.views import DashboardView, MarketingChannels, CheckRoomFillingView, DashboardLineGraphAPIView, \
    MonitoringView, DashboardWeeklyFinanceAPIView, ArchivedView, MonitoringExcelDownloadView, SalesApiView, \
    FinanceStatisticsApiView, StudentLanguage, ExportDashboardToExcelAPIView

urlpatterns = [
    path('admin/',DashboardView.as_view(), name='dashboard'),
    path("channels/",MarketingChannels.as_view(), name='marketing-channels'),
    path("room-filling/",CheckRoomFillingView.as_view(), name='check-room-lesson-schedule'),
    path("finance/",DashboardLineGraphAPIView.as_view(), name='dashboard-line-graph'),

    path('monitoring/',MonitoringView.as_view(), name='monitoring'),

    path('monitoring/excel',MonitoringExcelDownloadView.as_view(), name='monitoring-excel'),

    path("archive/",ArchivedView.as_view(), name='archived'),

    path('paychart/',DashboardWeeklyFinanceAPIView.as_view(), name='paychart'),

    path("sales/",SalesApiView.as_view(), name='sales'),

    path("finance-kind/",FinanceStatisticsApiView.as_view(), name='finance-statistics'),

    path("student-lang/",StudentLanguage.as_view(), name='student-lang'),

    path("finance-excel/",ExportDashboardToExcelAPIView.as_view(), name='finance-excel'),
]