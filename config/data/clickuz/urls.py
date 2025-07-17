from django.urls import include, path

from data.clickuz.views import ClickUzMerchantAPIView

urlpatterns = [
    path("update/",ClickUzMerchantAPIView.as_view(), name="update"),
]