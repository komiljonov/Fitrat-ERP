from django.urls import path

from .views import FinanceListAPIView, FinanceDetailAPIView, FinanceNoPGList, StudentFinanceListAPIView, \
    StuffFinanceListAPIView

urlpatterns = [
    path('', FinanceListAPIView.as_view(), name='finans_list'),
    path('<uuid:pk>/', FinanceDetailAPIView.as_view(), name='finans_detail'),
    path('no-pg/', FinanceNoPGList.as_view(), name='finans_nopg'),

    path('student/<uuid:pk>/',StudentFinanceListAPIView.as_view(), name='finans_student'),
    path('stuff/<uuid:pk>/',StuffFinanceListAPIView.as_view(), name='finans_stuff'),

]