from django.urls import path
from .views import MarketingChannelList, MarketingChannelNOPG, MarketingChannelDetail, GroupTypeList, GroupTypeDetail

urlpatterns = [
    path("", MarketingChannelList.as_view(), name="marketing_channel_list"),
    path("<uuid:pk>/", MarketingChannelDetail.as_view(), name="marketing_channel_detail"),
    path("no-pg/", MarketingChannelNOPG.as_view(), name="marketing_channelNOPG"),



    path("group/",GroupTypeList.as_view(), name="group_type_list"),
    path("group/<uuid:pk>/",GroupTypeDetail.as_view(), name="group_type_detail"),
]