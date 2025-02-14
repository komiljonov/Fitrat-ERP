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
        creator = self.request.query_params.get('creator')
        if id:
            return Comment.objects.filter(Q(lid__id=id) | Q(student__id=id))

        if creator:
            return Comment.objects.filter((Q(lid__id=id) | Q(student__id=id)), creator__id=creator)
        return Comment.objects.none()

class CommentAppRead(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        id = self.kwargs.get('pk')
        creator = self.request.query_params.get('creator')
        if id:
            return Comment.objects.filter(Q(lid__id=id) | Q(student__id=id)).order_by('-created_at')

        if creator:
            return Comment.objects.filter((Q(lid__id=id) | Q(student__id=id)), creator__id=creator).order_by('-created_at')
        return Comment.objects.none()