from django.db.models import Q
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Relatives
from .serializers import RelativesSerializer


# Create your views here.

class ParentListView(ListCreateAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]



class ParentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]



class RelativesListNoPGView(ListAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class StudentsRelativesListView(ListAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        queryset = Relatives.objects.filter(Q(student__id=id) | Q(lid__id=id))
        return queryset
