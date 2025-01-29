from django.contrib.auth import get_user_model
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
        lid_id = self.kwargs.get('pk')
        student_id = self.kwargs.get('pk')
        if lid_id:
            return Comment.objects.filter(lid__id=lid_id)
        if student_id:
            return Comment.objects.filter(student__id=student_id)
        return Comment.objects.none()

