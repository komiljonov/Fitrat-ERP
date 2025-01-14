from django.urls import path
from .views import StudentGroupsView, StudentRetrieveUpdateDestroyAPIView, StudentListAPIView, GroupStudentsListView, \
    StudentGroupListView, StudentGroupDetailView, StudentGroupListNoPG

urlpatterns = [
    path('', StudentGroupsView.as_view(), name='group-list'),
    path('<int:pk>/', StudentRetrieveUpdateDestroyAPIView.as_view(), name='group-detail'),
    path('no-pg/',StudentListAPIView.as_view(), name='no-pg-list'),

    path('<uuid:pk>/students/', GroupStudentsListView.as_view(), name='student-detail'),

    path('student/', StudentGroupListView.as_view(), name='student-group-list'),
    path('student/<int:pk>/', StudentGroupDetailView.as_view(), name='student-group-detail'),
    path('student/no-pg/', StudentGroupListNoPG.as_view(), name='student-no-pg'),

]