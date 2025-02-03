from django.urls import path

from .views import ParentListView, ParentDetailView,RelativesListNoPGView, StudentsRelativesListView

urlpatterns = [
    path('', ParentListView.as_view()),
    path('<uuid:pk>', ParentDetailView.as_view()),
    path('no-pg/', RelativesListNoPGView.as_view()),
    path('student/<uuid:pk>', StudentsRelativesListView.as_view()),
]
