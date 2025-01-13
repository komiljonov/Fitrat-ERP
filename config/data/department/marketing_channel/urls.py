from django.urls import path
from .views import MarketingChannelList,MarketingChannelNOPG,MarketingChannelDetail

urlpatterns = [
    path("", MarketingChannelList.as_view(), name="marketing_channel_list"),
    path("<uuid:pk>/", MarketingChannelDetail.as_view(), name="marketing_channel_detail"),
    path("no-pg/", MarketingChannelNOPG.as_view(), name="marketing_channelNOPG"),
]