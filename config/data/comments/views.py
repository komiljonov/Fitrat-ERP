from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView

from .models import Comment
from .serializers import CommentSerializer
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

User = get_user_model()

class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.filter()
    serializer_class = CommentSerializer
    # permission_classes = (IsAuthenticated,)

class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class CommentLidRetrieveListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        id = self.kwargs.get('pk')
        if id:
            return Comment.objects.filter(Q(lid__id=id) | Q(student__id=id))
        return Comment.objects.none()

