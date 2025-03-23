from django.urls import path

from .models import PaymentMethod
from .views import FinanceListAPIView, FinanceDetailAPIView, FinanceNoPGList, StudentFinanceListAPIView, \
    StuffFinanceListAPIView, CasherListCreateAPIView, CasherRetrieveUpdateDestroyAPIView, CasherHandoverAPIView, \
    FinanceStatisticsAPIView, CasherNoPg, CasherHandoverHistory, CasherStatisticsAPIView, \
    TeacherGroupFinanceAPIView, FinanceTeacher, FinanceExcel, KindRetrive, KindList, PaymentMethodsRetrive, \
    PaymentMethodsList, PaymentStatistics, PaymentCasherStatistics, SalesList, SalesStudentList, SalesStudentsRetrive, \
    PaymentStatisticsByKind, SalesStudentNoPG, GeneratePaymentExcelAPIView, SaleStudentRetrieve, VoucherList, \
    VoucherRetrieve, VoucherNoPG, VoucherStudentRetrieve, VoucherStudentList

urlpatterns = [
    path('', FinanceListAPIView.as_view(), name='finance_list'),
    path('<uuid:pk>/', FinanceDetailAPIView.as_view(), name='finance_detail'),
    path('no-pg/', FinanceNoPGList.as_view(), name='finance_nopg'),

    path('student/<uuid:pk>/',StudentFinanceListAPIView.as_view(), name='finance_student'),
    path('stuff/<uuid:pk>/',StuffFinanceListAPIView.as_view(), name='finance_stuff'),

    path('casher/',CasherListCreateAPIView.as_view(), name='finance_casher'),
    path('casher/<uuid:pk>/',CasherRetrieveUpdateDestroyAPIView.as_view(), name='finance_casher'),
    path('casher/no-pg/',CasherNoPg.as_view(), name='finance_casher_no-pg'),
    path('casher/stats/<uuid:pk>/',CasherStatisticsAPIView.as_view(), name='finance_casher_stats'),

    path('handover', CasherHandoverAPIView.as_view(), name='finance_handover'),
    path('handover/<uuid:pk>/', CasherHandoverHistory.as_view(), name='finance_handover_history'),

    path('statistics/', FinanceStatisticsAPIView.as_view(), name='finance_statistics'),
    path('teacher/<uuid:pk>/',TeacherGroupFinanceAPIView.as_view(), name='finance_teacher'),
    path('teachers/', FinanceTeacher.as_view(), name='finance_teacher'),

    path('excel/',FinanceExcel.as_view(), name='finance_excel'),

    path('kind/',KindList.as_view(), name='finance_kind'),
    path('kind/<uuid:pk>/', KindRetrive.as_view(), name='finance_kind'),

    path('method/',PaymentMethodsList.as_view(), name='payment_method'),
    path('method/<uuid:pk>/', PaymentMethodsRetrive.as_view(), name='payment_method'),
    path('payment_statistics/',PaymentStatistics.as_view(), name='payment_method'),

    path('payment_casher/<uuid:pk>',PaymentCasherStatistics.as_view(), name='payment_casher'),

    path('sale/',SalesList.as_view(), name='sale'),

    path('sale-student/',SalesStudentList.as_view(), name='sale_student'),
    path("sale-student/<uuid:pk>/", SaleStudentRetrieve.as_view(), name="sale_student"),
    path("sale/no-pg/",SalesStudentNoPG.as_view(), name="sale_student"),
    path("sale-student/<uuid:pk>/",SalesStudentsRetrive.as_view(), name="sale_student"),

    path("payment-reason/",PaymentStatisticsByKind.as_view(), name="payment_kind"),

    path("finance/casher/excel/", GeneratePaymentExcelAPIView.as_view(), name="finance_casher_excel"),

    path("voucher/",VoucherList.as_view()),
    path("voucher/<uuid:pk>/",VoucherRetrieve.as_view()),
    path("voucher/no-pg/", VoucherNoPG.as_view()),

    path("voucher/student/",VoucherStudentList.as_view()),
    path("voucher/student/<uuid:pk>", VoucherStudentRetrieve.as_view()),


]