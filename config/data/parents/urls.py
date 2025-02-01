from django.urls import path

from .views import ParentListView, ParentDetailView, ParentListNoPGView, StudentsParentListView

urlpatterns = [
    path('', ParentListView.as_view()),
    path('<uuid:pk>', ParentDetailView.as_view()),
    path('no-pg/', ParentListNoPGView.as_view()),
    path('student/<uuid:pk>', StudentsParentListView.as_view()),
]
