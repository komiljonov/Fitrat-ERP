from django.urls import path

from .views import StoresListView, StoreDetailView, StudentDetailView, FinanceListView, StrikeListView, \
    VersionUpdateView, StudentNotificationsView

urlpatterns = [
    path('story/',StoresListView.as_view()),
    path('story/<uuid:pk>',StoreDetailView.as_view()),

    # path('home/',StudentHomeView.as_view()),

    path("student/<uuid:user__id>",StudentDetailView.as_view()),

    path("finance/<uuid:pk>",FinanceListView.as_view()),

    path("strike/", StrikeListView.as_view()),

    path("versions/",VersionUpdateView.as_view()),

    path("notifications/",StudentNotificationsView.as_view()),
]