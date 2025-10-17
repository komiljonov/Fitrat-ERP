from django.urls import path

from .pdf_generater import ContractGenerateAPIView
from .views import (
    LeadListCreateView,
    LeadRetrieveUpdateDestroyView,
    LeadListNoPG,
    ExportLeadToExcelAPIView,
    LeadStatisticsView,
    BulkUpdate,
    LeadStatistics,
    LeadArchiveAPIView,
    LeadCreateOrderAPIView,
)
from .webhook import LeadWebhook

urlpatterns = [
    path("", LeadListCreateView.as_view(), name="lead_list_create"),
    # path("orders", OrderListCreateView.as_view(), name="lead_list_create"),
    path("<uuid:pk>", LeadRetrieveUpdateDestroyView.as_view(), name="lead_retrieve"),
    path("<uuid:pk>/archive", LeadArchiveAPIView.as_view()),
    path("<uuid:pk>/create_order", LeadCreateOrderAPIView.as_view()),
    path("no-pg/", LeadListNoPG.as_view(), name="lead_list_pg"),
    path("excel/", ExportLeadToExcelAPIView.as_view(), name="lead_list_excel"),
    path("statistic", LeadStatisticsView.as_view(), name="lead_statistic"),
    path("bulk-update", BulkUpdate.as_view(), name="bulk_update"),
    path("document", ContractGenerateAPIView.as_view(), name="contract_generate"),
    path("webhook", LeadWebhook.as_view(), name="lead_webhook"),
    path("stats", LeadStatistics.as_view(), name="lead_statistic"),
]
