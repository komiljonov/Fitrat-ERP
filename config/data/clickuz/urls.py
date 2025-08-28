from django.urls import include, path

from data.clickuz.views import ClickUzMerchantAPIView, CreateClickOrderAPIView

urlpatterns = [
    path("update/", ClickUzMerchantAPIView.as_view(), name="update"),
    path("order/", CreateClickOrderAPIView.as_view(), name="order"),
]
