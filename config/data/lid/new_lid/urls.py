from django.urls import path

from .pdf_generater import ContractGenerateAPIView
from .views import LidListCreateView, LidRetrieveUpdateDestroyView, LidListNoPG, ExportLidToExcelAPIView, \
    LidStatisticsView, BulkUpdate, LidStatistics
from .webhook import WebhookView

urlpatterns = [
    path('', LidListCreateView.as_view(), name='lid_list_create'),
    path('<uuid:pk>/', LidRetrieveUpdateDestroyView.as_view(), name='lid_retrieve'),
    path('no-pg/', LidListNoPG.as_view(), name='lid_list_pg'),


    path('excel/',ExportLidToExcelAPIView.as_view(), name='lid_list_excel'),

    path('statistic/',LidStatisticsView.as_view(), name='lid_statistic'),

    path('bulk-update/',BulkUpdate.as_view(), name='bulk_update'),

    path("document/",ContractGenerateAPIView.as_view(), name="contract_generate"),

    path("webhook/",WebhookView.as_view(), name="lid_webhook"),

    path("stats/",LidStatistics.as_view(), name="lid_statistic"),
]