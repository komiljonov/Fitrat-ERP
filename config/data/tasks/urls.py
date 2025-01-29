from ..tasks.views import TaskListCreateView, TaskRetrieveUpdateDestroyView, TaskListNoPGView, TaskStudentRetrieveListAPIView

from django.urls import path

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<uuid:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-retrieve-update'),
    path('no-pg/',TaskListNoPGView.as_view(), name='task-list-no-pg'),

    path('all/<uuid:pk>/', TaskStudentRetrieveListAPIView.as_view(), name='task-list-student'),
]
