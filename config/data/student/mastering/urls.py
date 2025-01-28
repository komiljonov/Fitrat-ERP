from django.urls import include, path

from .views import MasteringList, MasteringNoPG, MasteringDetail

urlpatterns = [
    path('', MasteringList.as_view(), name='mastering_list'),
    path('<uuid:pk>', MasteringDetail.as_view(), name='mastering_detail'),
    path("no-pg/", MasteringNoPG.as_view(), name='mastering_nopg'),
]