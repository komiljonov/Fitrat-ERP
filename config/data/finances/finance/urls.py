from django.urls import path

from .views import FinanceListAPIView, FinanceDetailAPIView, FinanceNoPGList, StudentFinanceListAPIView, \
    StuffFinanceListAPIView, CasherListCreateAPIView

urlpatterns = [
    path('', FinanceListAPIView.as_view(), name='finance_list'),
    path('<uuid:pk>/', FinanceDetailAPIView.as_view(), name='finance_detail'),
    path('no-pg/', FinanceNoPGList.as_view(), name='finance_nopg'),

    path('student/<uuid:pk>/',StudentFinanceListAPIView.as_view(), name='finance_student'),
    path('stuff/<uuid:pk>/',StuffFinanceListAPIView.as_view(), name='finance_stuff'),

    path('casher',CasherListCreateAPIView.as_view(), name='finance_casher'),
    path('casher/<uuid:pk>/',CasherListCreateAPIView.as_view(), name='finance_casher'),

]