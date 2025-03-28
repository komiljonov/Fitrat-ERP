from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from data.student.homeworks.models import Homework
from data.student.homeworks.serializers import HomeworkSerializer


# Create your views here.
class HomeworkListCreateView(ListCreateAPIView):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        theme = self.request.query_params.get('theme', None)
        queryset = Homework.objects.all()
        if theme:
            queryset = queryset.filter(theme__id__in=theme)
        return queryset


class HomeworkDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]

