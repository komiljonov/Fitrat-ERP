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
        try:
            lid = Lid.objects.get(id=lid_id)
        except Lid.DoesNotExist:
            raise Http404("Lid not found.")
        return Comment.objects.filter(lid=lid)


class CommentStudentRetrieveListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        student_id = self.kwargs.get('pk')
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise Http404("Student not found.")
        return Comment.objects.filter(student=student)
