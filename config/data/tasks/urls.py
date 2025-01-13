from ..tasks.views import TaskListCreateView, TaskRetrieveUpdateDestroyView, TaskListNoPGView, \
    TaskLidRetrieveListAPIView, TaskStudentRetrieveListAPIView

from django.urls import path

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<uuid:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-retrieve-update'),
    path('no-pg/',TaskListNoPGView.as_view(), name='task-list-no-pg'),

    path('lid/<uuid:pk>/', TaskLidRetrieveListAPIView.as_view(), name='task-list-lid'),
    path('student/<uuid:pk>/', TaskStudentRetrieveListAPIView.as_view(), name='task-list-student'),
]
