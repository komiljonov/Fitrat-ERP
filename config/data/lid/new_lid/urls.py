from django.urls import path
from .views import LidListCreateView,LidRetrieveUpdateDestroyView,LidListNoPG

urlpatterns = [
    path('', LidListCreateView.as_view(), name='lid_list_create'),
    path('<uuid:pk>/', LidRetrieveUpdateDestroyView.as_view(), name='lid_retrieve'),
    path('no-pg/', LidListNoPG.as_view(), name='lid_list_pg'),
]