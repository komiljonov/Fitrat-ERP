from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView

from .models import Comment
from .serializers import CommentSerializer
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

User = get_user_model()

class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

class CommentLidRetrieveListAPIView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,**kwargs):
        lid = Lid.objects.get(id=kwargs.get('pk'))
        if lid:
            return Comment.objects.filter(lid__id=lid).first()

class CommentStudentRetrieveListAPIView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self,**kwargs):
        student = Student.objects.get(id=kwargs.get('pk'))
        if student:
            return Comment.objects.filter(student__id=student).first()
