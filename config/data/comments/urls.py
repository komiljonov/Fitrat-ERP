
from django.urls import path
from .views import (CommentListCreateAPIView,
                    CommentRetrieveUpdateDestroyAPIView,
                    CommentLidRetrieveListAPIView)

urlpatterns = [
    path('', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path("<uuid:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-retrieve-update'),

    path('all/<uuid:pk>/', CommentLidRetrieveListAPIView.as_view(), name='comment-list-create'),
    # path('student/<uuid:pk>/', CommentStudentRetrieveListAPIView.as_view(), name='comment-list-create'),
]