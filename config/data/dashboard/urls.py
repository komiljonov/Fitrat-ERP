from django.urls import include, path

from data.dashboard.views import DashboardView, MarketingChannels, CheckRoomFillingView, DashboardLineGraphAPIView, \
    MonitoringView, DashboardWeeklyFinanceAPIView, ArchivedView, GenerateExcelView, SalesApiView, \
    FinanceStatisticsApiView, StudentLanguage, ExportDashboardToExcelAPIView, AdminLineGraph, DashboardSecondView

urlpatterns = [
    path('admin/',DashboardView.as_view(), name='dashboard'),
    path("secondary-admin/",DashboardSecondView.as_view()),
    path("channels/",MarketingChannels.as_view(), name='marketing-channels'),
    path("room-filling/",CheckRoomFillingView.as_view(), name='check-room-lesson-schedule'),
    path("finance/",DashboardLineGraphAPIView.as_view(), name='dashboard-line-graph'),

    path('monitoring/',MonitoringView.as_view(), name='monitoring'),

    path('monitoring/excel',GenerateExcelView.as_view(), name='monitoring-excel'),

    path("archive/",ArchivedView.as_view(), name='archived'),

    path('paychart/',DashboardWeeklyFinanceAPIView.as_view(), name='paychart'),

    path("sales/",SalesApiView.as_view(), name='sales'),

    path("finance-kind/",FinanceStatisticsApiView.as_view(), name='finance-statistics'),

    path("student-lang/",StudentLanguage.as_view(), name='student-lang'),

    path("finance-excel/",ExportDashboardToExcelAPIView.as_view(), name='finance-excel'),

    path("admin-linegraph/",AdminLineGraph.as_view(), name='admin-linegraph')
]