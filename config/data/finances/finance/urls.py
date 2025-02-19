from django.urls import path

from .views import FinanceListAPIView, FinanceDetailAPIView, FinanceNoPGList, StudentFinanceListAPIView, \
    StuffFinanceListAPIView, CasherListCreateAPIView, CasherRetrieveUpdateDestroyAPIView, CasherHandoverAPIView, \
    FinanceStatisticsAPIView, CasherNoPg, CasherHandoverHistory, CasherStatisticsAPIView, \
    TeacherGroupFinanceAPIView, FinanceTeacher, FinanceExcel

urlpatterns = [
    path('', FinanceListAPIView.as_view(), name='finance_list'),
    path('<uuid:pk>/', FinanceDetailAPIView.as_view(), name='finance_detail'),
    path('no-pg/', FinanceNoPGList.as_view(), name='finance_nopg'),

    path('student/<uuid:pk>/',StudentFinanceListAPIView.as_view(), name='finance_student'),
    path('stuff/<uuid:pk>/',StuffFinanceListAPIView.as_view(), name='finance_stuff'),

    path('casher',CasherListCreateAPIView.as_view(), name='finance_casher'),
    path('casher/<uuid:pk>/',CasherRetrieveUpdateDestroyAPIView.as_view(), name='finance_casher'),
    path('casher/no-pg/',CasherNoPg.as_view(), name='finance_casher_no-pg'),
    path('casher/stats/<uuid:pk>/',CasherStatisticsAPIView.as_view(), name='finance_casher_stats'),

    path('handover', CasherHandoverAPIView.as_view(), name='finance_handover'),
    path('handover/<uuid:pk>/', CasherHandoverHistory.as_view(), name='finance_handover_history'),

    path('statistics/', FinanceStatisticsAPIView.as_view(), name='finance_statistics'),
    path('teacher/<uuid:pk>/',TeacherGroupFinanceAPIView.as_view(), name='finance_teacher'),
    path('teachers/', FinanceTeacher.as_view(), name='finance_teacher'),

    path('excel/',FinanceExcel.as_view(), name='finance_excel'),

]