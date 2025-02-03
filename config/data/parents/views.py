from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.


from .serializers import RelativesSerializer
from .models import Relatives

class ParentListView(ListCreateAPIView):
    queryset = Relatives.objects.all()
    serializer_class = RelativesSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (SearchFilter, OrderingFilter,DjangoFilterBackend)

    search_fields = ('fathers_name','mothers_name','fathers_phone',)
    ordering_fields = ('fathers_name','mothers_name','fathers_phone','mothers_phone')
    filterset_fields = ('fathers_name','mothers_name','fathers_phone','mothers_phone')


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
